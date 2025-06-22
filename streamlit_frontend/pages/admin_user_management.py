import streamlit as st
import pandas as pd
import sys
import os

# Add lib directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))

from lib.api_helpers import make_api_request, safe_get_users, safe_get_organizers, is_api_healthy
from lib.ui_components import load_css, render_header, render_status_indicator, handle_api_error
from lib.navigation import display_sidebar_navigation

# Helper functions
def get_all_users():
    """Get all users from API"""
    users, success = safe_get_users()
    if not success:
        st.error("Failed to load users. Please check API connection.")
    return users

def get_pending_organizers():
    """Get pending organizer approvals"""
    organizers, success = safe_get_organizers("pending")
    if not success:
        st.error("Failed to load pending organizers. Please check API connection.")
    return organizers

def get_approved_organizers():
    """Get approved organizers"""
    organizers, success = safe_get_organizers("approved")
    if not success:
        st.error("Failed to load approved organizers. Please check API connection.")
    return organizers

def approve_organizer(user_id):
    """Approve an organizer"""
    result, success = make_api_request(f"admin/organizers/{user_id}/approve", "POST")
    return success, result

def reject_organizer(user_id):
    """Reject an organizer"""
    result, success = make_api_request(f"admin/organizers/{user_id}/reject", "POST")
    return success, result

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

def reset_user_password(user_id, new_password):
    """Reset user's password"""
    data = {"password": new_password, "password_confirmation": new_password}
    result, success = make_api_request(f"admin/users/{user_id}/reset-password", "POST", data)
    return success, result

def delete_user(user_id):
    """Delete a user"""
    result, success = make_api_request(f"admin/users/{user_id}", "DELETE")
    return success, result

# Get the tab parameter from URL if provided - but check "tab" first before any query_params
try:
    tab_param = st.query_params.get("tab", ["0"])[0]
    initial_tab = int(tab_param) if tab_param.isdigit() and 0 <= int(tab_param) < 4 else 0
except:
    initial_tab = 0

# Page config
st.set_page_config(
    page_title="User Management",
    page_icon="👥",
    layout="wide"
)

# Load CSS
load_css()

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

# --- Admin Authenticated Content Starts Here ---

# Display navigation sidebar for admin pages
display_sidebar_navigation() 

# Header for this specific admin page
st.title("User Management")
st.caption("Manage all users, organizers, and job seekers")

# Add a success message display area for actions like approval/rejection
if "action_success_message" in st.session_state and st.session_state.action_success_message:
    st.success(st.session_state.action_success_message)

# Navigation bar
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.button("← Back to Admin Dashboard", use_container_width=True):
        st.switch_page("pages/admin_dashboard.py")
with col3:
    refresh = st.button("🔄 Refresh Data", use_container_width=True)

# Tab navigation
tab_names = ["All Users", "Pending Organizers", "Approved Organizers", "Job Seekers"]
tabs = st.tabs(tab_names)

