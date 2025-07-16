import streamlit as st
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

st.set_page_config(layout="wide", page_title="Organizer: Booth Management")


import requests
import pandas as pd
import json
from datetime import datetime

# Configuration for the Laravel API
API_BASE_URL = "http://localhost:8000/api" # Make sure this matches your Laravel dev server
LOGIN_URL = f"{API_BASE_URL}/login" # For login if not already logged in
ORGANIZER_JOB_FAIRS_URL = f"{API_BASE_URL}/organizer/job-fairs"
# Booths are nested under job fairs for listing and creation:
# GET /api/organizer/job-fairs/{jobFair}/booths
# POST /api/organizer/job-fairs/{jobFair}/booths
# Individual booth management (update, delete):
# PUT /api/organizer/booths/{booth}
# DELETE /api/organizer/booths/{booth}
ORGANIZER_BOOTHS_BASE_URL = f"{API_BASE_URL}/organizer/booths"
ORGANIZER_BOOTH_JOB_OPENINGS_URL_FORMAT = f"{API_BASE_URL}/organizer/booths/{{booth_id}}/job-openings" # For specific booth's job openings
ORGANIZER_JOB_OPENING_URL_FORMAT = f"{API_BASE_URL}/organizer/job-openings/{{job_opening_id}}" # For individual job opening CRUD

