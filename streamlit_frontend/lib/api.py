"""
API client for connecting to the Laravel backend
"""

import streamlit as st
import requests
import json
import os
import tempfile
import re
from dotenv import load_dotenv
import time
from typing import Dict, List, Tuple, Any, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# API configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")

# Global requests session object to persist cookies
api_session = requests.Session()

def get_auth_headers() -> Dict[str, str]:
    """
    Get authentication headers for API requests
    
    Returns:
        Dict containing authorization headers
    """
    if "user_token" not in st.session_state:
        return {"Accept": "application/json"}
    
    return {
        "Authorization": f"Bearer {st.session_state.user_token}",
        "Accept": "application/json"
    }

def make_api_request(
    endpoint: str, 
    method: str = "GET", 
    data: Dict = None, 
    files: Dict = None, 
    params: Dict = None,
    timeout: int = 30,
    use_cookie_auth: bool = False,
    return_status_code: bool = False 
) -> Tuple[Any, bool, Optional[int]]:
    """
    Make API request to the Laravel backend
    
    Args:
        endpoint: API endpoint (without the base URL)
        method: HTTP method (GET, POST, PUT, DELETE)
        data: Data to send in the request
        files: Files to upload
        params: URL parameters
        timeout: Request timeout in seconds
        use_cookie_auth: If True, rely on session cookies instead of Bearer token
        return_status_code: If True, also return the HTTP status code
        
    Returns:
        Tuple containing (response_data, success_boolean) or 
        (response_data, success_boolean, status_code_int) if return_status_code is True.
    """
    url = f"{API_BASE_URL}/{endpoint}"
    
    # ALWAYS reconstruct headers fresh for each request
    headers = {"Accept": "application/json"}
    if "user_token" in st.session_state and st.session_state.user_token:
        headers["Authorization"] = f"Bearer {st.session_state.user_token}"
    
    request_cookies = {}
    if use_cookie_auth:
        xsrf_token = api_session.cookies.get('XSRF-TOKEN')
        if xsrf_token:
            headers['X-XSRF-TOKEN'] = xsrf_token
        request_cookies = api_session.cookies.get_dict()

    try:
        logger.info(f"Attempting {method} request to {url} with headers: {list(headers.keys())} and params: {params}")
        
        if params is not None:
            sanitized_params = {}
            for key, value in params.items():
                if value is not None:
                    sanitized_params[str(key)] = str(value)
            params = sanitized_params
        
        # Always include withCredentials=True equivalent by using the session object
        # and explicitly passing its cookies if determined above.
        if method == "GET":
            response = api_session.get(url, headers=headers, params=params, timeout=timeout, cookies=request_cookies)
        elif method == "POST":
            if files:
                # For multipart/form-data, requests handles Content-Type. Remove it from headers if present.
                multipart_headers = {k: v for k, v in headers.items() if k.lower() != 'content-type'}
                response = api_session.post(url, headers=multipart_headers, data=data, files=files, timeout=timeout, cookies=request_cookies)
            else:
                response = api_session.post(url, headers=headers, json=data, timeout=timeout, cookies=request_cookies)
        elif method == "PUT":
            if files:
                multipart_headers = {k: v for k, v in headers.items() if k.lower() != 'content-type'}
                response = api_session.put(url, headers=multipart_headers, data=data, files=files, timeout=timeout, cookies=request_cookies)
            else:
                response = api_session.put(url, headers=headers, json=data, timeout=timeout, cookies=request_cookies)
        elif method == "DELETE":
            response = api_session.delete(url, headers=headers, timeout=timeout, cookies=request_cookies)
        else:
            return ({"error": f"Unsupported HTTP method: {method}"}, False, None) if return_status_code else ({"error": f"Unsupported HTTP method: {method}"}, False)
        
        status_code_to_return = response.status_code if return_status_code else None

        if response.status_code in [200, 201, 204]: # Added 204 for success
            try:
                # For 204 No Content, response.json() will fail.
                if response.status_code == 204:
                    json_response = {"data": "Success (No Content)", "status_code": 204}
                else:
                    json_response = response.json()
                
                return (json_response, True, status_code_to_return) if return_status_code else (json_response, True)
            except json.JSONDecodeError:
                # Handle cases where response is successful but not JSON (e.g. plain text or empty for 204)
                # For 204, this part might not be hit if handled above, but as a fallback.
                success_data = {"data": "Success", "status_code": response.status_code, "content": response.text if response.text else "No Content"}
                return (success_data, True, status_code_to_return) if return_status_code else (success_data, True)
                
        elif response.status_code == 401:
            error_data = {"error": "Authentication failed. Please log in again.", "details": response.text if response.text else "No details"}
            return (error_data, False, status_code_to_return) if return_status_code else (error_data, False)
            
        elif response.status_code == 403:
            error_data = {"error": "You don't have permission to access this resource.", "details": response.text if response.text else "No details"}
            return (error_data, False, status_code_to_return) if return_status_code else (error_data, False)
            
        elif response.status_code == 419: # CSRF token mismatch / session expired
            error_data = {"error": "Your session has expired or there was a security token mismatch. Please refresh and try again.", "status_code": 419, "details": response.text if response.text else "No details"}
            return (error_data, False, status_code_to_return) if return_status_code else (error_data, False)
            
        elif response.status_code == 422: # Validation errors
            validation_errors = response.json().get('errors', {})
            error_messages = []
            for field, messages in validation_errors.items():
                if isinstance(messages, list):
                    error_messages.extend([f"{field}: {msg}" for msg in messages])
                else:
                    error_messages.append(f"{field}: {messages}")
            
            error_data = {"error": "Validation failed.", "details": error_messages}
            return (error_data, False, status_code_to_return) if return_status_code else (error_data, False)
            
        else: # Other client/server errors
            try:
                error_data_json = response.json()
                error_message = error_data_json.get('message', f"Error {response.status_code}")
                error_data = {"error": error_message, "details": error_data_json}
            except json.JSONDecodeError:
                error_data = {"error": f"Error {response.status_code}: {response.text}"}
            return (error_data, False, status_code_to_return) if return_status_code else (error_data, False)
                
    except requests.exceptions.Timeout:
        error_data = {"error": "Request timed out. Please try again later."}
        return (error_data, False, None) if return_status_code else (error_data, False)
        
    except requests.exceptions.ConnectionError as e: # Added specific exception variable e
        logger.error(f"ConnectionError during API request to {url}: {e}", exc_info=True)
        error_data = {"error": "Could not connect to the server. Please check your internet connection."}
        return (error_data, False, None) if return_status_code else (error_data, False)
        
    except Exception as e:
        logger.error(f"Generic Exception during API request to {url}: {e}", exc_info=True) # Corrected f-string
        error_data = {"error": f"An unexpected error occurred: {str(e)}"}
        return (error_data, False, None) if return_status_code else (error_data, False)