# All Users Tab
with tabs[0]:
    st.subheader("All Users")
    
    # Search and filters
    search_col1, search_col2 = st.columns([3, 1])
    with search_col1:
        search_term = st.text_input("Search by name or email", "")
    with search_col2:
        role_filter = st.multiselect("Filter by role", options=["admin", "organizer", "user"], default=["admin", "organizer", "user"])
    
    # Get and display users
    with st.spinner("Loading users..."):
        users = get_all_users()
        
    if not users:
        st.info("No users found or error loading users")
    else:
        # Filter users
        filtered_users = [u for u in users if u.get('role', 'user') in role_filter]
        if search_term:
            filtered_users = [u for u in filtered_users if 
                             search_term.lower() in u.get('name', '').lower() or 
                             search_term.lower() in u.get('email', '').lower()]
        
        st.write(f"Showing {len(filtered_users)} of {len(users)} users")
        
        # Display users in a more streamlit-native way
        for user in filtered_users:
            st.divider()
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader(user.get('name', 'Unknown'))
                st.write(f"**Role:** {user.get('role', 'user').upper()}")
                st.write(f"**Email:** {user.get('email', 'No email')}")
                status = "ACTIVE" if user.get('is_active', True) else "INACTIVE"
                st.write(f"**Status:** {status}")
            
            with col2:
                if st.button("Manage User", key=f"manage_{user.get('id')}", use_container_width=True):
                    st.session_state.selected_user = user
                    
            if "selected_user" in st.session_state and st.session_state.selected_user.get('id') == user.get('id'):
                with st.expander("User Actions", expanded=True):
                    action_col1, action_col2 = st.columns(2)
                    
                    with action_col1:
                        # Role change if not own account
                        if st.session_state.user_id != user.get('id'):
                            new_role = st.selectbox("Change Role", 
                                                   options=["user", "organizer", "admin"],
                                                   index=["user", "organizer", "admin"].index(user.get('role', 'user')),
                                                   key=f"role_{user.get('id')}")
                            
                            if new_role != user.get('role'):
                                if st.button("Update Role", key=f"update_role_{user.get('id')}"):
                                    with st.spinner("Updating role..."):
                                        success, result = update_user_role(user.get('id'), new_role)
                                        if success:
                                            st.success(f"Role updated to {new_role}!")
                                            st.rerun()
                                        else:
                                            error_msg = result.get('error', 'Failed to update role') if isinstance(result, dict) else 'Failed to update role'
                                            st.error(error_msg)
                        else:
                            st.info("You cannot change your own role")
                    
                    with action_col2:
                        # Status toggle if not own account
                        if st.session_state.user_id != user.get('id'):
                            is_active = user.get('is_active', True)
                            if st.button(f"{'Deactivate' if is_active else 'Activate'} User", 
                                        key=f"toggle_{user.get('id')}"):
                                with st.spinner(f"{'Deactivating' if is_active else 'Activating'} user..."):
                                    success, result = toggle_user_status(user.get('id'), not is_active)
                                    if success:
                                        st.success(f"User {'deactivated' if is_active else 'activated'}!")
                                        st.rerun()
                                    else:
                                        error_msg = result.get('error', 'Failed to update status') if isinstance(result, dict) else 'Failed to update status'
                                        st.error(error_msg)
                        else:
                            st.info("You cannot deactivate your own account")
                    
                    # Password reset
                    st.subheader("Reset Password")
                    password = st.text_input("New Password", type="password", key=f"pwd_{user.get('id')}")
                    confirm_password = st.text_input("Confirm Password", type="password", key=f"confirm_{user.get('id')}")
                    
                    if st.button("Reset Password", key=f"reset_{user.get('id')}"):
                        if not password:
                            st.error("Password cannot be empty")
                        elif password != confirm_password:
                            st.error("Passwords do not match")
                        elif len(password) < 8:
                            st.error("Password must be at least 8 characters")
                        else:
                            with st.spinner("Resetting password..."):
                                success, result = reset_user_password(user.get('id'), password)
                                if success:
                                    st.success("Password reset successfully!")
                                else:
                                    error_msg = result.get('error', 'Failed to reset password') if isinstance(result, dict) else 'Failed to reset password'
                                    st.error(error_msg)
                    
                    # Delete user option (with confirmation)
                    if st.session_state.user_id != user.get('id'):
                        st.subheader("Danger Zone")
                        delete_confirm = st.checkbox("I understand this action cannot be undone", key=f"confirm_delete_{user.get('id')}")
                        
                        if delete_confirm:
                            if st.button("Delete User", key=f"delete_{user.get('id')}", type="primary"):
                                with st.spinner("Deleting user..."):
                                    success, result = delete_user(user.get('id'))
                                    if success:
                                        st.success("User deleted successfully!")
                                        st.rerun()
                                    else:
                                        error_msg = result.get('error', 'Failed to delete user') if isinstance(result, dict) else 'Failed to delete user'
                                        st.error(error_msg)

# Pending Organizers Tab
with tabs[1]:
    st.subheader("Pending Organizer Approvals")
    
    # Get and display pending organizers
    with st.spinner("Loading pending organizers..."):
        pending_organizers = get_pending_organizers()
    
    if not pending_organizers:
        st.info("No pending organizer approvals")
    else:
        st.success(f"Found {len(pending_organizers)} pending organizer(s)")
        
        # Display pending organizers
        for organizer in pending_organizers:
            st.divider()
            cols = st.columns([3, 1, 1])
            
            with cols[0]:
                st.subheader(organizer.get('name', 'Unknown'))
                st.write(f"**Email:** {organizer.get('email', 'No email')}")
            
            with cols[1]:
                if st.button("✅ Approve", key=f"approve_{organizer.get('id')}", use_container_width=True):
                    with st.spinner("Approving organizer..."):
                        success, result = approve_organizer(organizer.get('id'))
                        if success:
                            st.success("Organizer approved!")
                            st.rerun()
                        else:
                            error_msg = result.get('error', 'Failed to approve organizer') if isinstance(result, dict) else 'Failed to approve organizer'
                            st.error(error_msg)
            
            with cols[2]:
                if st.button("❌ Reject", key=f"reject_{organizer.get('id')}", use_container_width=True):
                    with st.spinner("Rejecting organizer..."):
                        success, result = reject_organizer(organizer.get('id'))
                        if success:
                            st.success("Organizer rejected!")
                            st.rerun()
                        else:
                            error_msg = result.get('error', 'Failed to reject organizer') if isinstance(result, dict) else 'Failed to reject organizer'
                            st.error(error_msg)

