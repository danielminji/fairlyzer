import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime, timedelta, time
import json

# Add lib directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))

from lib.api_helpers import make_api_request # Use the wrapper that returns 2 values
from lib.ui_components import load_css, handle_api_error
from lib.navigation import display_sidebar_navigation

# Page config
st.set_page_config(
    page_title="Admin: Job Fair Management",
    page_icon="🏢",
    layout="wide"
)

# Load CSS
load_css()

# Check authentication
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Please log in first.")
    st.switch_page("app.py")
    st.stop()

# Check admin permissions
if st.session_state.user_role != "admin":
    st.error("You don't have permission to access this page. Admin access required.")
    st.switch_page("app.py")
    st.stop()

# --- Admin Authenticated Content ---
display_sidebar_navigation()

st.title("Job Fair Management")
st.caption("Administer all job fairs in the system")

# API Endpoints
JOB_FAIRS_ENDPOINT = "admin/job-fairs"
ORGANIZERS_ENDPOINT = "admin/users/organizers" # Hypothetical, may need to fetch all users and filter or use a dedicated one

# --- Helper Functions ---
def fetch_job_fairs():
    response, success = make_api_request(JOB_FAIRS_ENDPOINT, "GET", params={'per_page': 'all'})
    if success:
        return response.get('data', []) if isinstance(response, dict) else []
    else:
        handle_api_error(response, "Failed to fetch job fairs.")
        return []

def fetch_organizers():
    response, success = make_api_request("admin/job-fairs/organizers", "GET")
    if success:
        return response.get('data', []) if isinstance(response, dict) else []
    else:
        handle_api_error(response, "Failed to fetch organizers.")
        return []

# --- Initialize session state for CRUD operations ---
if 'editing_job_fair_id' not in st.session_state:
    st.session_state.editing_job_fair_id = None
if 'job_fair_data_for_edit' not in st.session_state:
    st.session_state.job_fair_data_for_edit = {}
if 'confirm_delete_job_fair_id' not in st.session_state:
    st.session_state.confirm_delete_job_fair_id = None
# New session state for managing booths of a selected job fair
if 'selected_job_fair_id_for_booths' not in st.session_state:
    st.session_state.selected_job_fair_id_for_booths = None
if 'selected_job_fair_title_for_booths' not in st.session_state:
    st.session_state.selected_job_fair_title_for_booths = None

# New session states for booth CRUD
if 'editing_booth_id' not in st.session_state:
    st.session_state.editing_booth_id = None
if 'booth_data_for_edit' not in st.session_state:
    st.session_state.booth_data_for_edit = {}
if 'confirm_delete_booth_id' not in st.session_state:
    st.session_state.confirm_delete_booth_id = None
if 'success_message_booth_admin' not in st.session_state:
    st.session_state.success_message_booth_admin = None
if 'error_message_booth_admin' not in st.session_state:
    st.session_state.error_message_booth_admin = None

# --- Main Page Logic ---

# Button to go back to Admin Dashboard
if st.button("← Back to Admin Dashboard", key="back_to_admin_dashboard_job_fairs"):
    st.switch_page("pages/admin_dashboard.py")

st.divider()

# Tabs for Create/Manage
tab_list, tab_create = st.tabs(["List Job Fairs", "Create New Job Fair"])