# ==========================================
# User Authentication API
# ==========================================

def register_user(name: str, email: str, password: str, password_confirmation: str, role: str, company: Optional[str] = None) -> Tuple[Dict, bool]:
    """
    Register a new user (job_seeker or organizer_applicant)
    """
    data = {
        "name": name,
        "email": email,
        "password": password,
        "password_confirmation": password_confirmation,
        "user_type": role  # Changed key from "role" to "user_type"
    }
    # The 'role' parameter now contains either 'user' or 'organizer_applicant'
    if role == "organizer_applicant" and company:
        data["company_name"] = company # Changed key to "company_name"
    
    return make_api_request("register", "POST", data=data, use_cookie_auth=True)

def login_user(email: str, password: str) -> Tuple[Dict, bool]:
    """
    Log in a user. This function now targets /api/login.
    It first fetches a CSRF cookie from /sanctum/csrf-cookie,
    then attempts login by POSTing credentials with the XSRF-TOKEN header.
    """
    data = {"email": email, "password": password}
    
    csrf_url = f"{API_BASE_URL.replace('/api', '')}/sanctum/csrf-cookie"
    
    login_api_endpoint = "login"

    standard_headers = {"Accept": "application/json"}

    try:
        logger.info(f"Fetching CSRF cookie from: {csrf_url}")
        csrf_response = api_session.get(csrf_url, headers=standard_headers, timeout=10)
        logger.info(f"CSRF response status: {csrf_response.status_code}")
        logger.info(f"Cookies in api_session after CSRF call: {api_session.cookies.get_dict()}")

        xsrf_token = api_session.cookies.get('XSRF-TOKEN')
        
        if xsrf_token:
            login_headers = {**standard_headers, 'X-XSRF-TOKEN': xsrf_token}
        else:
            login_headers = standard_headers 

        login_post_url = f"{API_BASE_URL}/{login_api_endpoint}"
        
        logger.info(f"Attempting login to: {login_post_url}")
        response = api_session.post(login_post_url, headers=login_headers, json=data, timeout=30)
        logger.info(f"Login POST response status: {response.status_code}")
        logger.info(f"Cookies in api_session after login POST: {api_session.cookies.get_dict()}")
        
        if response.status_code in [200, 201]: 
            try:
                return response.json(), True 
            except json.JSONDecodeError:
                return {"message": "Login successful, but no JSON body."}, True
        elif response.status_code == 419:
             return {"error": "Login failed due to session issue (419). Please try again.", "details": response.text}, False
        elif response.status_code == 422:
            return {"error": "Validation failed.", "details": response.json().get('errors', {})}, False
        else:
            return {"error": f"Login failed with status {response.status_code}", "details": response.text}, False
            
    except requests.exceptions.RequestException as e:
        return {"error": f"Login connection error: {str(e)}"}, False

