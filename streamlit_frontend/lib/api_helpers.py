"""
API Helper functions for Streamlit frontend
"""

# Removed: os, requests, json, load_dotenv, get_api_url, get_auth_headers, make_api_request
# These will be imported from streamlit_frontend.lib.api or are not needed here if functions use api.py directly.

# Import necessary functions from the main api.py
from .api import make_api_request, API_BASE_URL # Assuming API_BASE_URL is exposed or use a getter if not.
                                              # For simplicity, assuming direct import or a helper in api.py to get it.

# If API_BASE_URL is not directly importable from api.py, is_api_healthy might need its own way to get it, 
# or api.py should provide a get_api_url() function.
# For now, assuming `from .api import API_BASE_URL` works or `is_api_healthy` will be adapted.
import requests # Keep requests for is_api_healthy if it remains independent.

def _safe_api_call(endpoint, method="GET", data=None):
    """Helper function to handle API calls with consistent return values"""
    if data is None:
        api_result = make_api_request(endpoint=endpoint, method=method)
    else:
        api_result = make_api_request(endpoint=endpoint, method=method, data=data)
    # Always return just the first two values (result, success)
    return api_result[0], api_result[1]

def is_api_healthy():
    """Check if the API is responding and returning proper responses"""
    try:
        # If API_BASE_URL is imported:
        api_url_for_health = API_BASE_URL 
        # If not, we might need a local definition or a getter from api.py
        # api_url_for_health = os.getenv('API_BASE_URL', 'http://localhost:8000/api') # Fallback if not imported
        
        response = requests.get(f"{api_url_for_health}/csrf-token", timeout=3) # csrf-token is a common Laravel check
        if response.status_code == 200:
            try:
                _ = response.json() # Verify it's valid JSON
                return True
            except ValueError:
                return False
        return False
    except:
        return False

def safe_get_users():
    """Get users with improved error handling, using the main api.py make_api_request"""
    # make_api_request from .api handles auth headers internally
    result, success = _safe_api_call(endpoint="admin/users", method="GET")
    
    if success:
        return result.get("data", []), True
    else:
        # Log error or handle as needed, result contains error info from make_api_request
        print(f"Error fetching users: {result.get('error')}")
        return [], False

def safe_get_organizers(status="pending"):
    """Get organizers with improved error handling, using the main api.py make_api_request"""
    endpoint = f"admin/organizers/{status}"
    result, success = _safe_api_call(endpoint=endpoint, method="GET")
    
    if success:
        # Both pending and approved now return data wrapped in "data" key
        return result.get("data", []), True
    else:
        print(f"Error fetching {status} organizers: {result.get('error')}")
        return [], False 