# Approved Organizers Tab
with tabs[2]:
    st.subheader("Approved Organizers")
    
    # Get and display approved organizers
    with st.spinner("Loading approved organizers..."):
        approved_organizers = get_approved_organizers()
    
    if not approved_organizers:
        st.info("No approved organizers found")
    else:
        st.success(f"Found {len(approved_organizers)} approved organizer(s)")
        
        # Display approved organizers in a more streamlit-native way
        for organizer in approved_organizers:
            st.divider()
            st.subheader(organizer.get('name', 'Unknown'))
            st.write(f"**Email:** {organizer.get('email', 'No email')}")
            status = "ACTIVE" if organizer.get('is_active', True) else "INACTIVE"
            st.write(f"**Status:** {status}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Manage User", key=f"manage_approved_{organizer.get('id')}", use_container_width=True):
                    st.session_state.selected_organizer = organizer
            
            if "selected_organizer" in st.session_state and st.session_state.selected_organizer.get('id') == organizer.get('id'):
                with st.expander("User Actions", expanded=True):
                    # Allow changing back to regular user
                    if st.button("Revoke Organizer Status", key=f"revoke_{organizer.get('id')}"):
                        with st.spinner("Revoking organizer status..."):
                            success, result = update_user_role(organizer.get('id'), "user")
                            if success:
                                st.success("Organizer status revoked!")
                                st.rerun()
                            else:
                                error_msg = result.get('error', 'Failed to revoke organizer status') if isinstance(result, dict) else 'Failed to revoke organizer status'
                                st.error(error_msg)
                    
                    # Status toggle
                    is_active = organizer.get('is_active', True)
                    if st.button(f"{'Deactivate' if is_active else 'Activate'} Account", key=f"toggle_org_{organizer.get('id')}"):
                        with st.spinner(f"{'Deactivating' if is_active else 'Activating'} account..."):
                            success, result = toggle_user_status(organizer.get('id'), not is_active)
                            if success:
                                st.success(f"Account {'deactivated' if is_active else 'activated'}!")
                                st.rerun()
                            else:
                                error_msg = result.get('error', 'Failed to update account status') if isinstance(result, dict) else 'Failed to update account status'
                                st.error(error_msg)

# Job Seekers Tab
with tabs[3]:
    st.subheader("Job Seekers")
    
    # Get and display job seekers (regular users)
    with st.spinner("Loading job seekers..."):
        all_users = get_all_users()
        job_seekers = [u for u in all_users if u.get('role') == 'user']
    
    if not job_seekers:
        st.info("No job seekers found")
    else:
        st.success(f"Found {len(job_seekers)} job seeker(s)")
        
        # Display job seekers
        for user in job_seekers:
            st.divider()
            st.subheader(user.get('name', 'Unknown'))
            st.write(f"**Email:** {user.get('email', 'No email')}")
            st.write(f"**Joined:** {user.get('created_at', 'Unknown')}")
            
            cols = st.columns(2)
            
            with cols[0]:
                if st.button("View Profile", key=f"view_{user.get('id')}", use_container_width=True):
                    st.session_state.view_user = user
            
            with cols[1]:
                if st.button("Promote to Organizer", key=f"promote_{user.get('id')}", use_container_width=True):
                    with st.spinner("Promoting user to organizer..."):
                        success, result = update_user_role(user.get('id'), "organizer")
                        if success:
                            st.success("User promoted to organizer!")
                            st.rerun()
                        else:
                            error_msg = result.get('error', 'Failed to promote user') if isinstance(result, dict) else 'Failed to promote user'
                            st.error(error_msg)

# System Status
st.subheader("System Status")
with st.expander("API Connection Status"):
    if is_api_healthy():
        st.success("✅ API connection is working")
    else:
        st.error("❌ API connection issue detected")
        st.write("Please check your API server status or connection settings.")

# Auto-select tab based on URL parameter
if initial_tab > 0:
    # This JavaScript will be executed in the browser to select the appropriate tab
    js = f"""
    <script>
        window.setTimeout(function() {{
            // Find all tab buttons
            var tabs = document.querySelectorAll('button[data-baseweb="tab"]');
            // Click the tab at the desired index if it exists
            if (tabs && tabs.length > {initial_tab}) {{
                tabs[{initial_tab}].click();
            }}
        }}, 100);
    </script>
    """
    st.components.v1.html(js, height=0) 