def logout_user() -> Tuple[Dict, bool]:
    """
    Log out a user. This will hit /api/logout.
    The Bearer token should be sent by make_api_request.
    If using cookie-based session for logout, make_api_request needs adjustment or direct call.
    Assuming /api/logout is protected by auth:sanctum and expects a Bearer token if it's an API client,
    or uses session if it's SPA.
    """
    return make_api_request("logout", "POST", use_cookie_auth=True)

def get_current_user() -> Tuple[Dict, bool]:
    """
    Fetch the currently authenticated user's profile
    """
    return make_api_request("user", "GET", use_cookie_auth=True)

def get_my_resumes_list() -> Tuple[List[Dict], bool]:
    """
    Get a list of the current user's resumes (for dropdowns etc.)
    Ensures cookie-based authentication is used.
    """
    return make_api_request("my-resumes-list", "GET", use_cookie_auth=True)

# ==========================================
# Resume API
# ==========================================

def get_user_resumes() -> Tuple[Dict, bool]:
    """
    Get a list of resumes for the current user.
    Tries cookie-based auth first, then falls back to Bearer token if cookie auth fails.
    """
    # Primary attempt: cookie-based authentication
    response_data, success = make_api_request("resumes", "GET", use_cookie_auth=True)

    # Fallback logic: if primary attempt failed with an authentication-like error, try with Bearer token
    if not success and ("Authentication failed" in str(response_data.get("error", "")) or "Unauthenticated" in str(response_data.get("error", ""))):
        logger.info("Cookie-based fetch for get_user_resumes failed. Attempting Bearer token authentication.")
        # Force make_api_request to use Bearer token by setting use_cookie_auth=False
        # This relies on "user_token" being in st.session_state if available
        return make_api_request("resumes", "GET", use_cookie_auth=False)
    
    return response_data, success

def upload_resume(file, description: str = None) -> Tuple[Dict, bool]: # description is not used by backend endpoint
    """
    Upload a resume file for enhanced parsing.
    Assumes cookie-based auth if no token.
    
    Args:
        file: File object (e.g., from st.file_uploader)
        description: Optional description (not currently used by the endpoint)
        
    Returns:
        Tuple containing (response_data, success_boolean)
    """
    if not file:
            return {"error": "No file provided"}, False
        
    files = {'resume': (file.name, file, file.type)}
    data = {}
    if description: # Though backend currently doesn't use it, keep for potential future use
        data["description"] = description
    
    # Determine if we should explicitly use cookie auth based on token presence
    use_cookies = "user_token" not in st.session_state
    return make_api_request("resumes", "POST", data=data, files=files, use_cookie_auth=use_cookies)

def get_resume(resume_id: int) -> Tuple[Dict, bool]:
    """
    Get a specific resume by ID
    
    Args:
        resume_id: ID of the resume to get
        
    Returns:
        Tuple containing (response_data, success_boolean)
    """
    return make_api_request(f"resumes/{resume_id}", "GET", use_cookie_auth=True)

def delete_resume(resume_id: int) -> Tuple[Dict, bool]:
    """
    Delete a resume by ID
    
    Args:
        resume_id: ID of the resume to delete
        
    Returns:
        Tuple containing (response_data, success_boolean)
    """
    return make_api_request(f"resumes/{resume_id}", "DELETE", use_cookie_auth=True)