# --- Authentication (similar to 05_Organizer_Job_Fairs.py) ---
def handle_organizer_login(email, password):
    try:
        response = requests.post(LOGIN_URL, data={'email': email, 'password': password})
        response.raise_for_status()
        data = response.json()
        if 'token' in data and 'user' in data:
            if data['user'].get('role') == 'organizer':
                st.session_state.user_token = data['token']
                st.session_state.current_user = data['user']
                st.session_state.user_id = data['user']['id']
                st.session_state.user_role = data['user']['role']
                st.session_state.user_name = data['user']['name']
                st.session_state.authenticated = True
                st.success("Logged in successfully as Organizer!")
                st.rerun() # Rerun to reflect login state
            else:
                st.error("Login successful, but you are not an approved organizer.")
        else:
            st.error("Login failed: Token or user data not found in response.")
    except requests.exceptions.HTTPError as e:
        st.error(f"Login failed: {e.response.status_code} - {e.response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"Login request failed: {e}")

def handle_organizer_logout():
    for key in ['user_token', 'current_user', 'user_id', 'user_role', 'user_name', 'authenticated']:
        if key in st.session_state:
            del st.session_state[key]
    st.success("Logged out.")
    st.query_params.clear() # Clear query params on logout
    st.switch_page("00_Login_Register.py") # Or back to the main job fairs page if preferred

def get_organizer_auth_headers():
    if 'user_token' not in st.session_state:
        return None
    return {'Authorization': f"Bearer {st.session_state.user_token}", 'Accept': 'application/json'}

# --- API Helper Functions for Booths ---
def fetch_job_fair_details(job_fair_id):
    headers = get_organizer_auth_headers()
    if not headers: return None
    try:
        response = requests.get(f"{ORGANIZER_JOB_FAIRS_URL}/{job_fair_id}", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        st.error(f"Failed to fetch job fair details: {e.response.status_code} - {e.response.text}")
        if e.response.status_code == 404:
             st.warning(f"Job Fair with ID {job_fair_id} not found.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
        return None

def fetch_booths_for_job_fair(job_fair_id):
    headers = get_organizer_auth_headers()
    if not headers: return []
    try:
        url = f"{ORGANIZER_JOB_FAIRS_URL}/{job_fair_id}/booths"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        st.error(f"Failed to fetch booths: {e.response.status_code} - {e.response.text}")
        return []
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
        return []

# --- API Helper Functions for Job Openings ---
def fetch_job_openings_for_booth(booth_id):
    headers = get_organizer_auth_headers()
    if not headers: return []
    try:
        url = ORGANIZER_BOOTH_JOB_OPENINGS_URL_FORMAT.format(booth_id=booth_id)
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        st.error(f"Failed to fetch job openings for booth {booth_id}: {e.response.status_code} - {e.response.text}")
        return []
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
        return []

def create_job_opening_for_booth(booth_id, data):
    headers = get_organizer_auth_headers()
    if not headers: 
        st.error("Authentication error. Cannot create job opening.")
        return None
    try:
        url = ORGANIZER_BOOTH_JOB_OPENINGS_URL_FORMAT.format(booth_id=booth_id)
        response = requests.post(url, headers=headers, json=data) # Send as JSON payload
        response.raise_for_status()
        st.success("Job opening created successfully!")
        return response.json()
    except requests.exceptions.HTTPError as e:
        error_msg = f"Failed to create job opening: {e.response.status_code}"
        try:
            error_details = e.response.json()
            if "message" in error_details:
                error_msg += f" - {error_details['message']}"
            if "errors" in error_details:
                for field, messages in error_details["errors"].items():
                    for msg in messages:
                        st.error(f"{field.replace('_', ' ').capitalize()}: {msg}")
            else:
                 st.error(error_msg + f" - {e.response.text}")
        except json.JSONDecodeError:
            st.error(error_msg + f" - {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
        return None

def update_job_opening(job_opening_id, data):
    headers = get_organizer_auth_headers()
    if not headers: 
        st.error("Authentication error. Cannot update job opening.")
        return None
    try:
        url = ORGANIZER_JOB_OPENING_URL_FORMAT.format(job_opening_id=job_opening_id)
        response = requests.put(url, headers=headers, json=data) # Send as JSON payload
        response.raise_for_status()
        st.success("Job opening updated successfully!")
        return response.json()
    except requests.exceptions.HTTPError as e:
        error_msg = f"Failed to update job opening: {e.response.status_code}"
        try:
            error_details = e.response.json()
            if "message" in error_details:
                error_msg += f" - {error_details['message']}"
            if "errors" in error_details:
                for field, messages in error_details["errors"].items():
                    for msg in messages:
                        st.error(f"{field.replace('_', ' ').capitalize()}: {msg}")
            else:
                 st.error(error_msg + f" - {e.response.text}")
        except json.JSONDecodeError:
            st.error(error_msg + f" - {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
        return None

def delete_job_opening(job_opening_id):
    headers = get_organizer_auth_headers()
    if not headers: 
        st.error("Authentication error. Cannot delete job opening.")
        return False
    try:
        url = ORGANIZER_JOB_OPENING_URL_FORMAT.format(job_opening_id=job_opening_id)
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        st.success("Job opening deleted successfully!")
        return True
    except requests.exceptions.HTTPError as e:
        st.error(f"Failed to delete job opening: {e.response.status_code} - {e.response.text}")
        return False
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
        return False

# --- Helper function definitions for Job Openings (moved up) ---
# PRIMARY_FIELD_OPTIONS = ["Computer Science", "Medical", "Finance", "General"] # Old options
PRIMARY_FIELD_OPTIONS_MAP = {
    "computer_science": "Computer Science",
    "medical": "Medical",
    "finance": "Finance",
    "engineering": "Engineering",
    "real_estate": "Real Estate",
    "environmental_science": "Environmental Science",
    "marketing": "Marketing",
    "design": "Design",
    "logistics": "Logistics",
    "urban_planning": "Urban Planning",
    "architecture": "Architecture",
    "general": "General"
}

def render_job_opening_form(booth_id, job_opening_id=None):
    st.subheader("Add/Edit Job Opening")
    
    # Determine the default or initial primary_field (snake_case)
    default_primary_field_key = list(PRIMARY_FIELD_OPTIONS_MAP.keys())[0] # Fallback to the first key

    current_data = {
        'job_title': '',
        'primary_field': default_primary_field_key, # Store the key (snake_case)
        'description': '',
        'required_skills_general': [],
        'required_skills_soft': [],
        'required_experience_years': 0,
        'required_experience_entries': 0,
        'required_cgpa': 0.0
    }

    if job_opening_id and st.session_state.get('editing_job_opening_id') == job_opening_id:
        edit_data = st.session_state.get('current_job_opening_data_for_edit', {})
        current_data['job_title'] = edit_data.get('job_title', '')
        # Ensure primary_field from edit_data is a valid key, otherwise use default
        current_primary_field_from_edit = edit_data.get('primary_field', default_primary_field_key)
        if current_primary_field_from_edit not in PRIMARY_FIELD_OPTIONS_MAP.keys():
            # If the stored value isn't a key (e.g., old TitleCase value), try to find its key
            found_key = None
            for key, value in PRIMARY_FIELD_OPTIONS_MAP.items():
                if value == current_primary_field_from_edit:
                    found_key = key
                    break
            current_data['primary_field'] = found_key if found_key else default_primary_field_key
        else:
            current_data['primary_field'] = current_primary_field_from_edit
        
        current_data['description'] = edit_data.get('description', '')
        current_data['required_skills_general'] = edit_data.get('required_skills_general', []) if isinstance(edit_data.get('required_skills_general'), list) else []
        current_data['required_skills_soft'] = edit_data.get('required_skills_soft', []) if isinstance(edit_data.get('required_skills_soft'), list) else []
        current_data['required_experience_years'] = edit_data.get('required_experience_years', 0)
        current_data['required_experience_entries'] = edit_data.get('required_experience_entries', 0)
        current_data['required_cgpa'] = edit_data.get('required_cgpa', 0.0)

    with st.form(key=f"job_opening_form_{job_opening_id if job_opening_id else 'new'}"):
        job_title = st.text_input("Job Title", value=current_data['job_title'])
        
        # Get list of display values (Title Case) for options
        primary_field_display_options = list(PRIMARY_FIELD_OPTIONS_MAP.values())
        # Get list of keys (snake_case) to map selection back
        primary_field_keys = list(PRIMARY_FIELD_OPTIONS_MAP.keys())
        
        # Determine the index for the current primary_field key
        try:
            current_primary_field_key_index = primary_field_keys.index(current_data['primary_field'])
        except ValueError:
            current_primary_field_key_index = 0 # Default to first option if key not found

        selected_display_value = st.selectbox(
            "Primary Field", 
            options=primary_field_display_options, 
            index=current_primary_field_key_index
        )
        # Map selected display value back to its snake_case key for submission
        selected_primary_field_key = primary_field_keys[primary_field_display_options.index(selected_display_value)]
        
        description = st.text_area("Description (Optional)", value=current_data['description'], height=150)
        
        st.markdown("##### Required Skills")
        skills_general_str = st.text_input("General Skills (e.g., Network Protocols, Firewall Management)", 
                                        value=", ".join(current_data['required_skills_general']),
                                        help="Enter skills separated by commas. Example: TCP/IP, VPN, Cisco iOS")
        skills_soft_str = st.text_input("Soft Skills (e.g., Communication, Teamwork)", 
                                      value=", ".join(current_data['required_skills_soft']),
                                      help="Enter skills separated by commas. Example: Problem Solving, Collaboration, Time Management")
        
        st.markdown("##### Required Experience")
        exp_years = st.number_input("Years of Work Experience", min_value=0, step=1, value=int(current_data['required_experience_years']))
        exp_entries = st.number_input("Total of Work Experience", min_value=0, step=1, value=int(current_data['required_experience_entries']))

        st.markdown("##### Required Education/Qualification")
        cgpa = st.number_input("Minimum CGPA (0.0 to 4.0)", min_value=0.0, max_value=4.0, step=0.01, value=float(current_data['required_cgpa']), format="%.2f")
        
        submit_button_label = "Update Job Opening" if job_opening_id else "Add Job Opening"
        submitted = st.form_submit_button(submit_button_label)

        if submitted:
            required_skills_general = [s.strip() for s in skills_general_str.split(',') if s.strip()] 
            required_skills_soft = [s.strip() for s in skills_soft_str.split(',') if s.strip()]
            
            job_opening_data = {
                'job_title': job_title,
                'primary_field': selected_primary_field_key, # Submit the snake_case key
                'description': description,
                'required_skills_general': required_skills_general,
                'required_skills_soft': required_skills_soft,
                'required_experience_years': exp_years,
                'required_experience_entries': exp_entries,
                'required_cgpa': float(f"{cgpa:.2f}")
            }

            if job_opening_id:
                updated_opening = update_job_opening(job_opening_id, job_opening_data)
                if updated_opening:
                    st.session_state.editing_job_opening_id = None 
                    st.session_state.current_job_opening_data_for_edit = None
                    st.rerun()
            else:
                new_opening = create_job_opening_for_booth(booth_id, job_opening_data)
                if new_opening:
                    st.rerun() 
    
    if job_opening_id and st.button("Cancel Edit", key=f"cancel_edit_jo_{job_opening_id}"):
        st.session_state.editing_job_opening_id = None
        st.session_state.current_job_opening_data_for_edit = None
        st.rerun()

def display_job_openings_for_booth(booth_id):
    st.subheader(f"Job Openings for Booth ID: {booth_id}")
    job_openings = fetch_job_openings_for_booth(booth_id)

    if not job_openings:
        st.info("No job openings found for this booth yet. Use the form below to add one.")
    else:
        for jo in job_openings:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{jo.get('job_title', 'N/A')}** (ID: {jo['id']})")
                st.caption(f"Primary Field: {jo.get('primary_field', 'N/A')}")
                if jo.get('description'):
                    with st.expander("Description"):
                        st.write(jo.get('description'))
                
                details_md = f"""
                - **General Skills:** { ', '.join(jo.get('required_skills_general', [])) if jo.get('required_skills_general') else 'N/A'}
                - **Soft Skills:** { ', '.join(jo.get('required_skills_soft', [])) if jo.get('required_skills_soft') else 'N/A'}
                - **Experience:** {jo.get('required_experience_years', 'N/A')} years, {jo.get('required_experience_entries', 'N/A')} entries
                - **Min CGPA:** {jo.get('required_cgpa', 'N/A')}
                """
                st.markdown(details_md)

            with col2:
                if st.button("Edit", key=f"edit_jo_{jo['id']}"):
                    st.session_state.editing_job_opening_id = jo['id']
                    st.session_state.current_job_opening_data_for_edit = jo 
                    st.rerun() 
            with col3:
                if st.button("Delete", key=f"delete_jo_{jo['id']}"):
                    st.session_state.confirm_delete_job_opening_id = jo['id']
                    st.rerun()
            
            if st.session_state.get('confirm_delete_job_opening_id') == jo['id']:
                st.warning(f"Are you sure you want to delete job opening: {jo.get('job_title', '(No Title)')} (ID: {jo['id']})?")
                c1, c2, _ = st.columns([1,1,5])
                if c1.button("Confirm Delete", key=f"confirm_del_btn_jo_{jo['id']}"):
                    if delete_job_opening(jo['id']):
                        st.session_state.confirm_delete_job_opening_id = None
                        st.rerun()
                    else:
                        st.session_state.confirm_delete_job_opening_id = None 
                        st.rerun() 
                if c2.button("Cancel Delete", key=f"cancel_del_btn_jo_{jo['id']}"):
                    st.session_state.confirm_delete_job_opening_id = None
                    st.rerun()
            st.divider()

    if st.session_state.get('editing_job_opening_id'):
        render_job_opening_form(booth_id, job_opening_id=st.session_state.editing_job_opening_id)
    else:
        render_job_opening_form(booth_id) 

# --- Main Page Logic ---
if not st.session_state.get('authenticated') or st.session_state.get('user_role') != 'organizer':
    st.subheader("Organizer Login Required")
    if st.session_state.get('authenticated') and st.session_state.get('user_role') != 'organizer':
        st.warning(f"You are logged in as a {st.session_state.get('user_role')}. Organizer access required for this page.")
        if st.button("Logout and switch account?"):
            handle_organizer_logout() # This will redirect
        st.stop()
    
    # Show login form if not authenticated at all
    st.write("You need to be logged in as an Organizer to manage booths.")
    st.page_link("pages/05_Organizer_Job_Fairs.py", label="Go to Organizer Login/Dashboard", icon="🔑")
    st.stop()

# Authenticated as Organizer, proceed.
st.sidebar.write(f"Welcome, Organizer {st.session_state.user_name}!")
if st.sidebar.button("Logout", key="booth_mgmt_logout"):
    handle_organizer_logout()

job_fair_id = st.session_state.get('booth_management_job_fair_id')

if not job_fair_id:
    st.warning("No Job Fair selected for booth management. Please select a job fair from the Job Fair Management page.")
    if st.button("Go to Job Fair Management"):
        st.switch_page("pages/05_Organizer_Job_Fairs.py")
    st.stop()

# Fetch and display job fair details for context
job_fair_details = fetch_job_fair_details(job_fair_id)

if job_fair_details:
    job_fair_title = job_fair_details.get('title', 'Selected Job Fair')
    st.title(f"Booth Management for: {job_fair_title}")

    # Display a breadcrumb or back navigation
    if st.button("← Back to Job Fair List (05)"):
        # Optionally clear session state specific to this page before navigating
        keys_to_clear = ['selected_booth_id', 'editing_booth', 'editing_job_opening_id', 'current_job_opening_data_for_edit']
        for key in keys_to_clear:
            if key in st.session_state: del st.session_state[key]
        # booth_management_job_fair_id is cleared by the target page if it's done with it, or kept if returning to same one
        st.switch_page("pages/05_Organizer_Job_Fairs.py")

    display_location = job_fair_details.get('formatted_address') if job_fair_details.get('formatted_address') else job_fair_details.get('location', 'N/A')
    st.caption(f"Job Fair ID: {job_fair_id} | Location: {display_location}")
    st.markdown("---")

    # Initialize session state for selected booth and editing mode
    if 'selected_booth_id' not in st.session_state:
        st.session_state.selected_booth_id = None
    if 'editing_booth' not in st.session_state:
        st.session_state.editing_booth = False # True if edit form for booth is active
    if 'editing_job_opening_id' not in st.session_state: # For editing a specific job opening
        st.session_state.editing_job_opening_id = None
    if 'current_job_opening_data_for_edit' not in st.session_state:
        st.session_state.current_job_opening_data_for_edit = {}

    # --- Booth Listing and Management ---
    st.header("Manage Booths")

    # --- Add Booth Form (always visible) ---
    with st.form("add_booth_form", clear_on_submit=True):
        st.subheader("Add a New Booth")
        new_company_name = st.text_input("Company Name", key="add_booth_company_name")
        new_booth_number = st.text_input("Booth Number", key="add_booth_number")
        add_booth_submitted = st.form_submit_button("Add Booth")
        if add_booth_submitted:
            if not new_company_name or not new_booth_number:
                st.warning("Both Company Name and Booth Number are required.")
            else:
                headers = get_organizer_auth_headers()
                if headers:
                    try:
                        create_url = f"{ORGANIZER_JOB_FAIRS_URL}/{job_fair_id}/booths"
                        payload = {
                            "company_name": new_company_name,
                            "booth_number_on_map": new_booth_number
                        }
                        response = requests.post(create_url, headers=headers, json=payload)
                        response.raise_for_status()
                        st.success("Booth added successfully!")
                        st.rerun()
                    except requests.exceptions.HTTPError as e:
                        st.error(f"Failed to add booth: {e.response.status_code} - {e.response.text}")
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
                else:
                    st.error("Authentication error. Please log in again.")

    booths_data = fetch_booths_for_job_fair(job_fair_id)

    if booths_data:
        if not booths_data: # Check if the list is empty
            st.info("No booths found for this job fair yet.")
        else:
            for booth_item in booths_data: # Iterate directly over the list of dicts
                booth_id = booth_item['id']
                with st.container(border=True):
                    st.subheader(f"{booth_item.get('company_name', 'N/A')} - Booth {booth_item.get('booth_number_on_map', 'N/A')} (ID: {booth_id})") # Use booth_number_on_map
                    col_b_manage_openings, col_b_edit, col_b_delete = st.columns(3)
                    if col_b_manage_openings.button("Manage Job Openings 💼", key=f"manage_openings_booth_{booth_id}"):
                        st.session_state.managing_job_openings_for_booth_id = booth_id
                        st.session_state.selected_booth_id_for_edit = None # Clear other selections
                        st.session_state.confirm_delete_booth_id = None
                        st.session_state.editing_job_opening_id = None # Clear job opening edit state too
                        st.session_state.confirm_delete_job_opening_id = None
                        st.rerun()

                    if col_b_edit.button("Edit Booth Details ✏️", key=f"edit_booth_{booth_id}"):
                        st.session_state.selected_booth_id_for_edit = booth_id
                        st.session_state.confirm_delete_booth_id = None 
                        st.session_state.managing_job_openings_for_booth_id = None # Clear other selections
                        st.rerun()
                    if col_b_delete.button("Delete Booth 🗑️", key=f"delete_booth_{booth_id}", type="secondary"):
                        st.session_state.confirm_delete_booth_id = booth_id
                        st.session_state.selected_booth_id_for_edit = None 
                        st.session_state.managing_job_openings_for_booth_id = None # Clear other selections
                        st.rerun()
    else:
        st.info("No booths found for this job fair yet or failed to load them.")

    st.markdown("---")

    # --- Section for Editing or Deleting Selected Booth ---
    selected_booth_id = st.session_state.get('selected_booth_id_for_edit')
    confirm_delete_booth_id = st.session_state.get('confirm_delete_booth_id')

    # Logic for managing job openings will be handled in a separate block below this one

    if selected_booth_id is not None and st.session_state.get('managing_job_openings_for_booth_id') is None:
        selected_booth_data = None
        if booths_data:
            for booth_item_for_edit in booths_data:
                if booth_item_for_edit['id'] == selected_booth_id:
                    selected_booth_data = booth_item_for_edit
                    break
        
        if selected_booth_data:
            st.header(f"Edit Booth: {selected_booth_data.get('company_name')} (Booth {selected_booth_data.get('booth_number_on_map', 'N/A')})")
            with st.form(f"edit_booth_form_{selected_booth_id}", clear_on_submit=False):
                edit_company_name = st.text_input("Company Name", value=selected_booth_data.get('company_name', ''), key=f"edit_company_{selected_booth_id}")
                edit_booth_number_on_map = st.text_input("Booth Number", value=selected_booth_data.get('booth_number_on_map', ''), key=f"edit_booth_num_on_map_{selected_booth_id}") # Changed field name
                
                submitted_edit_booth = st.form_submit_button("Save Booth Changes")
                if submitted_edit_booth:
                    if not edit_company_name or not edit_booth_number_on_map:
                        st.warning("Company Name and Booth Number are required.")
                    else:
                        headers = get_organizer_auth_headers()
                        if headers:
                            payload = {
                                'company_name': edit_company_name,
                                'booth_number_on_map': edit_booth_number_on_map, # Changed field name
                            }
                            try:
                                update_url = f"{ORGANIZER_BOOTHS_BASE_URL}/{selected_booth_id}"
                                response = requests.put(update_url, headers=headers, data=payload) # Using data for form-encoded
                                response.raise_for_status()
                                st.success(f"Booth '{edit_company_name}' updated successfully!")
                                st.session_state.selected_booth_id_for_edit = None # Clear selection
                                st.rerun()
                            except requests.exceptions.HTTPError as e:
                                st.error(f"Failed to update booth: {e.response.status_code} - {e.response.text}")
                                # Further error parsing can be added if needed
                            except Exception as e:
                                st.error(f"An unexpected error occurred: {e}")
            if st.button("Cancel Edit", key=f"cancel_edit_booth_{selected_booth_id}"):
                st.session_state.selected_booth_id_for_edit = None
                st.rerun()

    elif confirm_delete_booth_id is not None and st.session_state.get('managing_job_openings_for_booth_id') is None:
        # ... (delete confirmation logic for booth - remains largely the same but ensure it does not conflict with job opening delete)
        booth_to_delete_data = None
        if booths_data:
            for b_data in booths_data:
                if b_data['id'] == confirm_delete_booth_id:
                    booth_to_delete_data = b_data
                    break
        if booth_to_delete_data:
            st.subheader(f"Confirm Delete Booth: {booth_to_delete_data.get('company_name')}")
            st.warning(f"⚠️ Permanently delete this booth and ALL its associated job openings? This CANNOT be undone.")
            col_del_confirm, col_del_cancel = st.columns(2)
            if col_del_confirm.button("YES, DELETE BOOTH AND ITS JOB OPENINGS", key=f"confirm_del_booth_btn_{confirm_delete_booth_id}", type="primary"):
                headers = get_organizer_auth_headers()
                if headers:
                    try:
                        delete_url = f"{ORGANIZER_BOOTHS_BASE_URL}/{confirm_delete_booth_id}"
                        response = requests.delete(delete_url, headers=headers)
                        response.raise_for_status()
                        st.success(f"Booth '{booth_to_delete_data.get('company_name')}' and its job openings deleted.")
                        st.session_state.confirm_delete_booth_id = None
                        st.rerun()
                    except requests.exceptions.HTTPError as e:
                        st.error(f"Failed to delete booth: {e.response.status_code} - {e.response.text}")
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
            if col_del_cancel.button("Cancel Delete", key=f"cancel_del_booth_btn_{confirm_delete_booth_id}"):
                st.session_state.confirm_delete_booth_id = None
                st.rerun()
        else:
            st.error("Could not find booth data to delete.")
            st.session_state.confirm_delete_booth_id = None # Clear state

    st.markdown("---")

    # --- Section for Managing Job Openings for a Selected Booth ---
    managing_booth_id = st.session_state.get('managing_job_openings_for_booth_id')
    editing_job_opening_id = st.session_state.get('editing_job_opening_id')
    confirm_delete_job_opening_id = st.session_state.get('confirm_delete_job_opening_id')

    if managing_booth_id is not None:
        # Find the booth details from the booths_data list
        current_booth_for_job_openings = None
        if booths_data:
            for b_data in booths_data:
                if b_data['id'] == managing_booth_id:
                    current_booth_for_job_openings = b_data
                    break
        
        if not current_booth_for_job_openings:
            st.error("Selected booth data not found. Please go back and select a booth again.")
            st.session_state.managing_job_openings_for_booth_id = None # Clear state
            st.stop()

        st.header(f"Manage Job Openings for: {current_booth_for_job_openings.get('company_name')} (Booth {current_booth_for_job_openings.get('booth_number_on_map')})")

        display_job_openings_for_booth(managing_booth_id)

        if st.button("Done with Job Openings for this Booth", key=f"done_managing_jo_{managing_booth_id}"):
            st.session_state.managing_job_openings_for_booth_id = None
            st.session_state.editing_job_opening_id = None
            st.session_state.current_job_opening_data_for_edit = None
            st.session_state.confirm_delete_job_opening_id = None
            st.rerun()

    if st.button("⬅️ Back to All Job Fairs"):
        # Clear all booth & job opening specific states before navigating away
        for key_to_clear in ['managing_job_openings_for_booth_id', 'editing_job_opening_id', 
                             'current_job_opening_data_for_edit', 'confirm_delete_job_opening_id',
                             'selected_booth_id_for_edit', 'confirm_delete_booth_id']:
            if key_to_clear in st.session_state:
                del st.session_state[key_to_clear]
        st.switch_page("pages/05_Organizer_Job_Fairs.py") 