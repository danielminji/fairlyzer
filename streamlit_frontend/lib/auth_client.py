"""
Authentication client for the Resume Analyzer application.
Manages user authentication and session state.
"""

import streamlit as st
import requests
import os
from dotenv import load_dotenv
import time
import json
from streamlit.components.v1 import html
from typing import Dict, Tuple, Optional, List
import logging
import functools
from . import api

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")

# Define user roles
USER_ROLES = {
    'admin': 'Admin',
    'user': 'Job Seeker',
    'organizer': 'Organizer'
}

def execute_js(js_code):
    """Execute JavaScript code safely using the Streamlit HTML component"""
    html(js_code)

def init_session():
    """
    Initialize session state variables for authentication
    """
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if 'user_token' not in st.session_state:
        st.session_state.user_token = None
        
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
        
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None

def get_csrf_token():
    """Get a CSRF token from Laravel backend"""
    try:
        response = requests.get(f"{API_BASE_URL}/csrf-token")
        if response.status_code == 200:
            token = response.json().get('token')
            st.session_state.csrf_token = token
            st.session_state.cookies = response.cookies.get_dict()
            return token
        return None
    except Exception as e:
        print(f"Error getting CSRF token: {str(e)}")
        return None

def register(name: str, email: str, password: str, password_confirmation: str) -> Tuple[bool, str]:
    """
    Register a new user
    
    Args:
        name: User's name
        email: User's email
        password: User's password
        password_confirmation: Password confirmation
        
    Returns:
        Tuple of (success, message)
    """
    if not name or not email or not password or not password_confirmation:
        return False, "All fields are required"
    
    if password != password_confirmation:
        return False, "Passwords do not match"
    
    try:
        # Call the register API
        response, success = api.register_user(name, email, password, password_confirmation)
        
        if not success:
            error_msg = response.get('error', 'Registration failed')
            if isinstance(error_msg, dict) and 'details' in error_msg:
                error_msg = "\n".join(error_msg['details'])
            logger.warning(f"Registration failed: {error_msg}")
            return False, error_msg
        
        logger.info(f"User registered successfully: {email}")
        return True, "Registration successful. Please log in."
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return False, f"An error occurred during registration: {str(e)}"

def register_organizer(name: str, email: str, password: str, password_confirmation: str, company: str) -> Tuple[bool, str]:
    """
    Register a new organizer
    
    Args:
        name: Organizer's name
        email: Organizer's email
        password: Organizer's password
        password_confirmation: Password confirmation
        company: Company name
        
    Returns:
        Tuple of (success, message)
    """
    if not name or not email or not password or not password_confirmation or not company:
        return False, "All fields are required"
    
    if password != password_confirmation:
        return False, "Passwords do not match"
    
    try:
        # Call the register organizer API
        response, success = api.register_organizer(name, email, password, password_confirmation, company)
        
        if not success:
            error_msg = response.get('error', 'Registration failed')
            if isinstance(error_msg, dict) and 'details' in error_msg:
                error_msg = "\n".join(error_msg['details'])
            logger.warning(f"Organizer registration failed: {error_msg}")
            return False, error_msg
        
        logger.info(f"Organizer registered successfully: {email}")
        return True, "Registration submitted for approval. You will be notified once your account is approved."
        
    except Exception as e:
        logger.error(f"Organizer registration error: {str(e)}")
        return False, f"An error occurred during registration: {str(e)}"

def login(email: str, password: str) -> Tuple[bool, str]:
    """
    Log in a user with email and password
    
    Args:
        email: User's email
        password: User's password
        
    Returns:
        Tuple of (success, message_or_data)
    """
    if not email or not password:
        return False, "Email and password are required"
    
    try:
        # Call the login API
        response, success = api.login_user(email, password)
        
        if not success:
            error_msg = response.get('error', 'Login failed')
            logger.warning(f"Login failed: {error_msg}")
            return False, error_msg
        
        # Extract token from response
        token = response.get('token', None)
        user_data = response.get('user', {})
        
        if not token or not user_data:
            logger.warning("Login successful but missing token or user data")
            return False, "Authentication error: missing token or user data"
        
        # Store authentication info in session state
        st.session_state.authenticated = True
        st.session_state.user_token = token
        st.session_state.user_info = user_data
        st.session_state.user_role = user_data.get('role', 'user')
        
        logger.info(f"User logged in successfully: {user_data.get('email')}")
        return True, user_data
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return False, f"An error occurred during login: {str(e)}"

def logout():
    """
    Log out the current user and clear session state
    
    Returns:
        Tuple of (success, message)
    """
    try:
        # Call the logout API if user is authenticated
        if st.session_state.authenticated and st.session_state.user_token:
            api.logout_user()
        
        # Clear session state
        st.session_state.authenticated = False
        st.session_state.user_token = None
        st.session_state.user_info = None
        st.session_state.user_role = None
        
        return True, "Logged out successfully"
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        # Still clear session state even if API call fails
        st.session_state.authenticated = False
        st.session_state.user_token = None
        st.session_state.user_info = None
        st.session_state.user_role = None
        
        return False, f"Error during logout: {str(e)}"