def get_resume_analysis_with_fallback(resume_id: int) -> Tuple[Dict, bool]:
    """
    Get analysis for a specific resume, with fallback
    
    This function will first try the normal cookie-based authentication, and if that fails,
    it will fall back to trying explicit Bearer token authentication.
    
    Args:
        resume_id: ID of the resume
        
    Returns:
        Tuple containing (response_data, success_boolean)
    """
    # First try with cookie-based authentication
    response_data, success = make_api_request(f"resumes/{resume_id}/analysis", "GET", use_cookie_auth=True)
    
    # If that failed, explicitly check the error message
    if not success and 'Unauthenticated' in str(response_data):
        logger.info("Cookie authentication failed, trying with explicit Bearer token")
        # This forces the use of the Bearer token regardless of use_cookie_auth setting
        if "user_token" in st.session_state:
            headers = {"Accept": "application/json", "Authorization": f"Bearer {st.session_state.user_token}"}
            url = f"{API_BASE_URL}/resumes/{resume_id}/analysis"
            
            try:
                # Directly make a request with explicit headers
                response = api_session.get(url, headers=headers, timeout=30)
                
                if response.status_code in [200, 201]:
                    try:
                        return response.json(), True
                    except json.JSONDecodeError:
                        return {"data": "Success", "status_code": response.status_code, "content": response.text}, True
                else:
                    logger.error(f"Fallback request failed with status {response.status_code}")
                    return {"error": f"Both authentication methods failed. Status: {response.status_code}"}, False
            except Exception as e:
                logger.error(f"Error in fallback request: {str(e)}")
                return {"error": f"Error in fallback request: {str(e)}"}, False
        else:
            return {"error": "No authentication token available for fallback method"}, False
    
    # If the first try was successful or failed with a different error, return the original result
    return response_data, success

def get_resume_analysis(resume_id: int) -> Tuple[Dict, bool]:
    """
    Get analysis for a specific resume
    
    Args:
        resume_id: ID of the resume
        
    Returns:
        Tuple containing (response_data, success_boolean)
    """
    return make_api_request(f"resumes/{resume_id}/analysis", "GET", use_cookie_auth=True)

def get_job_recommendations(resume_id: int) -> Tuple[Dict, bool]:
    """
    Get job recommendations for a resume.
    This is a placeholder, actual implementation might vary.
    """
    # This endpoint might need to be specific, e.g., /resumes/{resume_id}/job-recommendations
    # Or it could be a more general one that takes resume_id as a parameter
    # For now, assuming a general endpoint that can be filtered by resume_id if needed
    # or a dedicated one for job recommendations based on resume.
    # Let's assume the backend has /job-recommendations?resume_id={resume_id}
    # return make_api_request(f"job-recommendations?resume_id={resume_id}", "GET")
    
    # Based on current Laravel setup, this would likely be:
    # GET /api/resumes/{resume_id}/recommendations/jobs
    # Or if it's not resume specific but rather based on user profile after resume analysis:
    # GET /api/job-recommendations (if user context implies the resume)
    
    # For now, let's assume a direct endpoint related to resume analysis results.
    # This part is illustrative as the actual recommendation logic/endpoint isn't defined yet.
    # Fallback to a generic placeholder if no clear recommendation endpoint exists.
    return make_api_request(f"resumes/{resume_id}/job-recommendations", "GET")

# ==========================================
# Job Fair API
# ==========================================

def get_all_job_fairs() -> Tuple[Dict, bool]:
    """
    Get all job fairs. This should ideally fetch from a public endpoint
    or an endpoint appropriate for the user's role.
    For now, using a generic '/job-fairs' which might be admin-only or public based on backend.
    Assuming it's public or the role is handled by the backend.
    """
    return make_api_request("public/job-fairs", "GET")

def get_job_fair_openings(job_fair_id: int) -> Tuple[Dict, bool]:
    """
    Get all job openings for a specific job fair for an authenticated user.
    Uses the endpoint: GET /api/job-fairs/{jobFairId}/openings
    This endpoint is expected to be protected by auth:sanctum.
    """
    # Allowing make_api_request to decide auth method (token first if available, then cookies)
    return make_api_request(f"job-fairs/{job_fair_id}/openings", "GET")

