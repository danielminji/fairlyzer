import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import json
from lib.ui import display_navbar
import os

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

# Assuming lib.api.login_user is the preferred way to login as it handles CSRF
# If lib.api is not structured to be easily called from here, we might need adjustment
# For now, let's assume we can import it or we adapt the direct call.
# from ..lib.api import login_user # This relative import might not work directly in pages
# We'll stick to direct requests.post for now and ensure variables match api.py expectations

# Configuration for the Laravel API
API_BASE_URL = os.environ.get('FAIRLYZER_API_BASE_URL', 'http://localhost:8000/api') # Make sure this matches your Laravel dev server
LOGIN_URL = f"{API_BASE_URL}/login"
# USER_URL = f"{API_BASE_URL}/user" # Not used directly in this simplified version
ORGANIZER_JOB_FAIRS_URL = f"{API_BASE_URL}/organizer/job-fairs"

st.set_page_config(layout="wide", page_title="Organizer: Job Fair Management")

# --- Navigation Handler (checks on rerun) ---
if st.session_state.get('navigate_to_booth_management'): # Check only the navigation flag
    st.write(f"DEBUG (05_Organizer_Job_Fairs.py): About to switch. Booth Management Job Fair ID in session: {st.session_state.get('booth_management_job_fair_id')}") # DEBUG
    # Clear only the navigation flag, the target page will use/clear the job_fair_id from session_state
    del st.session_state.navigate_to_booth_management 
    st.switch_page("pages/06_Organizer_Booth_Management.py")

st.title("Organizer Dashboard: Job Fair Management")

# --- Authentication ---
def handle_organizer_login(email, password):
    try:
        # Ideally, use the login_user function from lib/api.py if it handles CSRF etc.
        # For this focused change, direct POST and manual session var setting:
        response = requests.post(LOGIN_URL, data={'email': email, 'password': password})
        response.raise_for_status()
        data = response.json()
        if 'token' in data and 'user' in data:
            if data['user'].get('role') == 'organizer': # Ensure they are an organizer
                st.session_state.user_token = data['token'] # Key used by lib/api.py
                st.session_state.current_user = data['user'] # Storing the whole user object
                st.session_state.user_id = data['user']['id']
                st.session_state.user_role = data['user']['role']
                st.session_state.user_name = data['user']['name']
                st.session_state.authenticated = True
                st.success("Logged in successfully as Organizer!")
                st.rerun()
            else:
                st.error("Login successful, but you are not an approved organizer.")
        else:
            st.error("Login failed: Token or user data not found in response.")
            if 'message' in data:
                st.error(f"Message: {data['message']}")
    except requests.exceptions.HTTPError as e:
        st.error(f"Login failed: {e.response.status_code} - {e.response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Login request failed: {e}")

def handle_organizer_logout():
    # Clear all potentially set session variables related to user auth
    for key in ['user_token', 'current_user', 'user_id', 'user_role', 'user_name', 'authenticated', 'navigate_to_booth_management', 'booth_management_job_fair_id']:
        if key in st.session_state:
            del st.session_state[key]
    st.success("Logged out.")
    st.switch_page("app.py") # Navigate to the main app/login page
    st.rerun() # May not be strictly necessary after switch_page but good practice

# --- API Helper Functions (with auth) ---
def get_organizer_auth_headers(): # Renamed to be specific
    if 'user_token' not in st.session_state:
        return None
    return {'Authorization': f"Bearer {st.session_state.user_token}", 'Accept': 'application/json'}