with tab_list:
    st.subheader("Existing Job Fairs")
    if st.button("🔄 Refresh Job Fairs", key="refresh_job_fairs_list_admin"):
        st.rerun()

    job_fairs = fetch_job_fairs()
    
    if not job_fairs:
        st.info("No job fairs found. You can create one in the 'Create New Job Fair' tab.")
    else:
        # Display success/error messages for CRUD operations
        if "success_message_jf_admin" in st.session_state and st.session_state.success_message_jf_admin:
            st.success(st.session_state.success_message_jf_admin)
            st.session_state.success_message_jf_admin = None # Clear after display
        if "error_message_jf_admin" in st.session_state and st.session_state.error_message_jf_admin:
            st.error(st.session_state.error_message_jf_admin)
            st.session_state.error_message_jf_admin = None # Clear after display

        # Define headers for the table
        cols_header = st.columns((0.5, 1.5, 1.5, 1.7, 1.2, 1.2, 0.8, 0.7, 0.5, 0.5, 1)) # ID, Title, Organizer, Location, Starts, Ends, Status, Booths, Edit, Del, Manage Booths
        headers = ['ID', 'Title', 'Organizer', 'Location', 'Starts', 'Ends', 'Status', 'Booths', 'Edit', 'Del', 'Manage Booths']
        for col, header_text in zip(cols_header, headers):
            col.markdown(f"**{header_text}**")
        st.markdown("---")

        for jf in job_fairs:
            organizer = jf.get('organizer', {}) # Organizer is a nested dictionary
            organizer_name = organizer.get('name', 'N/A') if isinstance(organizer, dict) else 'N/A'
            
            row_cols = st.columns((0.5, 1.5, 1.5, 1.7, 1.2, 1.2, 0.8, 0.7, 0.5, 0.5, 1)) # Adjusted location column width
            row_cols[0].write(str(jf.get('id')))
            row_cols[1].write(jf.get('title', 'N/A'))
            row_cols[2].write(organizer_name)
            
            # Display formatted_address or location_query, and coordinates
            location_display_admin = jf.get('formatted_address') or jf.get('location_query') or jf.get('location', 'N/A')
            row_cols[3].write(location_display_admin)
            if jf.get('latitude') and jf.get('longitude'):
                row_cols[3].caption(f"Lat: {jf.get('latitude'):.4f}, Lon: {jf.get('longitude'):.4f}")
            
            row_cols[4].write(pd.to_datetime(jf.get('start_datetime')).strftime('%Y-%m-%d %H:%M') if jf.get('start_datetime') else 'N/A')
            row_cols[5].write(pd.to_datetime(jf.get('end_datetime')).strftime('%Y-%m-%d %H:%M') if jf.get('end_datetime') else 'N/A')
            row_cols[6].write(jf.get('status', 'N/A'))
            row_cols[7].write(str(jf.get('booths_count', 0)))

            job_fair_id = jf.get('id')
            job_fair_title = jf.get('title', 'N/A')

            if row_cols[8].button("✏️", key=f"edit_jf_{job_fair_id}", help="Edit Job Fair"):
                st.session_state.editing_job_fair_id = job_fair_id
                st.session_state.job_fair_data_for_edit = jf 
                st.session_state.confirm_delete_job_fair_id = None 
                st.session_state.selected_job_fair_id_for_booths = None # Clear booth management state
                st.rerun()

            if row_cols[9].button("🗑️", key=f"delete_jf_{job_fair_id}", help="Delete Job Fair"):
                st.session_state.confirm_delete_job_fair_id = job_fair_id
                st.session_state.editing_job_fair_id = None 
                st.session_state.selected_job_fair_id_for_booths = None # Clear booth management state
                st.rerun()
            
            if row_cols[10].button("Manage Booths", key=f"manage_booths_jf_{job_fair_id}", help="Manage Booths for this Job Fair"):
                st.session_state.selected_job_fair_id_for_booths = job_fair_id
                st.session_state.selected_job_fair_title_for_booths = job_fair_title
                st.session_state.editing_job_fair_id = None # Clear edit state
                st.session_state.confirm_delete_job_fair_id = None # Clear delete state
                # Optionally, switch to a dedicated "Manage Booths" tab if using tabs for this section
                # For now, it will display a new section below the job fair list / edit form.
                st.rerun()

            # Inline delete confirmation
            if st.session_state.confirm_delete_job_fair_id == job_fair_id:
                st.warning(f"Are you sure you want to delete Job Fair: '{jf.get('title', job_fair_id)}'? This action cannot be undone.")
                confirm_cols = st.columns([1,1,8])
                if confirm_cols[0].button("Yes, Delete", key=f"confirm_delete_jf_btn_{job_fair_id}"):
                    response, success, _ = make_api_request(f"{JOB_FAIRS_ENDPOINT}/{job_fair_id}", "DELETE", return_status_code=True)
                    if success:
                        st.session_state.success_message_jf_admin = f"Job Fair ID {job_fair_id} deleted successfully."
                    else:
                        error_detail = response.get('error', 'Failed to delete job fair.')
                        st.session_state.error_message_jf_admin = f"Error deleting Job Fair ID {job_fair_id}: {error_detail}"
                    st.session_state.confirm_delete_job_fair_id = None
                    st.rerun()
                if confirm_cols[1].button("Cancel", key=f"cancel_delete_jf_btn_{job_fair_id}"):
                    st.session_state.confirm_delete_job_fair_id = None
                    st.rerun()
            st.markdown("---") # Separator for each job fair entry
        
        # Remove old dataframe display and TODO
        # st.dataframe(df_display, use_container_width=True, hide_index=True)
        # st.info("Full Edit/Delete functionality will be added in a future update for this table.")
        # TODO: Add action buttons for edit/delete for each row.
        # For now, users would use API tools or database directly if urgent.