def get_job_fair_details(job_fair_id: int) -> Tuple[Dict, bool]:
    """
    Fetch details for a specific job fair.
    """
    return make_api_request(f"organizer/job-fairs/{job_fair_id}", "GET") # Assuming this is an organizer endpoint

def create_job_fair(data: Dict, map_file = None) -> Tuple[Dict, bool]:
    """
    Create a new job fair
    
    Args:
        data: Job fair data including name, description, location, dates, etc.
        map_file: Optional map image file
        
    Returns:
        Tuple containing (response_data, success_boolean)
    """
    files = None
    if map_file:
        files = {'map_image': (map_file.name, map_file, map_file.type)}
    return make_api_request("job-fairs", "POST", data=data, files=files, use_cookie_auth=True)

def update_job_fair(job_fair_id: int, data: Dict, map_file = None) -> Tuple[Dict, bool]:
    """
    Update an existing job fair
    
    Args:
        job_fair_id: ID of the job fair to update
        data: Job fair data to update
        map_file: Optional new map image file
        
    Returns:
        Tuple containing (response_data, success_boolean)
    """
    files = None
    if map_file:
        # Laravel often expects _method:PUT for form data, but here we use PUT directly
        # For file uploads with PUT, it's often simpler to use POST and a specific route or POST with _method=PUT
        # Assuming the API handles PUT with multipart/form-data correctly if files are present
        files = {'map_image': (map_file.name, map_file, map_file.type)}
    
    # If sending files with PUT, data needs to be form data, not json.
    # The make_api_request handles this by not sending json=data if files are present.
    return make_api_request(f"job-fairs/{job_fair_id}", "PUT", data=data, files=files, use_cookie_auth=True)

def delete_job_fair(job_fair_id: int) -> Tuple[Dict, bool]:
    """
    Delete a job fair
    
    Args:
        job_fair_id: ID of the job fair to delete
        
    Returns:
        Tuple containing (response_data, success_boolean)
    """
    return make_api_request(f"job-fairs/{job_fair_id}", "DELETE", use_cookie_auth=True)

# ==========================================
# Booth API
# ==========================================

def get_booths(job_fair_id: int = None) -> Tuple[Dict, bool]:
    """
    Get all booths, optionally filtered by job fair
    
    Args:
        job_fair_id: Optional ID of job fair to filter booths
        
    Returns:
        Tuple containing (response_data, success_boolean)
    """
    endpoint = "booths"
    params = None
    if job_fair_id:
        params = {"job_fair_id": job_fair_id}
    return make_api_request(endpoint, "GET", params=params, use_cookie_auth=True) # Assuming might need auth

def get_booth(booth_id: int) -> Tuple[Dict, bool]:
    """
    Get a specific booth
    
    Args:
        booth_id: ID of the booth to get
        
    Returns:
        Tuple containing (response_data, success_boolean)
    """
    return make_api_request(f"booths/{booth_id}", "GET", use_cookie_auth=True) # Assuming might need auth

def create_booth(data: Dict) -> Tuple[Dict, bool]:
    """
    Create a new booth
    
    Args:
        data: Booth data including job_fair_id, company_name, booth_number, etc.
        
    Returns:
        Tuple containing (response_data, success_boolean)
    """
    return make_api_request("booths", "POST", data=data, use_cookie_auth=True)

def update_booth(booth_id: int, data: Dict) -> Tuple[Dict, bool]:
    """
    Update an existing booth
    
    Args:
        booth_id: ID of the booth to update
        data: Booth data to update
        
    Returns:
        Tuple containing (response_data, success_boolean)
    """
    return make_api_request(f"booths/{booth_id}", "PUT", data=data, use_cookie_auth=True)

def delete_booth(booth_id: int) -> Tuple[Dict, bool]:
    """
    Delete a booth
    
    Args:
        booth_id: ID of the booth to delete
        
    Returns:
        Tuple containing (response_data, success_boolean)
    """
    return make_api_request(f"organizer/booths/{booth_id}", "DELETE")

def get_job_fair_booths(job_fair_id: int) -> Tuple[Dict, bool]:
    """
    Get all booths for a specific job fair
    
    Args:
        job_fair_id: ID of the job fair
        
    Returns:
        Tuple containing (response_data, success_boolean)
    """
    return make_api_request(f"job-fairs/{job_fair_id}/booths", "GET", use_cookie_auth=True) # Assuming might need auth

