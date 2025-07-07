"""
Navigation utilities for the Resume Analyzer & Booth Recommendations app.
Provides consistent navigation across all pages.
"""

import streamlit as st
from .auth_client import get_user_display_name, get_user_role, logout

def display_sidebar_navigation():
    """
    Display the navigation sidebar for authenticated users.
    Uses the same structure across all pages for consistency.
    """
    st.sidebar.title("Navigation")
    
    # Get user info
    user_role = st.session_state.get("user_role", "user")
    user_name = get_user_display_name()
    
    # Display welcome message with username
    st.sidebar.markdown(f"**Welcome, {user_name}!**")
    st.sidebar.markdown("---")
    
    # Using st.page_link for cleaner navigation in MPAs
    # Ensure the paths are relative to the app's root directory where Streamlit is run.
    # If pages are in a 'pages' subdirectory, Streamlit handles this automatically.

    st.sidebar.page_link("app.py", label="App Home", icon="🏠")

    if user_role == "admin":
        st.sidebar.markdown("### Admin Menu")
        if st.sidebar.button("👑 Admin Dashboard", key="nav_admin_dashboard_main", use_container_width=True):
            st.switch_page("pages/admin_dashboard.py")
        if st.sidebar.button("👥 User Management", key="nav_user_management_main", use_container_width=True):
            st.switch_page("pages/admin_user_management.py")
        if st.sidebar.button("📄 Job Requirements", key="nav_job_req_main", use_container_width=True):
            st.switch_page("pages/admin_job_requirements.py")
        if st.sidebar.button("🏢 Job Fair Admin", key="nav_job_fair_admin_main", use_container_width=True):
            st.switch_page("pages/admin_job_fair_management.py")
            
    elif user_role == "organizer":
        st.sidebar.markdown("### Organizer Menu")
        st.sidebar.page_link("pages/05_Organizer_Job_Fairs.py", label="Job Fairs", icon="🏢")
        st.sidebar.page_link("pages/06_Organizer_Booth_Management.py", label="Booth Management", icon="🏪")
            
    else: # Job Seeker
        st.sidebar.markdown("### Job Seeker Menu")
        st.sidebar.page_link("pages/01_resume_upload.py", label="Resume Upload", icon="📤")
        st.sidebar.page_link("pages/02_my_resumes.py", label="My Resumes", icon="📋")
        st.sidebar.page_link("pages/02_resume_analysis.py", label="Resume Analysis", icon="🔍")
        st.sidebar.page_link("pages/08_Booth_Recommendations.py", label="Booth Recommendations", icon="🎯")
    
    # Profile and logout options for all users
    st.sidebar.markdown("---")
    
    st.sidebar.page_link("pages/05_profile.py", label="Profile", icon="👤")
    
    if st.sidebar.button("🚪 Logout", key="nav_logout_button"): # Changed to button for logout action
        logout_response, success = logout() # Assuming logout() is defined in auth_client and handles session clearance
        if success:
            st.session_state.authenticated = False
            st.session_state.user_token = None
            st.session_state.user_role = None
            st.session_state.clear() # Clear all session state for a clean logout
            st.switch_page("app.py") # Navigate to home/login page
        else:
            st.sidebar.error("Logout failed. Please try again.")
            # Optionally, still try to switch page or show error message
            st.switch_page("app.py")

# The old switch_page function is no longer needed if using st.page_link or direct st.switch_page
# def switch_page(page_name):
#     """
#     DEPRECATED: Switch to another page in the Streamlit app.
#     """
#     # Construct the full path if pages are in a 'pages' subdirectory
#     # Streamlit's st.switch_page handles this well.
#     # Example: page_name could be "01_resume_upload.py"
#     target_page_path = f"pages/{page_name}" if not page_name.startswith("pages/") and not page_name == "app.py" else page_name
#     try:
#         st.switch_page(target_page_path)
#     except Exception as e:
#         st.error(f"Error switching to page '{target_page_path}': {e}")
#         st.info(f"Ensure the page '{target_page_path}' exists.") 