def check_auth() -> bool:
    """
    Check if user is authenticated
    
    Returns:
        Boolean indicating if user is authenticated
    """
    # First check if authenticated flag is set in session state
    if not st.session_state.get('authenticated', False):
        return False
    
    # Check if we have user info already
    if st.session_state.get('user_info') is None:
        # If no user info but authenticated flag is set, try to get user info
        if st.session_state.get('user_token') is not None:
            # Verify token validity by making an API call
            response, success = api.get_current_user()
            
            if not success:
                # Token is invalid, clear session state
                st.session_state.authenticated = False
                st.session_state.user_token = None
                st.session_state.user_info = None
                st.session_state.user_role = None
                return False
            
            # Update user info in session state
            st.session_state.user_info = response
            st.session_state.user_role = response.get('role', 'user')
            return True
        else:
            # No token, so not authenticated
            st.session_state.authenticated = False
            return False
    
    # We have both the authenticated flag and user info
    return True

def get_current_user() -> Optional[Dict]:
    """
    Get current user information
    
    Returns:
        User information dictionary or None if not authenticated
    """
    if not st.session_state.authenticated:
        return None
    
    return st.session_state.user_info

def get_user_role() -> Optional[str]:
    """
    Get current user role
    
    Returns:
        User role string or None if not authenticated
    """
    if not st.session_state.authenticated:
        return None
    
    return st.session_state.user_role

def is_admin() -> bool:
    """
    Check if current user is an admin
    
    Returns:
        Boolean indicating if user is an admin
    """
    return st.session_state.authenticated and st.session_state.user_role == 'admin'

def is_organizer() -> bool:
    """
    Check if current user is an organizer
    
    Returns:
        Boolean indicating if user is an organizer
    """
    return st.session_state.authenticated and st.session_state.user_role == 'organizer'

def is_job_seeker() -> bool:
    """
    Check if current user is a job seeker (regular user)
    
    Returns:
        Boolean indicating if user is a job seeker
    """
    return st.session_state.authenticated and st.session_state.user_role == 'user'

def require_auth(roles: Optional[List[str]] = None):
    """
    Decorator to protect Streamlit pages, ensuring the user is authenticated.
    Optionally checks if the user has one of the specified roles.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Initialize session if needed (basic check)
            if 'authenticated' not in st.session_state:
                st.session_state.authenticated = False
            
            # Check if user is authenticated based on session state
            if not st.session_state.get('authenticated', False):
                st.error("You must be logged in to view this page.")
                if st.button("Go to Login"):
                    st.session_state.view = "login"
                    if 'current_page_for_redirect' in st.session_state: # Store current page to redirect back after login
                        del st.session_state['current_page_for_redirect'] # Clean up if already exists
                    st.switch_page("app.py") # Assuming app.py handles the main view routing
                st.stop()
            
            # Role-based access control
            if roles:
                user_role = get_user_role()
                if user_role not in roles:
                    st.error(f"You do not have permission to view this page. Required role: {roles}")
                    if st.button("Go to Home"):
                        st.switch_page("app.py")
                st.stop()
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def get_user_display_name() -> str:
    """
    Get user's display name or email
    
    Returns:
        User's name or email
    """
    if not st.session_state.authenticated or not st.session_state.user_info:
        return "Guest"
    
    user_info = st.session_state.user_info
    return user_info.get('name', user_info.get('email', 'User'))

def add_auth_persistence_js():
    """
    Add JavaScript to the page to persist authentication between page refreshes
    This helps maintain the user's logged-in state across multiple pages.
    """
    auth_js = """
    <script>
        // Store authentication data in localStorage
        if ((localStorage.getItem('authenticated') !== 'true') && 
            window.streamlitApp && 
            window.streamlitApp.isAuthenticated) {
            localStorage.setItem('authenticated', 'true');
            localStorage.setItem('lastActive', new Date().getTime());
        }
        
        // Check every 5 seconds if the session is still valid
        setInterval(function() {
            if (localStorage.getItem('authenticated') === 'true') {
                localStorage.setItem('lastActive', new Date().getTime());
            }
        }, 5000);
        
        // Make auth data available to the Streamlit app
        window.getAuthData = function() {
            return {
                authenticated: localStorage.getItem('authenticated') === 'true',
                userToken: localStorage.getItem('userToken'),
                lastActive: localStorage.getItem('lastActive')
            };
        };
    </script>
    """
    
    # Use the html component to inject the JavaScript
    from streamlit.components.v1 import html
    html(auth_js) 