with tab_create:
    st.subheader("Add New Job Fair")
    
    organizers = fetch_organizers()
    organizer_options = {org['id']: f"{org['name']} ({org['email']})" for org in organizers}

    with st.form("new_job_fair_form_admin", clear_on_submit=True):
        nf_title = st.text_input("Job Fair Title*", help="e.g., Annual Tech Career Fair 2025")
        # Corrected usage of organizer_options for st.selectbox
        nf_organizer_id = st.selectbox(
            "Organizer*", 
            options=list(organizer_options.keys()), 
            format_func=lambda x: organizer_options[x],
            help="Select the organizing entity. Admins can assign to any organizer."
        )
        nf_description = st.text_area("Description", help="Provide details about the job fair.")
        nf_location = st.text_input("Location* (e.g., 'City Convention Center')", key="admin_nf_location", help="Provide a textual address for geocoding if coordinates are not entered.")
        
        col_lat_nf_admin, col_lon_nf_admin = st.columns(2)
        with col_lat_nf_admin:
            nf_latitude_admin = st.number_input("Latitude (Optional)", key="admin_nf_latitude", value=None, placeholder="e.g., 40.7128", format="%.6f", help="Enter if you know the exact latitude. Overrides geocoding if both lat/lon are set.")
        with col_lon_nf_admin:
            nf_longitude_admin = st.number_input("Longitude (Optional)", key="admin_nf_longitude", value=None, placeholder="e.g., -74.0060", format="%.6f", help="Enter if you know the exact longitude. Overrides geocoding if both lat/lon are set.")

        c1, c2 = st.columns(2)
        with c1:
            nf_start_datetime_date = st.date_input("Start Date*", value=datetime.now() + timedelta(days=7))
            nf_start_datetime_time = st.time_input("Start Time*", value=datetime.strptime("09:00", "%H:%M").time())
        with c2:
            nf_end_datetime_date = st.date_input("End Date*", value=datetime.now() + timedelta(days=7))
            nf_end_datetime_time = st.time_input("End Time*", value=datetime.strptime("17:00", "%H:%M").time())

        # Align status options with backend (draft, active, archived)
        nf_status = st.selectbox("Initial Status*", options=['draft', 'active', 'archived'], index=0, help="Set the initial status of the job fair.")
        nf_map_image = st.file_uploader("Upload Job Fair Map (Optional)", type=['png', 'jpg', 'jpeg', 'gif'])

        nf_submitted = st.form_submit_button("Create Job Fair")

        if nf_submitted:
            if not nf_title or not nf_organizer_id:
                st.warning("Title and Organizer are required.")
            elif (nf_latitude_admin is None and nf_longitude_admin is not None) or \
                 (nf_latitude_admin is not None and nf_longitude_admin is None):
                st.warning("If providing coordinates, both Latitude and Longitude are required.")
            elif not nf_location and (nf_latitude_admin is None or nf_longitude_admin is None):
                st.warning("Please provide a Location address OR both Latitude and Longitude.")
            else:
                start_datetime_combined = datetime.combine(nf_start_datetime_date, nf_start_datetime_time)
                end_datetime_combined = datetime.combine(nf_end_datetime_date, nf_end_datetime_time)

                if end_datetime_combined <= start_datetime_combined:
                    st.error("End date/time must be after start date/time.")
                else:
                    payload = {
                        'title': nf_title,
                        'organizer_id': nf_organizer_id,
                        'description': nf_description,
                        'start_datetime': start_datetime_combined.isoformat(),
                        'end_datetime': end_datetime_combined.isoformat(),
                        'status': nf_status,
                    }
                    
                    # Add location or coordinates to payload
                    if nf_latitude_admin is not None and nf_longitude_admin is not None:
                        payload['latitude'] = nf_latitude_admin
                        payload['longitude'] = nf_longitude_admin
                        if nf_location: # If user also provided text, send it as location_query
                            payload['location'] = nf_location
                    elif nf_location:
                        payload['location'] = nf_location

                    files_payload = {}
                    if nf_map_image:
                        files_payload['map_image'] = (nf_map_image.name, nf_map_image, nf_map_image.type)

                    response, success, status_code = make_api_request(
                        JOB_FAIRS_ENDPOINT, 
                        "POST", 
                        data=payload,
                        files=files_payload if files_payload else {},
                        return_status_code=True
                    )

                    if success and status_code == 201:
                        created_fair_data_admin = response.get('data', {}) if response else {}
                        st.session_state.success_message_jf_admin = f"Job Fair '{created_fair_data_admin.get('title', nf_title)}' created successfully."
                        # Display geocoded information
                        if created_fair_data_admin.get('formatted_address'):
                            st.info(f"**Geocoded Location Details:**")
                            st.markdown(f"- **Formatted Address:** {created_fair_data_admin.get('formatted_address')}")
                            st.markdown(f"- **Latitude:** {created_fair_data_admin.get('latitude')}")
                            st.markdown(f"- **Longitude:** {created_fair_data_admin.get('longitude')}")
                            if created_fair_data_admin.get('location_query') and created_fair_data_admin.get('location_query') != created_fair_data_admin.get('formatted_address'):
                                st.caption(f"(Original query: {created_fair_data_admin.get('location_query')})")
                        elif created_fair_data_admin.get('location') and not (created_fair_data_admin.get('latitude') and created_fair_data_admin.get('longitude')):
                            st.warning("Location text was saved, but no coordinates were returned by the backend. Please verify the address or provide coordinates directly.")
                        elif created_fair_data_admin.get('latitude') and created_fair_data_admin.get('longitude') and not created_fair_data_admin.get('formatted_address'):
                             st.info("Coordinates saved. Formatted address was not returned (this may happen if location text was not provided for reverse geocoding).")
                        st.rerun()
                    else:
                        handle_api_error(response, "Failed to create job fair.")

