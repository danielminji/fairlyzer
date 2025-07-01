"""
My Resumes Page - Resume Analyzer & Booth Recommendations

This page displays a list of the user's uploaded resumes and provides
options to view detailed analysis, delete resumes, or upload new ones.
"""

import streamlit as st
from streamlit.components.v1 import html
import os
import sys
import time
import json
from datetime import datetime

# Add lib directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))

# Configure page - MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="My Resumes - Resume Analyzer",
    page_icon="📋",
    layout="wide"
)

# Import necessary functions from lib
import requests
from lib.api import API_BASE_URL, get_auth_headers, upload_resume
from lib.auth_client import add_auth_persistence_js, check_auth
from lib.ui_components import render_header, render_footer
from lib.navigation import display_sidebar_navigation

# Check authentication
if check_auth():
    st.session_state.current_path = "my_resumes"
    display_sidebar_navigation()
else:
    st.warning("Please log in first to view your resumes.")
    st.session_state.current_path = "my_resumes"
    html("""
    <script>
        setTimeout(function() {
            window.location.href = "/";
        }, 2000);
    </script>
    """)
    st.stop()

# Main UI
render_header()
st.title("My Resumes")
st.caption("View, analyze, and manage your uploaded resumes")

# API Functions
def get_user_resumes():
    """Get user's uploaded resumes"""
    try:
        headers = get_auth_headers()
        
        response = requests.get(
            f"{API_BASE_URL}/resumes",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict):
                return data.get('data', [])
            elif isinstance(data, list):
                return data
            return []
        else:
            st.error(f"Failed to fetch resumes: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error fetching resumes: {str(e)}")
        return []

def delete_resume(resume_id):
    """Delete a resume"""
    try:
        headers = get_auth_headers()
        
        response = requests.delete(
            f"{API_BASE_URL}/resumes/{resume_id}",
            headers=headers
        )
        
        if response.status_code in [200, 204]:
            data = response.json()
            if data.get('status') == 'success':
                st.success(data.get('message', 'Resume deleted successfully!'))
                time.sleep(1)
                st.rerun()
                return True
            else:
                st.error(data.get('message', 'Failed to delete resume.'))
                return False
        else:
            error_msg = response.text
            try:
                error_data = response.json()
                if isinstance(error_data, dict):
                    error_msg = error_data.get('message', error_msg)
            except:
                pass
            st.error(f"Error deleting resume: {error_msg}")
            return False
    except Exception as e:
        st.error(f"Error deleting resume: {str(e)}")
        return False

def format_date(date_str):
    """Format date string for display"""
    try:
        if not date_str:
            return "Unknown"
            
        # Try parsing as ISO format
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        
        # Format as Month Day, Year
        return dt.strftime("%B %d, %Y")
    except:
        return date_str

def view_resume_analysis(resume_id):
    """Redirect to the resume analysis page"""
    # Store resume ID in session state for the analysis page to access
    st.session_state.selected_resume_id = resume_id
    # Redirect to the dedicated analysis page
    st.switch_page("pages/02_resume_analysis.py")

# Search/Filter functionality
st.subheader("Filter Resumes")
search_query = st.text_input("Search by filename:", key="resume_search_query")

# Add a refresh button
if st.button("🔄 Refresh List", key="refresh_resumes_list"):
    st.rerun()

# Display user's resumes
resumes = get_user_resumes()

filtered_resumes = []
if resumes:
    if search_query:
        for r in resumes:
            if search_query.lower() in r.get('original_filename', '').lower():
                filtered_resumes.append(r)
    else:
        filtered_resumes = resumes

if not filtered_resumes:
    if search_query:
        st.info(f"No resumes found matching '{search_query}'.")
    else:
        st.info("No Resumes Found. Upload a resume from the 'Resume Upload' page.")
    
    # if st.button("Upload Your First Resume", type="primary"):
    # st.switch_page("pages/01_resume_upload.py") # Button to upload page is good if list is empty
else:
    # Display each resume
    st.subheader("Your Resumes")
    
    for resume_item in filtered_resumes: # Changed variable name
        resume_id = resume_item.get('id')
        # Use columns for better layout: Filename | Upload Date | Status | Actions
        col1, col2, col3, col4, col5 = st.columns([3, 2, 1.5, 1, 1])

        with col1:
            st.markdown(f"**{resume_item.get('original_filename', 'Untitled Resume')}**")
        with col2:
            st.caption(f"Uploaded: {format_date(resume_item.get('created_at', ''))}")
        with col3:
            status = resume_item.get('parsing_status', 'unknown')
            # Simple status display, can be enhanced with icons/colors
            if status.lower() == 'analyzed' or status.lower() == 'completed':
                st.markdown(f"<span style='color: green;'>●</span> {status.title()}", unsafe_allow_html=True)
            elif status.lower() == 'pending_analysis' or status.lower() == 'processing':
                st.markdown(f"<span style='color: orange;'>●</span> {status.title()}", unsafe_allow_html=True)
            elif status.lower() == 'error' or status.lower() == 'failed':
                st.markdown(f"<span style='color: red;'>●</span> {status.title()}", unsafe_allow_html=True)
            else:
                st.caption(status.title())
        with col4:
            if st.button("📊 Analyze", key=f"analyze_{resume_id}_myresumes"):
                view_resume_analysis(resume_id)
        with col5:
            if st.button("🗑️ Delete", key=f"delete_{resume_id}_myresumes"):
                if delete_resume(resume_id):
                    # Rerun handled by delete_resume on success
                    pass 
                else:
                    st.error("Failed to initiate delete.")
        st.divider()

# Sidebar with tips
with st.sidebar:
    st.markdown("### Managing Your Resumes")
    st.markdown("""
    Here you can:
    
    * **View Analysis** - See detailed skills, education, and experience extracted from your resume
    * **Get Recommendations** - Find company booths matching your profile
    * **Upload New Resumes** - Add multiple resumes for different job types
    * **Delete Old Resumes** - Remove outdated resumes
    
    For the best results, keep your most recent and relevant resume.
    """)
    
    st.markdown("---")
    
    st.markdown("### Why Resume Analysis Matters")
    st.markdown("""
    Our AI-powered analysis:
    
    * Identifies your key skills and qualifications
    * Matches your profile to relevant employers
    * Helps you prioritize which booths to visit
    * Saves you time at the job fair
    
    The more accurate your resume, the better your recommendations will be!
    """)
    
    # Include a help section
    st.markdown("---")
    st.markdown("### Need Help?")
    st.markdown("""
    If you're having trouble viewing your resume analysis or recommendations, try:
    
    1. Refreshing the page
    2. Reuploading your resume in PDF format
    3. Ensuring your resume is text-based (not scanned)
    
    Contact our support team if you continue to experience issues.
    """)

# At the bottom of the file
if __name__ == "__main__":
    # Check for resume_id in query parameters
    params = st.query_params
    
    # Handle delete action
    if "delete_id" in params:
        delete_id = params["delete_id"]
        success = delete_resume(delete_id)
        if success:
            st.success("Resume deleted successfully!")
            # Clear parameter and refresh
            params.clear()
            time.sleep(1)
            st.rerun()
        else:
            st.error("Failed to delete resume.")
    
    # Handle view action
    elif "resume_id" in params:
        resume_id = params["resume_id"]
        # Redirect to resume_analysis page
        view_resume_analysis(resume_id)
    else:
        # Display main interface
        pass # Remove if causes issues, the script runs top-down. Main function for this page should be the top-level code after imports and auth. 
    
    render_footer()