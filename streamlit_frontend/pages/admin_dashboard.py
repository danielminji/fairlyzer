import streamlit as st
import pandas as pd
import json
import os
import sys
from datetime import datetime, timedelta

# Add lib directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))

from lib.api import make_api_request  # Direct import from api.py for 3-value return
from lib.api_helpers import safe_get_users, safe_get_organizers, is_api_healthy
from lib.ui_components import load_css, render_header, render_status_indicator, handle_api_error
from lib.navigation import display_sidebar_navigation

# Page config
st.set_page_config(
    page_title="Admin Dashboard",
    page_icon="👑",
    layout="wide"
)

# Load CSS
load_css()

st.markdown(
    """
    <style>
    [data-testid='stSidebarNav'] { display: none !important; }
    [data-testid='stSidebarSearch'] { display: none !important; }
    [data-testid='stSidebarHeader'] { display: none !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# Check authentication - use main app authentication
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Please log in first.")
    st.info("Click the button below to go to the login page.")
    if st.button("Go to Login"):
        st.switch_page("app.py")
    st.stop()

# Check admin permissions
if st.session_state.user_role != "admin":
    st.error("You don't have permission to access this page. Admin access required.")
    st.info("Please log in with an admin account.")
    if st.button("Go to Home"):
        st.switch_page("app.py")
    st.stop()

# --- Admin Authenticated Content ---
display_sidebar_navigation()

st.title("Admin Dashboard")
st.caption("Comprehensive system administration")

# --- Helper Functions ---
def get_user_statistics():
    """Get user statistics from API"""
    result, success = make_api_request("admin/users/statistics", "GET")
    if success:
        return result.get('data', {})
    return {}

def get_job_fair_statistics():
    """Get job fair statistics from API"""
    result, success = make_api_request("admin/job-fairs/statistics", "GET")
    if success:
        return result.get('data', {})
    return {}

def get_all_users():
    """Get all users from API"""
    users, success = safe_get_users()
    return users if success else []

def get_all_job_fairs():
    """Get all job fairs from API"""
    result, success = make_api_request("admin/job-fairs", "GET")
    if success:
        return result.get('data', [])
    return []

def get_all_job_requirements():
    """Get all job requirements from API"""
    result, success = make_api_request("admin/job-requirements", "GET", params={'per_page': 'all'})
    if success:
        if isinstance(result, dict) and 'data' in result:
            return result['data']
        elif isinstance(result, list):
            return result
        return []
    return []

def update_user_role(user_id, new_role):
    """Update a user's role"""
    data = {"role": new_role}
    result, success = make_api_request(f"admin/users/{user_id}/role", "PUT", data)
    return success, result

def toggle_user_status(user_id, is_active):
    """Activate or deactivate a user"""
    data = {"is_active": is_active}
    result, success = make_api_request(f"admin/users/{user_id}/status", "PUT", data)
    return success, result

def approve_organizer(user_id):
    """Approve an organizer"""
    result, success = make_api_request(f"admin/organizers/{user_id}/approve", "POST")
    return success, result

# --- Dashboard Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview", 
    "👥 User Management", 
    "📄 Job Requirements", 
    "🏢 Job Fair Management", 
    "⚙️ System Settings"
])

# --- Overview Tab ---
with tab1:
    st.header("System Overview")
    
    # System Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    user_stats = get_user_statistics()
    job_fair_stats = get_job_fair_statistics()
    
    with col1:
        st.metric(
            label="Total Users",
            value=user_stats.get('total_users', 0),
            delta=f"+{user_stats.get('recent_registrations', 0)} this week"
        )
    
    with col2:
        st.metric(
            label="Active Job Fairs",
            value=job_fair_stats.get('active_job_fairs', 0),
            delta=f"{job_fair_stats.get('upcoming_job_fairs', 0)} upcoming"
        )
    
    with col3:
        st.metric(
            label="Pending Organizers",
            value=user_stats.get('pending_organizers', 0)
        )
    
    with col4:
        st.metric(
            label="Total Booths",
            value=job_fair_stats.get('total_booths', 0)
        )
    
    # Quick Actions
    st.subheader("Quick Actions")
    col1, col3 = st.columns(2)
    
    with col1:
        if st.button("🔍 View Pending Organizers", use_container_width=True, key="quick_action_pending_organizers"):
            st.query_params.view = "pending_organizers"
            st.switch_page("pages/admin_user_management.py")
    
    with col3:
        if st.button("👥 User Management Page", use_container_width=True, key="quick_action_user_management"):
            st.switch_page("pages/admin_user_management.py")