st.markdown("---")
st.caption("Admin Job Fair Management - Resume Analyzer System")

# --- Edit Job Fair Form (will be shown below the tabs if editing_job_fair_id is set) ---
if st.session_state.editing_job_fair_id:
    job_fair_to_edit = st.session_state.job_fair_data_for_edit
    if not job_fair_to_edit or job_fair_to_edit.get('id') != st.session_state.editing_job_fair_id:
        # Refetch if data is not in session or mismatched
        fetched_fairs = fetch_job_fairs()
        job_fair_to_edit = next((jf for jf in fetched_fairs if jf['id'] == st.session_state.editing_job_fair_id), None)
        if job_fair_to_edit:
            st.session_state.job_fair_data_for_edit = job_fair_to_edit
        else:
            st.error(f"Could not load job fair data for ID: {st.session_state.editing_job_fair_id}")
            st.session_state.editing_job_fair_id = None # Clear to prevent loop
            st.rerun()
    
    if job_fair_to_edit: # Proceed if data is available
        st.divider()
        st.subheader(f"Edit Job Fair: {job_fair_to_edit.get('title', '')}")
        with st.form(key=f"edit_job_fair_form_admin_{job_fair_to_edit.get('id')}"):
            edit_title = st.text_input("Title*", value=job_fair_to_edit.get('title', ''))
            
            # Organizer selection for edit
            organizers_edit = fetch_organizers() # Fetch fresh list for edit form
            organizer_options_edit = {org['id']: f"{org['name']} ({org['email']})" for org in organizers_edit}
            current_organizer_id = job_fair_to_edit.get('organizer_id')
            # Get index of current organizer for selectbox default
            organizer_ids_list = list(organizer_options_edit.keys())
            current_organizer_index = organizer_ids_list.index(current_organizer_id) if current_organizer_id in organizer_ids_list else 0
            edit_organizer_id = st.selectbox("Organizer*", options=organizer_ids_list, format_func=lambda x: organizer_options_edit[x], index=current_organizer_index)
            
            edit_description = st.text_area("Description", value=job_fair_to_edit.get('description', ''))

            # Use location_query for the text input if available, otherwise fallback to location or formatted_address
            current_location_text_admin_edit = job_fair_to_edit.get('location_query', job_fair_to_edit.get('location', ''))
            edit_location_admin = st.text_input(
                "Location (Textual Address)", 
                value=current_location_text_admin_edit, 
                key=f"admin_edit_location_text_{job_fair_to_edit.get('id')}",
                help="Update textual address. This will be geocoded if coordinates are not entered or to re-geocode."
            )
            
            col_lat_edit_admin, col_lon_edit_admin = st.columns(2)
            with col_lat_edit_admin:
                edit_latitude_admin = st.number_input("Latitude (Optional)", value=job_fair_to_edit.get('latitude'), placeholder="e.g., 40.7128", format="%.6f", key=f"admin_edit_latitude_{job_fair_to_edit.get('id')}", help="Enter/Update exact latitude. Overrides geocoding if both lat/lon are set.")
            with col_lon_edit_admin:
                edit_longitude_admin = st.number_input("Longitude (Optional)", value=job_fair_to_edit.get('longitude'), placeholder="e.g., -74.0060", format="%.6f", key=f"admin_edit_longitude_{job_fair_to_edit.get('id')}", help="Enter/Update exact longitude. Overrides geocoding if both lat/lon are set.")

            # Display current formatted address and/or coordinates for reference
            if job_fair_to_edit.get('formatted_address'):
                st.caption(f"Currently geocoded as: {job_fair_to_edit.get('formatted_address')}")
            elif job_fair_to_edit.get('latitude') and job_fair_to_edit.get('longitude'):
                st.caption(f"Current coordinates: Lat: {job_fair_to_edit.get('latitude')}, Lon: {job_fair_to_edit.get('longitude')}")            # Date and Time inputs
            # Safely parse datetimes, provide defaults if parsing fails
            try:
                start_datetime_str = job_fair_to_edit.get('start_datetime')
                end_datetime_str = job_fair_to_edit.get('end_datetime')
                if start_datetime_str:
                    current_start_datetime_obj = pd.to_datetime(start_datetime_str).to_pydatetime()
                else:
                    current_start_datetime_obj = datetime.now()
                if end_datetime_str:
                    current_end_datetime_obj = pd.to_datetime(end_datetime_str).to_pydatetime()
                else:
                    current_end_datetime_obj = datetime.now() + timedelta(days=1)
            except Exception:
                current_start_datetime_obj = datetime.now()
                current_end_datetime_obj = datetime.now() + timedelta(days=1)

            ec1, ec2 = st.columns(2)
            with ec1:
                edit_start_datetime_date = st.date_input("Start Date*", value=current_start_datetime_obj.date())
                edit_start_datetime_time = st.time_input("Start Time*", value=current_start_datetime_obj.time())
            with ec2:
                edit_end_datetime_date = st.date_input("End Date*", value=current_end_datetime_obj.date())
                edit_end_datetime_time = st.time_input("End Time*", value=current_end_datetime_obj.time())
            
            # Status options for Admin - should match backend JobFairController status enum if different from Organizer
            admin_status_options = ['draft', 'active', 'archived', 'published', 'completed', 'cancelled']
            current_status_admin = job_fair_to_edit.get('status', 'draft')
            edit_status_admin_index = admin_status_options.index(current_status_admin) if current_status_admin in admin_status_options else 0
            edit_status = st.selectbox("Status*", options=admin_status_options, index=edit_status_admin_index)

            st.markdown("**Current Map Image:**")
            if job_fair_to_edit.get('map_image_url'):
                st.image(job_fair_to_edit['map_image_url'], width=200)
                if st.checkbox("Remove current map image?", key=f"remove_map_image_checkbox_admin_{job_fair_to_edit.get('id')}"):
                    st.session_state[f"remove_map_flag_admin_edit_{job_fair_to_edit.get('id')}"] = True
                else:
                    st.session_state[f"remove_map_flag_admin_edit_{job_fair_to_edit.get('id')}"] = False
            else:
                st.caption("No map image uploaded.")
            
            edit_map_image = st.file_uploader("Upload New Map (Optional, will replace existing)", type=['png', 'jpg', 'jpeg', 'gif'])
            
            col_update_buttons_admin = st.columns(2)
            with col_update_buttons_admin[0]:
                update_submitted_admin = st.form_submit_button("Save Changes")
            with col_update_buttons_admin[1]:
                if st.form_submit_button("Cancel Edit", type="secondary"):
                    st.session_state.editing_job_fair_id = None
                    st.rerun()

            if update_submitted_admin:
                if not edit_title or not edit_organizer_id:
                    st.warning("Title and Organizer are required.")
                elif (edit_latitude_admin is None and edit_longitude_admin is not None) or \
                     (edit_latitude_admin is not None and edit_longitude_admin is None):
                    st.warning("If providing coordinates, both Latitude and Longitude are required.")
                elif not edit_location_admin and (edit_latitude_admin is None or edit_longitude_admin is None) and not (job_fair_to_edit.get('latitude') and job_fair_to_edit.get('longitude')):
                     st.warning("Please provide a Location address OR both Latitude and Longitude if clearing a previously set location.")    
                else:
                    start_datetime_combined_edit = datetime.combine(edit_start_datetime_date, edit_start_datetime_time)
                    end_datetime_combined_edit = datetime.combine(edit_end_datetime_date, edit_end_datetime_time)

                    if end_datetime_combined_edit <= start_datetime_combined_edit:
                        st.error("End date/time must be after start date/time.")
                    else:
                        payload_edit = {
                            'title': edit_title,
                            'organizer_id': edit_organizer_id,
                            'description': edit_description,
                            'start_datetime': start_datetime_combined_edit.isoformat(),
                            'end_datetime': end_datetime_combined_edit.isoformat(),
                            'status': edit_status,
                        }

                        # Handle location and coordinates for update
                        if edit_latitude_admin is not None and edit_longitude_admin is not None:
                            payload_edit['latitude'] = edit_latitude_admin
                            payload_edit['longitude'] = edit_longitude_admin
                            if edit_location_admin: 
                                payload_edit['location'] = edit_location_admin
                            elif 'location' in payload_edit: # remove if not provided but lat/lon are
                                 del payload_edit['location'] 
                        elif edit_location_admin: # Only location text provided/updated
                            payload_edit['location'] = edit_location_admin
                        elif not edit_location_admin and (edit_latitude_admin is None and edit_longitude_admin is None):
                            payload_edit['location'] = "" # Send empty string to signify clearing
                            payload_edit['latitude'] = None
                            payload_edit['longitude'] = None

                        files_payload_edit = {}
                        if edit_map_image:
                            files_payload_edit['map_image'] = (edit_map_image.name, edit_map_image, edit_map_image.type)
                        elif st.session_state.get(f"remove_map_flag_admin_edit_{job_fair_to_edit.get('id')}", False):
                            payload_edit['map_image'] = "" # Signal to backend to remove current image

                        response_edit, success_edit, status_code_edit = make_api_request(f"{JOB_FAIRS_ENDPOINT}/{job_fair_to_edit.get('id')}", "PUT", data=payload_edit, files=files_payload_edit, return_status_code=True)

                        if success_edit and status_code_edit == 200:
                            updated_fair_data_admin = response_edit.get('data', {}) if response_edit else {}
                            st.session_state.success_message_jf_admin = f"Job Fair '{updated_fair_data_admin.get('title', edit_title)}' updated successfully."
                            # Display geocoded information update
                            if updated_fair_data_admin.get('formatted_address'):
                                st.info(f"**Updated Geocoded Location:**")
                                st.markdown(f"- **Formatted Address:** {updated_fair_data_admin.get('formatted_address')}")
                                st.markdown(f"- **Latitude:** {updated_fair_data_admin.get('latitude')}")
                                st.markdown(f"- **Longitude:** {updated_fair_data_admin.get('longitude')}")
                                if updated_fair_data_admin.get('location_query') and updated_fair_data_admin.get('location_query') != updated_fair_data_admin.get('formatted_address'):
                                    st.caption(f"(Original query: {updated_fair_data_admin.get('location_query')})")
                            elif updated_fair_data_admin.get('location') and not (updated_fair_data_admin.get('latitude') and updated_fair_data_admin.get('longitude')):
                                st.warning("Location text was updated, but no coordinates were returned by the backend. Verify or provide coordinates.")
                            elif updated_fair_data_admin.get('latitude') and updated_fair_data_admin.get('longitude') and not updated_fair_data_admin.get('formatted_address'):
                                st.info("Coordinates updated. Formatted address was not returned (may occur if location text was not provided/updated for reverse geocoding).")

                            st.session_state.editing_job_fair_id = None
                            st.session_state.job_fair_data_for_edit = {}
                            if f"remove_map_flag_admin_edit_{job_fair_to_edit.get('id')}" in st.session_state:
                                del st.session_state[f"remove_map_flag_admin_edit_{job_fair_to_edit.get('id')}"]
                            st.rerun()

