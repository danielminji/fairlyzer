"""
Resume Upload Page - Resume Analyzer & Booth Recommendations

This page allows users to upload their resumes for analysis and recommendations.
"""

import streamlit as st
import os
import time
from datetime import datetime
import io
import pandas as pd
import re
import tempfile
import webbrowser
from datetime import timedelta

# Import local modules
from lib import api
from lib.auth_client import check_auth, get_current_user, require_auth
from lib.ui_components import render_header, render_footer, render_status_indicator
from lib.css.ui import load_css
from lib.navigation import display_sidebar_navigation

# Page configuration
st.set_page_config(
    page_title="Upload Resume - Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

# Load CSS
load_css()

# Apply authentication requirement
@require_auth()
def main():
    """Main function for the resume upload page"""
    display_sidebar_navigation()
    
    st.title("Upload Your Resume")
    st.write("Upload your resume to get started with analysis and booth recommendations.")
    
    # Upload form
    with st.form("resume_upload_form", clear_on_submit=True):
        uploaded_file = st.file_uploader(
            "Choose a resume file",
            type=["pdf", "docx", "doc"],
            help="Supported formats: PDF, Word Document (.docx, .doc)"
        )
        
        description = st.text_input(
            "Description (optional)",
            help="Add a short description to identify this resume"
        )
        
        upload_options = st.expander("Upload Options")
        with upload_options:
            analyze_immediately = st.checkbox("Analyze immediately after upload", value=True)
            save_for_future = st.checkbox("Save for future job fairs", value=True)
            show_debug_info = st.checkbox("Show debug information", value=False)
        
        submit_button = st.form_submit_button("Upload Resume")
        
        if submit_button:
            if uploaded_file is None:
                st.error("Please select a file to upload.")
            else:
                # Show debug information if enabled
                if show_debug_info:
                    st.write("### Debug Information")
                    debug_info = {
                        "Original Filename": getattr(uploaded_file, "name", "Unknown"),
                        "File Type": getattr(uploaded_file, "type", "Unknown"),
                        "File Size": f"{getattr(uploaded_file, 'size', 0) / 1024:.2f} KB",
                        "File Content Type": getattr(uploaded_file, "content_type", "Unknown"),
                    }
                    
                    # Display file details for debugging
                    debug_df = pd.DataFrame(list(debug_info.items()), columns=["Property", "Value"])
                    st.dataframe(debug_df, use_container_width=True)
                
                # Show progress spinner
                with st.spinner("Uploading and processing your resume..."):
                    try:
                        # Create a progress bar for better feedback
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        # Update progress bar
                        status_text.text("Processing file...")
                        progress_bar.progress(10)
                        time.sleep(0.5)
                        
                        # Get original filename for display only
                        original_filename = getattr(uploaded_file, "name", "Unknown")
                        if show_debug_info:
                            st.write(f"Original filename: {original_filename}")
                        
                        # Update progress bar
                        status_text.text("Preparing file for upload...")
                        progress_bar.progress(30)
                        time.sleep(0.5)
                        
                        # Always use direct upload method
                        status_text.text("Uploading to server...")
                        progress_bar.progress(50)
                        response, success = api.upload_resume(uploaded_file, description)
                        
                        progress_bar.progress(80)
                        
                        if success:
                            resume_id = response.get('data', {}).get('id')
                            st.session_state.active_resume_id = resume_id
                            
                            status_text.text("Upload successful!")
                            progress_bar.progress(100)
                            time.sleep(0.5)
                            progress_bar.empty()
                            status_text.empty()
                            
                            st.success("Resume uploaded successfully!")
                            st.session_state.upload_success = True # Set flag for the button

                        else:
                            status_text.text("Upload failed")
                            progress_bar.empty()
                            status_text.empty()
                            
                            error_msg = response.get('error', 'Unknown error occurred')
                            st.error(f"Error uploading resume: {error_msg}")
                            
                            # Provide guidance based on the error
                            if "strtolower" in error_msg:
                                st.warning("There was an issue with the file format. We'll try with a simplified method.")
                                time.sleep(1)
                                
                                # Automatically try the fallback method
                                st.info("Trying alternative upload method...")
                                fallback_response, fallback_success = api.upload_resume_bypass_validation(uploaded_file, description)
                                
                                if fallback_success:
                                    resume_id = fallback_response.get('data', {}).get('id')
                                    st.session_state.active_resume_id = resume_id
                                    st.success("Resume uploaded successfully with simplified method!")
                                else:
                                    fallback_error = fallback_response.get('error', 'Unknown error')
                                    st.error(f"Simplified upload also failed: {fallback_error}")
                                    
                                    # Show detailed troubleshooting steps
                                    st.warning("Please try the following:")
                                    st.markdown("""
                                    1. **Rename your file** to a simple name like 'resume.pdf' without spaces or special characters
                                    2. **Try a different file format** - if using Word, save as PDF
                                    3. **Make sure file is not open** in another application
                                    """)
                            
                            elif "file" in error_msg.lower() or "mimes" in error_msg.lower():
                                st.warning("Please ensure your file is in PDF, DOC, or DOCX format and not corrupted.")
                            elif "token" in error_msg.lower() or "auth" in error_msg.lower():
                                st.warning("Your session may have expired. Please logout and login again.")
                            
                            # Show the full error details if debug is enabled
                            if show_debug_info and 'details' in response:
                                st.write("### Error Details")
                                st.json(response.get('details', {}))
                                
                    except Exception as e:
                        st.error(f"An unexpected error occurred: {str(e)}")
                        st.code(str(e))
                        st.info("Please try again or contact support if the issue persists.")

    # Display "Go to My Resumes" button if a resume was just uploaded successfully
    if 'upload_success' in st.session_state and st.session_state.upload_success:
        if st.button("📋 Go to My Resumes to Continue", key="go_to_my_resumes_after_successful_upload", use_container_width=True):
            del st.session_state.upload_success # Clear the flag before switching
            st.switch_page("pages/02_my_resumes.py")
        else:
            # Show the horizontal rule if the button hasn't been clicked yet in this successful state
            st.markdown("<hr style='margin-top:1.5em; margin-bottom:1.5em;'>", unsafe_allow_html=True)

    # Navigation buttons - MOVED OUTSIDE THE FORM
    if 'active_resume_id' in st.session_state and st.session_state.active_resume_id:
        resume_id = st.session_state.active_resume_id
        st.success("Resume Uploaded! What would you like to do next?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 Analyze This Resume", use_container_width=True, key="analyze_this_resume_upload_page"):
                st.session_state.selected_resume_id = resume_id
                st.switch_page("pages/02_resume_analysis.py")
        with col2:
            if st.button("📋 View All My Resumes", use_container_width=True, key="view_all_my_resumes_upload_page"):
                st.switch_page("pages/02_my_resumes.py")
    
    # Add a direct manual recovery option when nothing else works
    if 'success' in locals() and not success and uploaded_file is not None:
        with st.expander("Still having issues? Try our advanced method"):
            st.warning("If you're still experiencing upload issues, try this recovery method:")
            
            if st.button("🛠️ Try Advanced Recovery Method"):
                with st.spinner("Using advanced recovery method..."):
                    try:
                        # Create a completely fresh file object with minimal properties
                        file_content = uploaded_file.getvalue() if hasattr(uploaded_file, 'getvalue') else uploaded_file.read()
                        
                        # Write content to a temporary file
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                            tmp.write(file_content)
                            tmp_path = tmp.name
                        
                        st.info(f"Created temporary file for upload")
                        
                        # Open the file for upload
                        with open(tmp_path, 'rb') as f:
                            # Create a simple file object with a standard name
                            simple_file = io.BytesIO(f.read())
                            simple_file.name = "resume.pdf"  # Ultra simple name
                            
                            # Try the upload with our minimal file
                            recovery_response, recovery_success = api.upload_resume_bypass_validation(simple_file, description)
                        
                        # Clean up
                        try:
                            os.unlink(tmp_path)
                        except:
                            pass
                        
                        if recovery_success:
                            resume_id = recovery_response.get('data', {}).get('id')
                            st.session_state.active_resume_id = resume_id
                            st.success("✅ Resume uploaded successfully with advanced recovery method!")
                            
                            # Ask what to do next
                            st.info("What would you like to do now?")
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("Analyze This Resume", key="analyze_recovered"):
                                    st.session_state.page = 'resume_analysis'
                                    st.rerun()
                            with col2:
                                if st.button("Get Recommendations", key="recommend_recovered"):
                                    st.session_state.page = 'booth_recommendations'
                                    st.rerun()
                        else:
                            error_msg = recovery_response.get('error', 'Unknown error occurred')
                            st.error(f"😔 Advanced recovery also failed: {error_msg}")
                            
                            # Provide contact support option
                            st.info("Please contact support with the following details:")
                            st.code(f"Error: {error_msg}\nTimestamp: {datetime.now()}")
                    except Exception as e:
                        st.error(f"Error during advanced recovery: {str(e)}")

    # Display a help section
    with st.expander("Tips for better resume analysis"):
        st.markdown("""
        ### Tips for better resume analysis
        
        - Ensure your resume is in a standard format (PDF or Word document)
        - Make sure your resume includes clear sections for skills, experience, education, etc.
        - List your skills explicitly, especially technical skills and certifications
        - Include dates for your work experience and education in a standard format
        - Avoid using custom fonts, graphics, or tables that might interfere with text extraction
        """)
    
    # Recent uploads section
    st.subheader("Your Recent Uploads")
    response, success = api.get_user_resumes()
    
    if success:
        resumes = response.get('data', [])
        
        if resumes:
            # Sort by upload date, newest first
            resumes.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            # Display the 5 most recent
            recent_resumes = resumes[:5]
            
            for resume_item_recent in recent_resumes:
                col1, col2 = st.columns([3, 2])
                
                with col1:
                    st.markdown(f"**{resume_item_recent.get('file_name', resume_item_recent.get('filename', 'Unnamed Resume'))}**")
                    upload_date = resume_item_recent.get('created_at', 'Unknown')
                    try:
                        # Try to format the date if possible
                        date_obj_utc = datetime.fromisoformat(upload_date.replace('Z', '+00:00'))
                        # Convert to Malaysian Time (UTC+8)
                        date_obj_myt = date_obj_utc + timedelta(hours=8)
                        formatted_date = date_obj_myt.strftime("%B %d, %Y at %I:%M %p MYT")
                        st.write(f"Uploaded: {formatted_date}")
                    except:
                        st.write(f"Uploaded: {upload_date} (raw UTC)") # Clarify raw if formatting fails
                
                st.divider()
        else:
            st.info("You haven't uploaded any resumes yet.")
    else:
        st.error(f"Error loading resumes: {response.get('error', 'Unknown error')}")
    
    render_footer()

if __name__ == "__main__":
    main() 