import streamlit as st
from streamlit.components.v1 import html
import os
import sys
import time
from datetime import datetime
from PIL import Image
import io
from streamlit_cropper import st_cropper

# Configure the page - MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="My Profile - Resume Analyzer",
    page_icon="👤",
    layout="wide"
)

# Add lib directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))

from lib.api import get_current_user, update_user_profile, upload_profile_photo, delete_own_account
from lib.ui_components import load_css, render_header
from lib.auth_client import add_auth_persistence_js

# Load CSS and Auth JS
load_css()
add_auth_persistence_js()

def format_date(date_str):
    """Format date string to a more readable format"""
    if not date_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%b %d, %Y")
    except (ValueError, TypeError):
        return date_str

def display_profile(user):
    """Displays the user's profile information in a read-only format."""
    st.subheader("Profile Information")

    # --- Profile Picture and Basic Info ---
    col1, col2 = st.columns([1, 3])
    with col1:
        # Custom CSS to make the image circular
        st.markdown('<style>.profile-photo img { border-radius: 50%; object-fit: cover; width: 150px; height: 150px; }</style>', unsafe_allow_html=True)
        st.image(user.get('profile_photo_url', 'https://via.placeholder.com/150'), caption="Profile Picture", width=150)
    
    with col2:
        st.text_input("Full Name", value=user.get('name', ''), disabled=True)
        st.text_input("Email Address", value=user.get('email', ''), disabled=True)
        st.text_input("Phone Number", value=user.get('phone', 'N/A'), disabled=True)
        st.text_input("Location", value=user.get('location', 'N/A'), disabled=True)

    # --- Professional Details ---
    st.subheader("Professional Details")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Industry", value=user.get('industry', 'N/A'), disabled=True)
        st.text_input("Experience Level", value=user.get('experience_level', 'N/A'), disabled=True)
    with col2:
        st.text_input("LinkedIn Profile", value=user.get('linkedin_url', 'N/A'), disabled=True)
        st.text_input("GitHub Profile", value=user.get('github_url', 'N/A'), disabled=True)
    
    st.subheader("Professional Summary")
    st.text_area("Bio", value=user.get('bio', 'N/A'), height=150, disabled=True)
    
    if st.button("Edit Profile", type="primary"):
        st.session_state.edit_mode = True
        st.rerun()

def edit_profile(user):
    """Displays a form to edit the user's profile."""
    with st.form("profile_form"):
        st.subheader("Edit Profile Information")

        # --- Profile Picture Upload and Crop ---
        uploaded_photo = st.file_uploader("Change Profile Picture", type=["png", "jpg", "jpeg"])
        cropped_photo = None
        if uploaded_photo:
            img = Image.open(uploaded_photo)
            cropped_photo = st_cropper(img, realtime_update=True, box_color='blue', aspect_ratio=(1, 1))
            st.write("Preview")
            st.image(cropped_photo, width=150)

        # --- Personal Information ---
        st.subheader("Personal Information")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name", value=user.get('name', ''))
            email = st.text_input("Email Address", value=user.get('email', ''))
            phone = st.text_input("Phone Number", value=user.get('phone', ''))
        with col2:
            location = st.text_input("Location", value=user.get('location', ''))

        # --- Professional Details ---
        st.subheader("Professional Details")
        col1, col2 = st.columns(2)
        with col1:
            industry_options = ["Technology", "Healthcare", "Finance", "Education", "Manufacturing", "Retail", "Marketing", "Other"]
            industry_index = industry_options.index(user.get('industry')) if user.get('industry') in industry_options else 0
            industry = st.selectbox("Industry", industry_options, index=industry_index)
            
            experience_options = ["Entry Level", "Mid Level", "Senior", "Manager", "Executive"]
            experience_index = experience_options.index(user.get('experience_level')) if user.get('experience_level') in experience_options else 0
            experience_level = st.selectbox("Experience Level", experience_options, index=experience_index)
        with col2:
            linkedin_url = st.text_input("LinkedIn Profile URL", value=user.get('linkedin_url', ''))
            github_url = st.text_input("GitHub Profile URL", value=user.get('github_url', ''))

        bio = st.text_area("Professional Summary", value=user.get('bio', ''), height=150)
        
        # --- Form Submission ---
        submit_col, cancel_col = st.columns(2)
        with submit_col:
            submitted = st.form_submit_button("Save Changes", type="primary", use_container_width=True)
        with cancel_col:
            cancelled = st.form_submit_button("Cancel", use_container_width=True)
        
        if submitted:
            # Upload photo first if it exists
            if cropped_photo:
                with st.spinner("Uploading photo..."):
                    # Convert PIL image to bytes
                    buf = io.BytesIO()
                    cropped_photo.save(buf, format="PNG")
                    byte_im = buf.getvalue()
                    
                    # Create a file-like object for the API
                    class CroppedImageFile:
                        def __init__(self, name, content, type):
                            self.name = name
                            self.content = content
                            self.type = type
                        def getvalue(self):
                            return self.content

                    photo_file = CroppedImageFile(uploaded_photo.name, byte_im, "image/png")
                    photo_result, photo_success = upload_profile_photo(photo_file)
                    
                    if photo_success:
                        st.success("Photo uploaded successfully!")
                    else:
                        st.error(f"Failed to upload photo: {photo_result.get('message', 'Unknown error')}")
            
            # Then update the rest of the profile
            profile_data = {
                'name': name, 'email': email, 'phone': phone, 'location': location,
                'industry': industry, 'experience_level': experience_level,
                'linkedin_url': linkedin_url, 'github_url': github_url, 'bio': bio
            }
            with st.spinner("Updating profile..."):
                result, success = update_user_profile(profile_data)
                if success:
                    st.success("Profile updated successfully!")
                    st.session_state.edit_mode = False
                    time.sleep(1)
                    st.rerun()
                else:
                    error_message = result.get('message') or result.get('error', 'An unknown error occurred.')
                    if 'errors' in result and isinstance(result['errors'], dict):
                        error_details = ". ".join([f"{k.replace('_', ' ').title()}: {v[0]}" for k, v in result['errors'].items()])
                        st.error(f"Failed to update profile: {error_details}")
                    else:
                        st.error(f"Failed to update profile: {error_message}")
        
        if cancelled:
            st.session_state.edit_mode = False
            st.rerun()
            