def get_booth_match_score(resume_id: int, booth_id: int) -> Tuple[Dict, bool]:
    """
    Calculate match score between a resume and a booth
    
    Args:
        resume_id: ID of the resume
        booth_id: ID of the booth
        
    Returns:
        Tuple containing (response_data, success_boolean)
    """
    return make_api_request(f"resumes/{resume_id}/booths/{booth_id}/match-score", "GET", use_cookie_auth=True)

# ==========================================
# Admin API
# ==========================================

def get_pending_organizers() -> Tuple[Dict, bool]:
    """
    Get all pending organizer applications (admin only)
    
    Returns:
        Tuple containing (response_data, success_boolean)
    """
    return make_api_request("admin/organizers/pending", "GET", use_cookie_auth=True)

def get_approved_organizers() -> Tuple[Dict, bool]:
    """
    Get all approved organizers (admin only)
    
    Returns:
        Tuple containing (response_data, success_boolean)
    """
    return make_api_request("admin/organizers/approved", "GET", use_cookie_auth=True)

def approve_organizer(organizer_id: int) -> Tuple[Dict, bool]:
    """
    Approve an organizer application (admin only)
    
    Args:
        organizer_id: ID of the organizer to approve
        
    Returns:
        Tuple containing (response_data, success_boolean)
    """
    return make_api_request(f"admin/organizers/{organizer_id}/approve", "POST", use_cookie_auth=True)

def reject_organizer(organizer_id: int) -> Tuple[Dict, bool]:
    """
    Reject an organizer application (admin only)
    
    Args:
        organizer_id: ID of the organizer to reject
        
    Returns:
        Tuple containing (response_data, success_boolean)
    """
    return make_api_request(f"admin/organizers/{organizer_id}/reject", "POST", use_cookie_auth=True)

# ==========================================
# Utility Functions
# ==========================================

def get_job_fair(job_fair_id: int) -> Tuple[Dict, bool]:
    """
    Get details for a specific job fair (alias for get_job_fair_details)
    
    Args:
        job_fair_id: ID of the job fair to get
        
    Returns:
        Tuple containing (response_data, success_boolean)
    """
    return get_job_fair_details(job_fair_id) # Uses use_cookie_auth=True from the aliased function

def is_api_healthy() -> bool:
    """
    Check if the API is healthy and available
    
    Returns:
        Boolean indicating API health status
    """
    try:
        response = requests.get(f"{API_BASE_URL}/health-check", timeout=5)
        return response.status_code == 200
    except:
        return False

def upload_resume_bypass_validation(file, description: str = None) -> Tuple[Dict, bool]:
    """
    Upload a resume bypassing normal validation by sending a direct file without complex metadata.
    This is a fallback for when normal upload fails with strtolower() errors.
    
    Args:
        file: Resume file to upload
        description: Optional description of the resume
        
    Returns:
        Tuple containing (response_data, success_boolean)
    """
    if not file:
            return {"error": "No file provided"}, False
        
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.name}") as tmp_file:
            tmp_file.write(file.getvalue()) # Getvalue if it's an in-memory file like BytesIO
            temp_path = tmp_file.name
        
        # files_data = {} # This line seems unused, can be removed or kept if intended for future use.
        # Open the temporary file for upload
        with open(temp_path, 'rb') as f:
            # Simplify the file upload structure to avoid any complex metadata issues
            form_data = {}
            if description is not None:
                form_data["description"] = str(description)
            
            # Get auth headers but remove Content-Type to let the multipart form set it
            url = f"{API_BASE_URL}/resumes" # Standard upload endpoint
            
            # Determine if we should explicitly use cookie auth based on token presence
            use_cookies_for_upload = "user_token" not in st.session_state
            
            current_headers = {"Accept": "application/json"}
            current_cookies = {}

            if not use_cookies_for_upload and "user_token" in st.session_state:
                 current_headers["Authorization"] = f"Bearer {st.session_state.user_token}"
            elif use_cookies_for_upload:
                xsrf_token = api_session.cookies.get('XSRF-TOKEN')
                if xsrf_token:
                    current_headers['X-XSRF-TOKEN'] = xsrf_token
                current_cookies = api_session.cookies.get_dict()
            
            multipart_headers = {k: v for k, v in current_headers.items() if k.lower() != 'content-type'}
                
            # Super simplified file implementation - using files dict directly
            files_for_upload = {"resume": (os.path.basename(temp_path), f, file.type if hasattr(file, 'type') else 'application/octet-stream')}

            response = api_session.post(
                        url, 
                        headers=multipart_headers, 
                data=form_data if form_data else None, # Ensure data is None if empty, not {}
                files=files_for_upload, 
                timeout=60, # Increased timeout for uploads
                cookies=current_cookies
            )

            if response.status_code in [200, 201]:
                return response.json(), True
            else:
                return {"error": f"Upload failed with status {response.status_code}", "details": response.text}, False
    
    except Exception as e:
        return {"error": f"Error during file preparation or upload: {str(e)}"}, False
    finally:
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.unlink(temp_path)