def fetch_job_fairs():
    headers = get_organizer_auth_headers()
    if not headers:
        # Check if it's because the role is wrong, though this page should only be shown if authenticated as organizer
        if st.session_state.get('authenticated') and st.session_state.get('user_role') != 'organizer':
             st.warning("You are not logged in as an organizer.")
             return []
        return [] # Not authenticated
    try:
        response = requests.get(ORGANIZER_JOB_FAIRS_URL, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            st.error("Session expired or unauthorized. Please log in again.")
            handle_organizer_logout()
        elif e.response.status_code == 403: # Forbidden, likely not an organizer
            st.error("You do not have permission to access these resources. Ensure you are an approved organizer.")
            # Optionally logout if it implies a role mismatch that shouldn't have reached here
        else:
            st.error(f"Failed to fetch job fairs: {e.response.status_code} - {e.response.text}")
        return []
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
        return []

# --- Main Page Logic ---
if not st.session_state.get('authenticated') or st.session_state.get('user_role') != 'organizer':
    st.warning("You must be logged in as an organizer to access this page.")
    if st.button("Go to Login Page"):
        st.session_state.view = "login"
        st.switch_page("app.py")
    st.stop()
else:
    display_navbar()

    if 'selected_job_fair_id_for_actions' not in st.session_state: # Renamed for clarity
        st.session_state.selected_job_fair_id_for_actions = None

    # --- Create New Job Fair Section (Moved to the top) ---
    st.header("Create New Job Fair") # Changed from subheader for better hierarchy
    with st.expander("Add a New Job Fair", expanded=True): # expanded=True by default, or keep as False
        with st.form("new_job_fair_form", clear_on_submit=True):
            nf_title = st.text_input("Title", key="nf_title")
            nf_description = st.text_area("Description", key="nf_description")
            col1_nf, col2_nf = st.columns(2)
            with col1_nf:
                nf_start_date = st.date_input("Start Date", key="nf_start_date_v2", value=datetime.today())
                nf_start_time = st.time_input("Start Time", key="nf_start_time_v2")
            with col2_nf:
                nf_end_date = st.date_input("End Date", key="nf_end_date_v2", value=datetime.today() + pd.Timedelta(days=1))
                nf_end_time = st.time_input("End Time", key="nf_end_time_v2")
            nf_location = st.text_input("Location (e.g., '123 Main St, City, Country' or 'Venue Name, City')", key="nf_location", help="Provide a textual address for geocoding if coordinates are not entered.")
            
            col_lat_nf, col_lon_nf = st.columns(2)
            with col_lat_nf:
                nf_latitude = st.number_input("Latitude (Optional)", key="nf_latitude", value=None, placeholder="e.g., 40.7128", format="%.6f", help="Enter if you know the exact latitude. Overrides geocoding if both lat/lon are set.")
            with col_lon_nf:
                nf_longitude = st.number_input("Longitude (Optional)", key="nf_longitude", value=None, placeholder="e.g., -74.0060", format="%.6f", help="Enter if you know the exact longitude. Overrides geocoding if both lat/lon are set.")

            nf_map_image = st.file_uploader("Upload Job Fair Map (PNG, JPG)", type=["png", "jpg", "jpeg"], key="nf_map_image")
            nf_status = st.selectbox("Status", options=["draft", "active", "archived"], index=0, key="nf_status")
            nf_submitted = st.form_submit_button("Create Job Fair")
            if nf_submitted:
                if not nf_title or not nf_start_date or not nf_end_date or not nf_start_time or not nf_end_time:
                    st.warning("Title, Start/End Dates, and Start/End Times are required.")
                elif (nf_latitude is None and nf_longitude is not None) or (nf_latitude is not None and nf_longitude is None):
                    st.warning("If providing coordinates, both Latitude and Longitude are required.")
                elif not nf_location and (nf_latitude is None or nf_longitude is None):
                    st.warning("Please provide a Location address OR both Latitude and Longitude.")
                elif datetime.combine(nf_start_date, nf_start_time) >= datetime.combine(nf_end_date, nf_end_time):
                    st.warning("End date/time must be after start date/time.")
                else:
                    headers_nf = get_organizer_auth_headers()
                    if headers_nf:
                        start_dt_nf = datetime.combine(nf_start_date, nf_start_time)
                        end_dt_nf = datetime.combine(nf_end_date, nf_end_time)
                        payload_nf = {
                            'title': nf_title,
                            'description': nf_description,
                            'start_datetime': start_dt_nf.isoformat(),
                            'end_datetime': end_dt_nf.isoformat(),
                            'status': nf_status
                        }
                        # Add location or coordinates to payload
                        if nf_latitude is not None and nf_longitude is not None:
                            payload_nf['latitude'] = nf_latitude
                            payload_nf['longitude'] = nf_longitude
                            if nf_location: # If user also provided text, send it as location_query
                                payload_nf['location'] = nf_location
                        elif nf_location:
                             payload_nf['location'] = nf_location
                        
                        files_nf = {} if nf_map_image is None else {'map_image': (nf_map_image.name, nf_map_image, nf_map_image.type)}
                        try:
                            response = requests.post(ORGANIZER_JOB_FAIRS_URL, headers=headers_nf, data=payload_nf, files=files_nf)
                            response.raise_for_status() # Check for HTTP errors
                            created_fair_data = response.json() # Get the created job fair data
                            st.success(f"Job Fair '{created_fair_data.get('title', nf_title)}' created successfully!")
                            
                            # Display geocoded information if available
                            if created_fair_data.get('formatted_address'):
                                st.info(f"**Geocoded Location:**")
                                st.markdown(f"- **Formatted Address:** {created_fair_data.get('formatted_address')}")
                                st.markdown(f"- **Latitude:** {created_fair_data.get('latitude')}")
                                st.markdown(f"- **Longitude:** {created_fair_data.get('longitude')}")
                                if created_fair_data.get('location_query') != created_fair_data.get('formatted_address'):
                                     st.caption(f"(Original query: {created_fair_data.get('location_query')})")                           
                            elif created_fair_data.get('location'):
                                st.warning("Location was saved, but could not be automatically geocoded. Please verify the address.")
                            
                            # Add a small delay or a button to clear/continue before rerun, so user can see the info
                            # For now, direct rerun to refresh the list.
                            st.session_state.new_fair_creation_details = created_fair_data # Store for potential display after rerun
                            st.rerun()
                        except requests.exceptions.HTTPError as e_nf_api:
                            error_message = f"Failed to create job fair: {e_nf_api}"
                            try:
                                error_detail = e_nf_api.response.json()
                                if "errors" in error_detail: # Laravel validation errors
                                    for field, messages in error_detail["errors"].items():
                                        for msg in messages:
                                            st.error(f"{field}: {msg}")
                                else:
                                     st.error(error_message + f" - {e_nf_api.response.text}")
                            except json.JSONDecodeError:
                                 st.error(error_message + f" - {e_nf_api.response.text}")
                        except Exception as e_nf_api: 
                            st.error(f"Failed to create job fair: {e_nf_api}")
                    else: st.error("Authentication error.") 
    st.markdown("---") # Separator

    st.header("Your Job Fairs")
    job_fairs_data = fetch_job_fairs()

    if job_fairs_data:
        df_job_fairs_list = pd.DataFrame(job_fairs_data)
        if 'start_datetime' in df_job_fairs_list.columns:
            df_job_fairs_list['start_datetime'] = pd.to_datetime(df_job_fairs_list['start_datetime']).dt.strftime('%Y-%m-%d %H:%M')
        if 'end_datetime' in df_job_fairs_list.columns:
            df_job_fairs_list['end_datetime'] = pd.to_datetime(df_job_fairs_list['end_datetime']).dt.strftime('%Y-%m-%d %H:%M')

        if not df_job_fairs_list.empty:
            st.subheader("Current Job Fairs List")
            for index, row_list_item in df_job_fairs_list.iterrows():
                job_fair_id_list = row_list_item['id']
                with st.container():
                    # Display job fair info
                    st.markdown(f"**{row_list_item['title']}** (ID: {job_fair_id_list})")
                    
                    # Display formatted address if available, else the original location query
                    display_location = row_list_item.get('formatted_address') if row_list_item.get('formatted_address') else row_list_item.get('location', 'N/A')
                    st.markdown(f"Status: {row_list_item.get('status', 'N/A')} | Location: {display_location}")
                    
                    st.markdown(f"Starts: {row_list_item.get('start_datetime', 'N/A')} | Ends: {row_list_item.get('end_datetime', 'N/A')}")
                    # Display geocoded lat/lon if available in the list (optional, for organizer's quick reference)
                    if row_list_item.get('latitude') and row_list_item.get('longitude'):
                        st.caption(f"Coordinates: Lat {row_list_item.get('latitude'):.4f}, Lon {row_list_item.get('longitude'):.4f}")

                API_BASE_URL = os.environ.get('FAIRLYZER_API_BASE_URL', 'http://localhost:8000/api')
                PUBLIC_BASE_URL = API_BASE_URL.replace('/api', '')
                map_filename = (
                    row_list_item.get('map_filename')
                    or row_list_item.get('map_image')
                    or (row_list_item.get('map_image_path').split('/')[-1] if row_list_item.get('map_image_path') else None)
                )
                map_view_key = f"view_map_{job_fair_id_list}"
                map_state_key = f"show_map_{job_fair_id_list}"
                if map_filename:
                    map_url = f"{PUBLIC_BASE_URL}/storage/job_fair_maps/{map_filename}"
                    if st.button("View Map", key=map_view_key):
                        st.session_state[map_state_key] = not st.session_state.get(map_state_key, False)
                        st.rerun()
                    if st.session_state.get(map_state_key, False):
                        st.image(map_url, caption="Job Fair Map", use_container_width=True)
                        try:
                            import requests
                            response = requests.get(map_url)
                            if response.status_code == 200:
                                st.download_button(
                                    label="Download Map",
                                    data=response.content,
                                    file_name=map_filename,
                                    mime="image/png" if map_filename.lower().endswith(".png") else "image/jpeg",
                                    key=f"download_map_{job_fair_id_list}"
                                )
                            else:
                                st.warning("Map file could not be fetched for download (HTTP error).")
                        except Exception as e:
                            st.warning(f"Map file could not be fetched for download: {e}")
                if not map_filename:
                    st.warning("Map file not found for view or download.")

                # Action buttons for each job fair
                cols_actions = st.columns(3) # Edit Fair, Delete Fair, Manage Booths
                with cols_actions[0]:
                    if st.button("Edit Fair ✏️", key=f"edit_jf_details_{job_fair_id_list}"):
                        st.session_state.selected_job_fair_id_for_actions = job_fair_id_list
                        st.rerun()
                with cols_actions[1]:
                    # The Manage Booths button will navigate using session state.
                    if st.button("Manage Booths 🎪", key=f"manage_booths_nav_{job_fair_id_list}"):
                        st.session_state.navigate_to_booth_management = True
                        st.session_state.booth_management_job_fair_id = job_fair_id_list
                        st.rerun() # Rerun to trigger navigation check at the top
                with cols_actions[2]:
                    if st.button("Delete Fair 🗑️", key=f"delete_jf_details_{job_fair_id_list}", type="secondary"):
                        st.session_state.selected_job_fair_id_for_actions = job_fair_id_list # Still select for delete confirmation

                st.markdown("---")
        else:
            st.info("You haven't created any job fairs yet.")
    else:
        st.info("You haven't created any job fairs yet or failed to load them.")

    # --- Edit Job Fair Section ---
    if st.session_state.selected_job_fair_id_for_actions and any(jf['id'] == st.session_state.selected_job_fair_id_for_actions for jf in job_fairs_data): # Check if job_fairs_data is not empty
        selected_job_fair_data = next((jf for jf in job_fairs_data if jf['id'] == st.session_state.selected_job_fair_id_for_actions), None)
        
        if selected_job_fair_data:
            st.header(f"Edit Job Fair: {selected_job_fair_data['title']}")
            with st.form(f"edit_job_fair_form_{st.session_state.selected_job_fair_id_for_actions}"): # Unique key for the form
                current_start_dt = pd.to_datetime(selected_job_fair_data['start_datetime'])
                current_end_dt = pd.to_datetime(selected_job_fair_data['end_datetime'])

                edit_title = st.text_input("Title", value=selected_job_fair_data.get('title', ''), key=f"edit_title_{selected_job_fair_data['id']}")
                edit_description = st.text_area("Description", value=selected_job_fair_data.get('description', ''), key=f"edit_desc_{selected_job_fair_data['id']}")
                
                col1_edit, col2_edit = st.columns(2)
                with col1_edit:
                    edit_start_date = st.date_input("Start Date", value=current_start_dt.date(), key=f"edit_sdate_{selected_job_fair_data['id']}")
                    edit_start_time = st.time_input("Start Time", value=current_start_dt.time(), key=f"edit_stime_{selected_job_fair_data['id']}")
                with col2_edit:
                    edit_end_date = st.date_input("End Date", value=current_end_dt.date(), key=f"edit_edate_{selected_job_fair_data['id']}")
                    edit_end_time = st.time_input("End Time", value=current_end_dt.time(), key=f"edit_etime_{selected_job_fair_data['id']}")

                # Use location_query if available (it's the original text), otherwise fallback to location
                current_location_text = selected_job_fair_data.get('location_query', selected_job_fair_data.get('location', ''))
                edit_location = st.text_input("Location (Textual Address)", value=current_location_text, key=f"edit_loc_{selected_job_fair_data['id']}", help="Update textual address for geocoding if coordinates are not entered or to re-geocode.")

                col_lat_edit, col_lon_edit = st.columns(2)
                with col_lat_edit:
                    edit_latitude = st.number_input("Latitude (Optional)", value=selected_job_fair_data.get('latitude'), placeholder="e.g., 40.7128", format="%.6f", key=f"edit_lat_{selected_job_fair_data['id']}", help="Enter/Update exact latitude. Overrides geocoding if both lat/lon are set.")
                with col_lon_edit:
                    edit_longitude = st.number_input("Longitude (Optional)", value=selected_job_fair_data.get('longitude'), placeholder="e.g., -74.0060", format="%.6f", key=f"edit_lon_{selected_job_fair_data['id']}", help="Enter/Update exact longitude. Overrides geocoding if both lat/lon are set.")

                st.write("Current Map Image:")
                if selected_job_fair_data.get('map_image_path'):
                    # Construct the full URL correctly
                    # Remove '/api' from API_BASE_URL if it exists, then append the path
                    base_display_url = API_BASE_URL.replace("/api", "")
                    full_map_url = f"{base_display_url}{selected_job_fair_data['map_image_path']}"
                    if not selected_job_fair_data['map_image_path'].startswith('/storage'):
                         full_map_url = f"{base_display_url}/storage/{selected_job_fair_data['map_image_path'].lstrip('/')}"

                    st.image(full_map_url, width=200)
                    if st.checkbox("Remove current map image?", key=f"remove_map_{selected_job_fair_data['id']}"):
                        st.session_state[f"remove_map_flag_{selected_job_fair_data['id']}"] = True
                    else:
                        st.session_state[f"remove_map_flag_{selected_job_fair_data['id']}"] = False
                else:
                    st.caption("No map image uploaded.")

                edit_map_image = st.file_uploader("Upload New Map (Optional, will replace existing)", type=["png", "jpg", "jpeg"], key=f"edit_map_img_{selected_job_fair_data['id']}")
                
                current_status_options = ["draft", "active", "archived"] # Organizer specific statuses
                current_status_index = current_status_options.index(selected_job_fair_data.get('status', 'draft')) if selected_job_fair_data.get('status', 'draft') in current_status_options else 0
                edit_status = st.selectbox("Status", options=current_status_options, index=current_status_index, key=f"edit_status_{selected_job_fair_data['id']}")

                edit_submitted = st.form_submit_button("Update Job Fair")
                if edit_submitted:
                    if not edit_title or not edit_start_date or not edit_end_date or not edit_start_time or not edit_end_time :
                        st.warning("Title, Start/End Dates, and Start/End Times are required.")
                    elif (edit_latitude is None and edit_longitude is not None) or (edit_latitude is not None and edit_longitude is None):
                         st.warning("If providing coordinates, both Latitude and Longitude are required.")
                    elif not edit_location and (edit_latitude is None or edit_longitude is None):
                         st.warning("Please provide a Location address OR both Latitude and Longitude.")
                    elif datetime.combine(edit_start_date, edit_start_time) >= datetime.combine(edit_end_date, edit_end_time):
                        st.warning("End date/time must be after start date/time.")
                    else:
                        headers_edit = get_organizer_auth_headers()
                        if headers_edit:
                            start_dt_edit = datetime.combine(edit_start_date, edit_start_time)
                            end_dt_edit = datetime.combine(edit_end_date, edit_end_time)
                            payload_edit = {
                                '_method': 'PUT', # Important for Laravel to handle as PUT
                                'title': edit_title,
                                'description': edit_description,
                                'start_datetime': start_dt_edit.isoformat(),
                                'end_datetime': end_dt_edit.isoformat(),
                                'status': edit_status
                            }

                            # Add location or coordinates to payload
                            if edit_latitude is not None and edit_longitude is not None:
                                payload_edit['latitude'] = edit_latitude
                                payload_edit['longitude'] = edit_longitude
                                if edit_location: # If user also provided/kept text
                                    payload_edit['location'] = edit_location
                                elif not edit_location and 'location' in payload_edit: # remove if cleared and coords are set
                                    del payload_edit['location']

                            elif edit_location: # Only location text provided/updated
                                 payload_edit['location'] = edit_location
                            elif not edit_location and (edit_latitude is None and edit_longitude is None): # Location text cleared, and no coords
                                payload_edit['location'] = "" # Send empty string to signify clearing

                            files_edit = {}
                            if edit_map_image:
                                files_edit['map_image'] = (edit_map_image.name, edit_map_image, edit_map_image.type)
                            elif st.session_state.get(f"remove_map_flag_{selected_job_fair_data['id']}"):
                                payload_edit['map_image'] = "" # Send empty to signal removal if backend handles it this way

                            try:
                                update_url = f"{ORGANIZER_JOB_FAIRS_URL}/{selected_job_fair_data['id']}"
                                response = requests.post(update_url, headers=headers_edit, data=payload_edit, files=files_edit) # POST with _method=PUT
                                response.raise_for_status()
                                updated_fair_data = response.json()
                                st.success(f"Job Fair '{updated_fair_data.get('title', edit_title)}' updated successfully!")
                                
                                # Display geocoded information if available
                                if updated_fair_data.get('formatted_address'):
                                    st.info(f"**Updated Geocoded Location:**")
                                    st.markdown(f"- **Formatted Address:** {updated_fair_data.get('formatted_address')}")
                                    st.markdown(f"- **Latitude:** {updated_fair_data.get('latitude')}")
                                    st.markdown(f"- **Longitude:** {updated_fair_data.get('longitude')}")
                                    if updated_fair_data.get('location_query') != updated_fair_data.get('formatted_address'):
                                         st.caption(f"(Original query: {updated_fair_data.get('location_query')})")                           
                                elif updated_fair_data.get('location'):
                                    st.warning("Location was updated, but could not be automatically geocoded. Please verify the address.")

                                st.session_state.selected_job_fair_id_for_actions = None # Clear selection
                                if f'remove_map_image_ef_{selected_job_fair_data["id"]}' in st.session_state:
                                    del st.session_state[f'remove_map_image_ef_{selected_job_fair_data["id"]}'] # Clean up session state
                                st.rerun()
                            except requests.exceptions.HTTPError as e_upd_act_api:
                                error_message = f"Failed to update job fair: {e_upd_act_api}"
                                try:
                                    error_detail = e_upd_act_api.response.json()
                                    if "errors" in error_detail: # Laravel validation errors
                                        for field, messages in error_detail["errors"].items():
                                            for msg in messages:
                                                st.error(f"{field}: {msg}")
                                    else:
                                         st.error(error_message + f" - {e_upd_act_api.response.text}")
                                except json.JSONDecodeError:
                                     st.error(error_message + f" - {e_upd_act_api.response.text}")
                                except Exception as e_upd_act_api: 
                                    st.error(f"Failed to update job fair: {e_upd_act_api}")
                        else: st.error("Auth error.")
            
            if st.button("Close Actions View", key=f"close_actions_view_{selected_job_fair_data['id']}"):
                st.session_state.selected_job_fair_id_for_actions = None
                if 'confirm_delete_job_fair_id' in st.session_state: del st.session_state.confirm_delete_job_fair_id
                st.rerun()
        else:
            st.error("Could not load details for actions. It might have been deleted.")
            st.session_state.selected_job_fair_id_for_actions = None
            if st.button("Refresh List"):
                 st.rerun()

    # If 'remove map image' button is clicked
    # if st.form_submit_button("Yes, Remove Map Image", type="primary"):
    #     # Call API to remove map image
    #     success, message = api.remove_job_fair_map(selected_job_fair_data['id'])
    #     if success:
    #         st.success(f"Map image for '{selected_job_fair_data['name']}' removed successfully.")
    #         # Clear related session state keys to force re-fetch or hide UI elements
    #         if f'remove_map_image_ef_{selected_job_fair_data["id"]}' in st.session_state:
    #             del st.session_state[f'remove_map_image_ef_{selected_job_fair_data["id"]}']
    #         # Potentially clear other related states or trigger a rerun
    #         st.rerun()
    #     else:
    #         st.error(f"Failed to remove map image: {message}")

 