def account_settings(user):
    """Manages password changes and account deletion."""
    st.subheader("Change Password")
    
    # Add form key based on a timestamp to reset form
    form_key = f"password_form_{st.session_state.get('form_timestamp', int(time.time()))}"
    
    with st.form(form_key):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        submitted = st.form_submit_button("Update Password", type="primary", use_container_width=True)
        if submitted:
            if not all([current_password, new_password, confirm_password]):
                st.error("Please fill all password fields.")
            elif new_password != confirm_password:
                st.error("New passwords do not match.")
            else:
                with st.spinner("Updating password..."):
                    result, success = update_user_profile({'current_password': current_password, 'new_password': new_password})
                    if success:
                        # Set form_timestamp to a new value to force form reset
                        st.session_state.form_timestamp = int(time.time())
                        st.success("Password updated successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        error_message = result.get('message') or result.get('error', 'An unknown error occurred.')
                        st.error(f"Failed to update password: {error_message}")

    st.subheader("Account Management")
    st.text(f"Account Type: {user.get('role', 'User').capitalize()}")
    st.text(f"Member Since: {format_date(user.get('created_at'))}")
    
    st.warning("Deleting your account is permanent and cannot be undone.")
    if st.button("Delete My Account", type="primary"):
        st.session_state.delete_confirm = True
    
    if st.session_state.get('delete_confirm'):
        st.error("Are you absolutely sure? This action cannot be reversed.")
        if st.button("Yes, I want to delete my account", type="primary"):
            # Call the API to delete the account
            with st.spinner("Deleting account..."):
                result, success = delete_own_account()
                if success:
                    st.success("Account deleted successfully!")
                    # Clear auth state
                    st.session_state.authenticated = False
                    if 'user_token' in st.session_state:
                        del st.session_state.user_token
                    # Redirect to home page after short delay
                    time.sleep(2)
                    st.switch_page("app.py")
                else:
                    error_message = result.get('message') or result.get('error', 'An unknown error occurred.')
                    st.error(f"Failed to delete account: {error_message}")

def main():
    """Main function for the profile page."""
    render_header()

    if "authenticated" not in st.session_state or not st.session_state.authenticated:
        st.warning("Please log in first.")
        st.stop()

    user_data, success = get_current_user()
    if not success:
        st.error(f"Failed to load profile: {user_data.get('error', 'Unknown error')}")
        st.stop()
    
    user = user_data['data']

    # Initialize session state for edit_mode and delete_confirm
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False
    if 'delete_confirm' not in st.session_state:
        st.session_state.delete_confirm = False
    if 'form_timestamp' not in st.session_state:
        st.session_state.form_timestamp = int(time.time())

    tabs = st.tabs(["Profile Information", "Account Settings"])
    with tabs[0]:
        if st.session_state.edit_mode:
            edit_profile(user)
        else:
            display_profile(user)
    
    with tabs[1]:
        account_settings(user)

if __name__ == "__main__":
    main()