def get_detailed_analysis(resume_id: int) -> Tuple[Dict, bool]:
    """
    Fetches the detailed analysis data including job and booth recommendations.
    This endpoint requires authentication.
    
    Args:
        resume_id: ID of the resume
        
    Returns:
        Tuple containing (response_data, success_boolean)
    """
    return make_api_request(f"resumes/{resume_id}/detailed-analysis", "GET", use_cookie_auth=True)

def process_reference_resumes() -> Tuple[Dict, bool]:
    """
    Process reference resumes for the three main categories (Computer Science, Medical, Finance)
    This is a development/admin utility function, likely requires admin privileges / cookie auth
    
    Returns:
        Tuple containing (response_data, success_boolean)
    """
    return make_api_request("dev/process-reference-resumes", "GET", use_cookie_auth=True) 

def debug_resume_analysis(resume_id: int) -> Tuple[Dict, bool]:
    """
    Debug authentication for resume analysis
    
    Args:
        resume_id: ID of the resume
        
    Returns:
        Tuple containing (response_data, success_boolean)
    """
    return make_api_request(f"debug-resume-analysis/{resume_id}", "GET", use_cookie_auth=True) 

def get_public_job_fair_booths_list(job_fair_id: int) -> Tuple[List[Dict], bool]:
    """
    Fetch a public list of booths for a given job fair.
    """
    return make_api_request(f"job-fairs/{job_fair_id}/booths-list", "GET") 

def get_personalized_booth_recommendations(resume_id: int, job_fair_id: int) -> Tuple[Dict, bool]:
    """
    Get personalized booth recommendations for a specific resume and job fair.
    Uses the endpoint: GET /api/resumes/{resume_id}/job-fairs/{job_fair_id}/personalized-booth-recommendations
    This endpoint is protected by auth:sanctum.
    """
    return make_api_request(f"resumes/{resume_id}/job-fairs/{job_fair_id}/personalized-booth-recommendations", "GET", use_cookie_auth=False) 

# New function for getting directions
def get_directions_to_job_fair(job_fair_id: int, user_lat: float, user_lon: float, mode: str) -> Tuple[Optional[Dict[str, Any]], bool]:
    """
    Get directions to a job fair from user's location using Geoapify via backend.
    Args:
        job_fair_id: The ID of the job fair.
        user_lat: User's current latitude.
        user_lon: User's current longitude.
        mode: Travel mode (e.g., 'drive', 'walk').
    Returns:
        Tuple containing (response_data, success_boolean).
    """
    endpoint = f"public/job-fairs/{job_fair_id}/directions"
    params = {
        'user_lat': user_lat,
        'user_lon': user_lon,
        'mode': mode
    }
    # This is a public endpoint, so no specific auth headers needed beyond what make_api_request handles by default (e.g. session for CSRF if applicable)
    return make_api_request(endpoint, "GET", params=params) 

def update_user_profile(profile_data: dict) -> Tuple[dict, bool]:
    """
    Update the authenticated user's profile (and password if provided)
    """
    return make_api_request("user", "PUT", data=profile_data, use_cookie_auth=True)

def upload_profile_photo(photo_file) -> Tuple[dict, bool]:
    """
    Upload the user's profile photo.
    """
    files = {'profile_photo': (photo_file.name, photo_file.getvalue(), photo_file.type)}
    return make_api_request("user/photo", "POST", files=files)

def delete_own_account() -> Tuple[dict, bool]:
    """
    Delete the authenticated user's own account
    """
    return make_api_request("user", "DELETE", use_cookie_auth=True) 