# --- User Management Tab ---
with tab2:
    st.header("User Management")
    
    # Quick navigation to dedicated user management page
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 Full User Management", use_container_width=True):
            st.switch_page("pages/admin_user_management.py")
    
    with col2:
        if st.button("🔄 Refresh Data", use_container_width=True, key="refresh_user_management_dashboard_tab"):
            st.rerun()
    
    # User statistics overview
    user_stats = get_user_statistics()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", user_stats.get('total_users', 0))
    with col2:
        st.metric("Admins", user_stats.get('admins', 0))
    with col3:
        st.metric("Organizers", user_stats.get('organizers', 0))
    with col4:
        st.metric("Job Seekers", user_stats.get('job_seekers', 0))
    
    # Quick user management actions
    user_tab1, user_tab2, user_tab3 = st.tabs(["All Users", "Pending Organizers", "User Actions"])
    
    with user_tab1:
        st.subheader("Recent Users")
        users = get_all_users()[:10]  # Show only first 10
        
        if users:
            for user in users:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{user.get('name', 'Unknown')}** ({user.get('email', 'No email')})")
                with col2:
                    role_options = ["user", "organizer", "admin"]
                    current_role = user.get('role', 'user')
                    role_index = role_options.index(current_role) if current_role in role_options else 0
                    new_role = st.selectbox(
                        "Role", 
                        options=role_options,
                        index=role_index,
                        key=f"role_{user.get('id')}"
                    )
                with col3:
                    if new_role != current_role:
                        if st.button("Update", key=f"update_{user.get('id')}"):
                            success, result = update_user_role(user.get('id'), new_role)
                            if success:
                                st.success("Role updated!")
                                st.rerun()
                            else:
                                st.error("Failed to update role")
        else:
            st.info("No users found")
    
    with user_tab2:
        st.subheader("Pending Organizer Approvals")
        
        pending_organizers, success = safe_get_organizers("pending")
        if success and pending_organizers:
            for organizer in pending_organizers:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{organizer.get('name', 'Unknown')}**")
                    st.caption(organizer.get('email', 'No email'))
                with col2:
                    if st.button("✅ Approve", key=f"approve_{organizer.get('id')}"):
                        success, result = approve_organizer(organizer.get('id'))
                        if success:
                            st.success("Organizer approved!")
                            st.rerun()
                        else:
                            st.error("Failed to approve organizer")
                with col3:
                    if st.button("❌ Reject", key=f"reject_{organizer.get('id')}"):
                        # Implement reject functionality
                        st.info("Reject functionality - redirect to user management")
        else:
            st.info("No pending organizer approvals")
    
    with user_tab3:
        st.subheader("Quick Actions")
        if st.button("Create New User", use_container_width=True, key="admin_dash_create_user_btn"):
            # Navigate to the main user management page. Actual creation form would be there.
            st.switch_page("pages/admin_user_management.py") 
            # Optionally, set a query param if admin_user_management.py can open a create form directly
            # st.query_params.action = "create_user"
        if st.button("Export User Data", use_container_width=True, key="admin_dash_export_user_btn"):
            st.info("Export functionality - to be implemented")

# --- Job Requirements Tab ---
with tab3:
    st.header("Job Requirements Management")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 Manage Job Requirements", use_container_width=True):
            st.switch_page("pages/admin_job_requirements.py")
    
    with col2:
        if st.button("🔄 Refresh Data", use_container_width=True, key="refresh_job_requirements_dashboard_tab"):
            st.rerun()
    
    # Display current job requirements summary
    job_requirements = get_all_job_requirements()
    
    if job_requirements:
        st.subheader(f"Current Job Requirements ({len(job_requirements)})")
        
        # Group by primary field
        fields = {}
        for req in job_requirements:
            field = req.get('primary_field', 'General')
            if field not in fields:
                fields[field] = []
            fields[field].append(req)
        
        for field, reqs in fields.items():
            with st.expander(f"{field} ({len(reqs)} requirements)"):
                for req in reqs:
                    st.write(f"• **{req.get('job_title', 'Unknown')}** - Min CGPA: {req.get('required_cgpa', 'N/A')}, Experience: {req.get('required_experience_years', 0)} years")
    else:
        st.info("No job requirements found. Add some using the Job Requirements page.")

# --- Job Fair Management Tab ---
with tab4:
    st.header("Job Fair Management")
    
    st.write("Create, view, update, and delete job fairs in the system.")
    if st.button("📋 Manage All Job Fairs", use_container_width=True, key="manage_all_job_fairs_btn"):
        st.switch_page("pages/admin_job_fair_management.py")

# --- System Settings Tab ---
with tab5:
    st.header("System Settings")
    
    # API Health Check
    st.subheader("System Health")
    if is_api_healthy():
        st.success("✅ API is healthy and responding")
    else:
        st.error("❌ API health check failed")
    
    # System Statistics
    st.subheader("Detailed Statistics")
    user_stats = get_user_statistics()
    job_fair_stats = get_job_fair_statistics()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**User Statistics:**")
        for key, value in user_stats.items():
            st.write(f"• {key.replace('_', ' ').title()}: {value}")
    
    with col2:
        st.write("**Job Fair Statistics:**")
        for key, value in job_fair_stats.items():
            st.write(f"• {key.replace('_', ' ').title()}: {value}")
    
    # Configuration (placeholder)
    st.subheader("Configuration")
    st.info("System configuration options will be added here in future updates.")
      # Maintenance Actions
    st.subheader("Maintenance")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Clear Cache", use_container_width=True, key="admin_clear_cache_btn"):
            with st.spinner("Clearing system caches..."):
                response, success = make_api_request("admin/system/clear-cache", "POST")
                if success:
                    st.success(response.get("message", "Caches cleared successfully!"))
                else:
                    error_message = response.get("error", "Failed to clear caches.")
                    details = response.get("details")
                    if details:
                        error_message += f" Details: {details}"
                    st.error(error_message)
    
    with col2:
        if st.button("Backup Data", use_container_width=True, key="admin_backup_data_btn"):
            st.info("Data backup - to be implemented")
    
    with col3:
        if st.button("System Logs", use_container_width=True):
            st.info("System logs - to be implemented")

# Footer
st.markdown("---")
st.caption("Admin Dashboard - Resume Analyzer & Booth Recommendations System") 