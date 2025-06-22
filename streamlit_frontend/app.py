"""
Resume Analyzer & Booth Recommendations - Main Application

This is the main entry point for the Streamlit application.
It handles authentication, theme settings, and renders the appropriate
dashboard based on the user's role.
"""

import streamlit as st
from streamlit.components.v1 import html
import os
import json
from datetime import datetime, timedelta
import time

# Page configuration - MUST BE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Resume Analyzer & Booth Recommendations",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import local modules after st.set_page_config
from lib import api
from lib.auth_client import init_session, check_auth, get_current_user, get_user_role
from lib.auth_client import is_admin, is_organizer, is_job_seeker, logout
from lib.css.ui import load_css
from lib.ui import display_landing_page, display_login_page, display_register_page, display_home_page, display_navbar

# Load CSS
load_css()

# Initialize session state
def init_app():
    """Initialize all session state variables"""
    # Initialize authentication
    init_session()
    
    # Initialize app state
    if 'view' not in st.session_state:
        st.session_state.view = 'landing'
        
    if 'last_page_reload' not in st.session_state:
        st.session_state.last_page_reload = time.time()
        
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
        
    if 'notifications' not in st.session_state:
        st.session_state.notifications = []
        
    if 'active_resume_id' not in st.session_state:
        st.session_state.active_resume_id = None
        
    if 'active_job_fair_id' not in st.session_state:
        st.session_state.active_job_fair_id = None
        
    if 'active_booth_id' not in st.session_state:
        st.session_state.active_booth_id = None

# Add notification to session state
def add_notification(type, message, duration=5):
    """
    Add a notification to the session state with an expiration time
    
    Args:
        type (str): Type of notification (success, info, warning, error)
        message (str): Message to display
        duration (int): Duration in seconds before the notification expires
    """
    expire_time = datetime.now() + timedelta(seconds=duration)
    st.session_state.notifications.append({
        'type': type,
        'message': message,
        'expire': expire_time
    })

# Render notifications
def render_notifications():
    """Render all active notifications and remove expired ones"""
    # Check for expired notifications and remove them
    now = datetime.now()
    if 'notifications' in st.session_state:
        st.session_state.notifications = [
            n for n in st.session_state.notifications 
            if n['expire'] > now
        ]
    
    # Display remaining notifications
    for note in st.session_state.notifications:
        if note['type'] == 'success':
            st.success(note['message'])
        elif note['type'] == 'info':
            st.info(note['message'])
        elif note['type'] == 'warning':
            st.warning(note['message'])
        elif note['type'] == 'error':
            st.error(note['message'])

# Main app function
def main():
    """Main application entry point"""
    # Initialize the app
    init_app()
    
    # Render notifications
    render_notifications()
    
    # Get current view from session state
    current_view = st.session_state.get('view', 'landing')
    
    # Handle authentication status and view routing
    if check_auth():
        # User is authenticated
        user_info = get_current_user()
        user_role = get_user_role()
        
        # Display navigation sidebar for authenticated users
        display_navbar()
        
        # If view is explicitly set to 'home', display home page
        # This ensures proper display after login
        if current_view == 'home':
            display_home_page()
        else:
            # For any other view, still display home page by default when authenticated
            # This ensures proper loading after login
            display_home_page()
    else:
        # User is not authenticated, show appropriate page
        if current_view == 'login':
            display_login_page()
        elif current_view == 'register':
            display_register_page()
        else:
            # Default to landing page
            display_landing_page()

if __name__ == "__main__":
    main() 