# --- Manage Booths Section (New) ---
if st.session_state.selected_job_fair_id_for_booths:
    st.divider()
    st.subheader(f"Manage Booths for: {st.session_state.selected_job_fair_title_for_booths} (Job Fair ID: {st.session_state.selected_job_fair_id_for_booths})")

    job_fair_id_for_booths = st.session_state.selected_job_fair_id_for_booths    # --- Helper function to fetch booths for the current job fair ---
    def fetch_booths_for_job_fair(jf_id):
        endpoint = f"admin/job-fairs/{jf_id}/booths"
        response, success = make_api_request(endpoint, "GET")
        if success:
            return response.get('data', []) if isinstance(response, dict) else []
        else:
            handle_api_error(response, f"Failed to fetch booths for Job Fair ID {jf_id}.")
            return []

    # Display success/error messages for booth CRUD
    if st.session_state.success_message_booth_admin:
        st.success(st.session_state.success_message_booth_admin)
        st.session_state.success_message_booth_admin = None 
    if st.session_state.error_message_booth_admin:
        st.error(st.session_state.error_message_booth_admin)
        st.session_state.error_message_booth_admin = None

    # --- Display existing booths for the job fair ---
    st.markdown("#### Existing Booths")
    if st.button("🔄 Refresh Booths List", key="refresh_booths_list_admin"):
        st.rerun()
    
    booths_list = fetch_booths_for_job_fair(job_fair_id_for_booths)

    if not booths_list:
        st.info("No booths found for this job fair. Add one below.")
    else:
        booth_cols_header = st.columns((0.5, 2, 1, 0.5, 0.5, 1)) # ID, Company, Booth #, Edit, Del, Openings
        booth_headers = ['ID', 'Company Name', 'Booth Number', 'Edit', 'Del', 'Job Openings']
        for col, header_text in zip(booth_cols_header, booth_headers):
            col.markdown(f"**{header_text}**")
        st.markdown("---")

        for booth in booths_list:
            b_row_cols = st.columns((0.5, 2, 1, 0.5, 0.5, 1))
            b_row_cols[0].write(str(booth.get('id')))
            b_row_cols[1].write(booth.get('company_name', 'N/A'))
            b_row_cols[2].write(str(booth.get('booth_number_on_map', 'N/A')))
            
            booth_id = booth.get('id')
            if b_row_cols[3].button("✏️", key=f"edit_booth_{booth_id}", help="Edit Booth"):
                st.session_state.editing_booth_id = booth_id
                st.session_state.booth_data_for_edit = booth
                st.session_state.confirm_delete_booth_id = None
                st.rerun()

            if b_row_cols[4].button("🗑️", key=f"delete_booth_{booth_id}", help="Delete Booth"):
                st.session_state.confirm_delete_booth_id = booth_id
                st.session_state.editing_booth_id = None
                st.rerun()
            
            b_row_cols[5].button("Manage Openings", key=f"manage_openings_booth_{booth_id}", help="Manage Job Openings for this Booth (Not Implemented Yet)", disabled=True)

            # Inline delete confirmation for booths
            if st.session_state.confirm_delete_booth_id == booth_id:
                st.warning(f"Delete Booth: '{booth.get('company_name', booth_id)}'? This may also delete associated job openings.")
                b_confirm_cols = st.columns([1,1,8])
                if b_confirm_cols[0].button("Yes, Delete Booth", key=f"confirm_del_booth_btn_{booth_id}"):
                    del_response, del_success = make_api_request(f"admin/booths/{booth_id}", "DELETE")
                    if del_success:
                        st.session_state.success_message_booth_admin = f"Booth ID {booth_id} deleted."
                    else:
                        err_detail = del_response.get('error', 'Failed to delete booth.')
                        st.session_state.error_message_booth_admin = f"Error deleting Booth {booth_id}: {err_detail}"
                    st.session_state.confirm_delete_booth_id = None
                    st.rerun()
                if b_confirm_cols[1].button("Cancel Delete", key=f"cancel_del_booth_btn_{booth_id}"):
                    st.session_state.confirm_delete_booth_id = None
                    st.rerun()
            st.markdown("---")
    
    st.markdown("---    ")
    # --- Add New Booth Form ---
    if not st.session_state.editing_booth_id: # Only show add form if not editing a booth
        st.markdown("#### Add New Booth")
        with st.form("new_booth_for_job_fair_form_admin", clear_on_submit=True):
            nb_company_name = st.text_input("Company Name*", help="e.g., Tech Solutions Inc.")
            nb_booth_number = st.number_input("Booth Number on Map*", min_value=1, max_value=1000, step=1, help="Numeric identifier on the map, e.g., 1, 2, ...30")
            # map_coordinates could be added later if a map interface is built for placing booths
            
            nb_submitted = st.form_submit_button("Add Booth")

            if nb_submitted:
                if not nb_company_name or not nb_booth_number:
                    st.warning("Company Name and Booth Number are required.")
                else:
                    payload = {
                        'company_name': nb_company_name,
                        'booth_number_on_map': nb_booth_number,
                        # 'map_coordinates': json.loads(nb_map_coordinates) if nb_map_coordinates else None # Example if using JSON input
                    }
                    add_booth_endpoint = f"admin/job-fairs/{job_fair_id_for_booths}/booths"
                    response, success = make_api_request(add_booth_endpoint, "POST", data=payload)

                    if success:
                        st.session_state.success_message_booth_admin = f"Booth '{nb_company_name}' added successfully."
                        st.rerun()
                    else:
                        error_detail = response.get('error', response.get('message', 'Failed to add booth.'))
                        if 'errors' in response: error_detail = response['errors']
                        st.session_state.error_message_booth_admin = f"Error adding booth: {error_detail}"
                        st.rerun() # Rerun to show the error and persist form data

    # --- Edit Booth Form (Placeholder/Initial Setup) ---
    if st.session_state.editing_booth_id and st.session_state.booth_data_for_edit:
        st.divider()
        edit_booth_data = st.session_state.booth_data_for_edit
        st.markdown(f"#### Edit Booth: {edit_booth_data.get('company_name', '')} (ID: {st.session_state.editing_booth_id})")

        with st.form("edit_booth_form_admin", clear_on_submit=False):
            edit_b_company_name = st.text_input("Company Name*", value=edit_booth_data.get('company_name', ''))
            edit_b_booth_number = st.number_input("Booth Number on Map*", min_value=1, max_value=1000, step=1, value=int(edit_booth_data.get('booth_number_on_map', 1)))
            # edit_b_map_coordinates = st.text_input("Map Coordinates (JSON, Optional)", value=json.dumps(edit_booth_data.get('map_coordinates')) if edit_booth_data.get('map_coordinates') else "")

            col_save_booth, col_cancel_booth_edit, _ = st.columns([1,1,3])
            with col_save_booth:
                edit_b_submitted = st.form_submit_button("Save Booth Changes")
            with col_cancel_booth_edit:
                if st.form_submit_button("Cancel Edit Booth"):
                    st.session_state.editing_booth_id = None
                    st.session_state.booth_data_for_edit = {}
                    st.rerun()
            
            if edit_b_submitted:
                if not edit_b_company_name or not edit_b_booth_number:
                    st.error("Company Name and Booth Number are required for editing.")
                else:
                    update_payload = {
                        'company_name': edit_b_company_name,
                        'booth_number_on_map': edit_b_booth_number,
                        # 'map_coordinates': json.loads(edit_b_map_coordinates) if edit_b_map_coordinates else None
                    }
                    update_booth_endpoint = f"admin/booths/{st.session_state.editing_booth_id}"
                    response, success = make_api_request(update_booth_endpoint, "PUT", data=update_payload)

                    if success:
                        st.session_state.success_message_booth_admin = f"Booth ID {st.session_state.editing_booth_id} updated."
                        st.session_state.editing_booth_id = None
                        st.session_state.booth_data_for_edit = {}
                        st.rerun()
                    else:
                        error_detail = response.get('error', response.get('message', 'Update failed.'))
                        if 'errors' in response: error_detail = response['errors']
                        st.session_state.error_message_booth_admin = f"Error updating booth {st.session_state.editing_booth_id}: {error_detail}"
                        st.rerun() # Rerun to display error and keep form open

    st.markdown("---    ")
    if st.button("← Back to Job Fair List", key="back_to_jf_list_from_booths_bottom"):
        st.session_state.selected_job_fair_id_for_booths = None
        st.session_state.selected_job_fair_title_for_booths = None
        st.session_state.editing_booth_id = None # Clear booth edit state too
        st.session_state.confirm_delete_booth_id = None # Clear booth delete state
        st.rerun()

# Removed the old placeholder comment
# # Further CRUD operations (Edit, Delete) for job fairs will be implemented here.

# Further CRUD operations (Edit, Delete) for job fairs will be implemented here. 