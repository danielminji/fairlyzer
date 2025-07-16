import streamlit as st
import pandas as pd
import json # For parsing skills JSON
import os
import sys # Import sys

# Add lib directory to path to ensure imports work
# This assumes 'pages' is a subdir of 'streamlit_frontend' and 'lib' is also a subdir of 'streamlit_frontend'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lib.api import make_api_request # Direct import from api.py
from lib.navigation import display_sidebar_navigation # Corrected import
from lib.ui_components import load_css # Corrected import, render_header removed as it was causing issues

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

# API Endpoints
JOB_REQUIREMENTS_ENDPOINT = "admin/job-requirements"

# Standardized Primary Field Options
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

# Initialize session state for CRUD operations
if 'confirm_delete_req_id' not in st.session_state:
    st.session_state.confirm_delete_req_id = None
if 'error_message_jr' not in st.session_state:
    st.session_state.error_message_jr = None
if 'success_message_jr' not in st.session_state:
    st.session_state.success_message_jr = None
if 'editing_req_id' not in st.session_state:
    st.session_state.editing_req_id = None
if 'current_req_data_for_edit' not in st.session_state:
    st.session_state.current_req_data_for_edit = None

st.set_page_config(page_title="Admin: Job Requirements", layout="wide")
load_css() # Assuming this is a custom function to load CSS

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

# --- Admin Authenticated Content for Job Requirements ---
display_sidebar_navigation()

st.title("Job Requirements Management")
st.caption("Manage job requirements for the system")

# Button to go back to Admin Dashboard
if st.button("← Back to Admin Dashboard", key="back_to_admin_dashboard_job_reqs"):
    st.switch_page("pages/admin_dashboard.py")
st.divider()

# --- Fetch Job Requirements ---
def fetch_job_requirements():
    response, success = make_api_request(JOB_REQUIREMENTS_ENDPOINT, "GET", params={'per_page': 'all'})
    if success:
        data = response.get('data', []) if isinstance(response, dict) else response
        if isinstance(data, list):
            return sorted(data, key=lambda x: x.get('id', 0), reverse=False)
        return data
    else:
        st.error(f"Failed to fetch job requirements: {response.get('error', 'Unknown error') if isinstance(response, dict) else 'Unknown error'}")
        return []

# --- Display Job Requirements ---

# --- Edit Job Requirement Form (Moved Here initially, will be moved below table) ---
# This section will be moved after the table display logic.
# For now, commenting out its conditional display here to avoid rendering it twice during refactor.
# if st.session_state.editing_req_id and st.session_state.current_req_data_for_edit:
#     ... (entire edit form logic was here) ...

job_requirements = fetch_job_requirements()

with st.expander("View Existing Job Requirements", expanded=False):
    if not job_requirements:
        st.info("No job requirements found. Add some below.")
    else:
        # Convert skills JSON arrays to a more readable format for display
        for req in job_requirements:
            # Handle required_skills_general (can be array or JSON string)
            if 'required_skills_general' in req:
                if isinstance(req['required_skills_general'], list):
                    req['skills_general_display'] = ", ".join(req['required_skills_general'])
                elif isinstance(req['required_skills_general'], str):
                    try: 
                        req['skills_general_display'] = ", ".join(json.loads(req['required_skills_general']))
                    except json.JSONDecodeError: 
                        req['skills_general_display'] = req['required_skills_general']
                else:
                    req['skills_general_display'] = str(req['required_skills_general'])
            
            # Handle required_skills_soft (can be array or JSON string)
            if 'required_skills_soft' in req:
                if isinstance(req['required_skills_soft'], list):
                    req['skills_soft_display'] = ", ".join(req['required_skills_soft'])
                elif isinstance(req['required_skills_soft'], str):
                    try: 
                        req['skills_soft_display'] = ", ".join(json.loads(req['required_skills_soft']))
                    except json.JSONDecodeError: 
                        req['skills_soft_display'] = req['required_skills_soft']
                else:
                    req['skills_soft_display'] = str(req['required_skills_soft'])

        # Fix column names to match backend response
        df_columns = ['id', 'job_title', 'primary_field', 'skills_general_display', 'skills_soft_display', 'required_experience_years', 'required_experience_entries', 'required_cgpa']
        df_display = pd.DataFrame(job_requirements)
        
        # Rename columns for better display
        column_renames = {
            'job_title': 'Job Title',
            'primary_field': 'Primary Field', 
            'skills_general_display': 'General Skills',
            'skills_soft_display': 'Soft Skills',
            'required_experience_years': 'Min Experience (Years)',
            'required_experience_entries': 'Min Experience Entries',
            'required_cgpa': 'Min CGPA'
        }
        
        # Filter for existing columns to avoid errors if some are missing
        available_columns = [col for col in df_columns if col in df_display.columns]
        df_display = df_display[available_columns]
        df_display = df_display.rename(columns=column_renames)
        
        # Display messages (moved before the table loop for clarity)
        if st.session_state.success_message_jr:
            st.success(st.session_state.success_message_jr)
            st.session_state.success_message_jr = None # Clear after displaying
        if st.session_state.error_message_jr:
            st.error(st.session_state.error_message_jr)
            st.session_state.error_message_jr = None # Clear after displaying

        # Column headers using st.columns
        header_cols = st.columns((0.5, 2, 1.5, 2, 2, 1, 1, 1, 0.5, 0.5)) 
        headers = ['ID', 'Job Title', 'Primary Field', 'General Skills', 'Soft Skills', 'Min Exp (Yrs)', 'Min Exp (#)', 'Min CGPA', 'Edit', 'Del']
        for col, header_text in zip(header_cols, headers):
            col.markdown(f"**{header_text}**")
        st.markdown("---") # Visual separator after headers

        for index, row_data_series in df_display.iterrows():
            row_data = row_data_series.to_dict()
            req_id = row_data['id']

            # Data and button columns for each row
            data_cols = st.columns((0.5, 2, 1.5, 2, 2, 1, 1, 1, 0.5, 0.5))
            
            data_cols[0].write(str(req_id))
            data_cols[1].write(row_data.get('Job Title', 'N/A'))
            data_cols[2].write(row_data.get('Primary Field', 'N/A'))
            data_cols[3].write(row_data.get('General Skills', 'N/A'))
            data_cols[4].write(row_data.get('Soft Skills', 'N/A'))
            data_cols[5].write(str(row_data.get('Min Experience (Years)', 'N/A')))
            data_cols[6].write(str(row_data.get('Min Experience Entries', 'N/A'))) # Corrected from 'Min Exp (#)' used in header to actual data key
            data_cols[7].write(str(row_data.get('Min CGPA', 'N/A')))
            
            # Edit button
            if data_cols[8].button("✏️", key=f"edit_req_{req_id}", help="Edit Job Requirement"):
                original_req_data = next((item for item in job_requirements if item['id'] == req_id), None)
                if original_req_data:
                    st.session_state.editing_req_id = req_id
                    st.session_state.current_req_data_for_edit = original_req_data
                    st.session_state.confirm_delete_req_id = None 
                    st.rerun()
                else:
                    st.session_state.error_message_jr = f"Could not find data for Job Requirement ID {req_id} to edit."
                    st.rerun()

            # Delete button
            if data_cols[9].button("🗑️", key=f"delete_req_{req_id}", help="Delete Job Requirement"):
                st.session_state.confirm_delete_req_id = req_id
                st.session_state.editing_req_id = None 
                st.rerun()

            # Display delete confirmation inline if this req_id is marked for deletion
            if st.session_state.confirm_delete_req_id == req_id:
                # Use columns for the confirmation message and buttons to keep it tidy
                confirm_msg_cols = st.columns((5, 1, 1, 3)) # Adjust ratios as needed
                with confirm_msg_cols[0]: # Span confirmation message over a few conceptual "columns"
                     st.warning(f"Delete ID: {req_id}?")
                
                if confirm_msg_cols[1].button("Yes", key=f"confirm_del_btn_{req_id}"):
                    # Assuming make_api_request is modified to return status_code
                    # If not, this part of the logic might need adjustment in api.py
                    response, success, status_code = make_api_request(f"{JOB_REQUIREMENTS_ENDPOINT}/{req_id}", "DELETE", return_status_code=True)
                    
                    if success or status_code == 204: # HTTP 204 No Content is a success for DELETE
                        st.session_state.success_message_jr = f"Job Requirement ID {req_id} deleted successfully."
                    else:
                        error_detail = "Unknown error"
                        if isinstance(response, dict):
                            error_detail = response.get('details', response.get('error', 'Failed to delete job requirement'))
                        elif isinstance(response, str): # Handle if response is just an error string
                            error_detail = response

                        st.session_state.error_message_jr = f"Error deleting ID {req_id}: {error_detail} (Status: {status_code})"
                    st.session_state.confirm_delete_req_id = None
                    st.session_state.editing_req_id = None # Clear any edit state
                    st.rerun()
                if confirm_msg_cols[2].button("No", key=f"cancel_del_btn_{req_id}"):
                    st.session_state.confirm_delete_req_id = None
                    st.rerun()
            st.markdown("---") # Visual separator for each row
        
        # The old global delete confirmation is now removed as it's inline.

# --- Edit Job Requirement Form (Moved to appear AFTER the table) ---
if st.session_state.editing_req_id and st.session_state.current_req_data_for_edit:
    req_to_edit = st.session_state.current_req_data_for_edit
    st.divider()
    st.subheader(f"Edit Job Requirement ID: {req_to_edit['id']}")
    
    with st.form(key="edit_job_requirement_form"):
        edit_job_title = st.text_input("Job Title*", value=req_to_edit.get('job_title', ''))
        
        primary_field_display_options_edit = list(PRIMARY_FIELD_OPTIONS_MAP.values())
        primary_field_keys_edit = list(PRIMARY_FIELD_OPTIONS_MAP.keys())
        current_primary_field_key_edit = req_to_edit.get('primary_field', primary_field_keys_edit[0])
        
        edit_primary_field_index = 0
        if current_primary_field_key_edit in primary_field_keys_edit:
            edit_primary_field_index = primary_field_keys_edit.index(current_primary_field_key_edit)
        
        selected_display_value_edit = st.selectbox("Primary Field*", 
                                                options=primary_field_display_options_edit, 
                                                index=edit_primary_field_index, 
                                                key="edit_primary_field_jr_select")
        edit_primary_field_snake = primary_field_keys_edit[primary_field_display_options_edit.index(selected_display_value_edit)]
        
        skills_general_list = req_to_edit.get('required_skills_general', [])
        edit_skills_general_str = st.text_area("General Skills (comma-separated)", value=", ".join(skills_general_list) if isinstance(skills_general_list, list) else "")
        
        skills_soft_list = req_to_edit.get('required_skills_soft', [])
        edit_skills_soft_str = st.text_area("Soft Skills (comma-separated)", value=", ".join(skills_soft_list) if isinstance(skills_soft_list, list) else "")
        
        edit_experience_years = st.number_input("Minimum Experience (Years)", min_value=0, value=int(req_to_edit.get('required_experience_years', 0)), step=1)
        
        edit_experience_entries_val = req_to_edit.get('required_experience_entries', 0)
        edit_experience_entries = st.number_input("Minimum Experience Entries (Number of distinct work experiences)", min_value=0, value=int(edit_experience_entries_val) if edit_experience_entries_val is not None else 0, step=1)
        
        edit_cgpa_val = req_to_edit.get('required_cgpa', 0.0)
        edit_cgpa = st.number_input("Minimum CGPA (0.0 to 4.0)", min_value=0.0, max_value=4.0, value=float(edit_cgpa_val) if edit_cgpa_val is not None else 0.0, step=0.1, format="%.2f")

        submit_edit_button = st.form_submit_button("Save Changes")
        cancel_edit_button = st.form_submit_button("Cancel Edit")

        if submit_edit_button:
            if not edit_job_title or not edit_primary_field_snake:
                st.error("Job Title and Primary Field are required.")
            else:
                payload = {
                    "job_title": edit_job_title,
                    "primary_field": edit_primary_field_snake, # Use the selected snake_case key
                    "required_skills_general": [s.strip() for s in edit_skills_general_str.split(',') if s.strip()],
                    "required_skills_soft": [s.strip() for s in edit_skills_soft_str.split(',') if s.strip()],
                    "required_experience_years": edit_experience_years,
                    "required_experience_entries": edit_experience_entries, 
                    "required_cgpa": edit_cgpa,
                }
                
                response, success, status_code = make_api_request(f"{JOB_REQUIREMENTS_ENDPOINT}/{st.session_state.editing_req_id}", "PUT", data=payload, return_status_code=True)
                
                if success or status_code == 200 or status_code == 204: 
                    st.session_state.success_message_jr = f"Job Requirement ID {st.session_state.editing_req_id} updated successfully."
                    st.session_state.editing_req_id = None
                    st.session_state.current_req_data_for_edit = None
                else:
                    error_detail = "Update failed."
                    if isinstance(response, dict):
                        error_detail = response.get('message', response.get('error', 'Failed to update job requirement.'))
                        if 'errors' in response: 
                             error_detail = response['errors'] 
                        elif 'details' in response: 
                            error_detail = response['details']
                    elif isinstance(response, str):
                        error_detail = response
                    
                    st.session_state.error_message_jr = f"Error updating ID {st.session_state.editing_req_id}: {error_detail} (Status: {status_code})"
                st.rerun()
        
        if cancel_edit_button:
            st.session_state.editing_req_id = None
            st.session_state.current_req_data_for_edit = None
            st.rerun()
    st.markdown("---")

st.markdown("---")
# --- Add New Job Requirement Form ---
st.subheader("Add New Job Requirement")
with st.form(key="add_job_requirement_form", clear_on_submit=True):
    add_job_title = st.text_input("Job Title*")
    
    primary_field_display_options_add = list(PRIMARY_FIELD_OPTIONS_MAP.values())
    primary_field_keys_add = list(PRIMARY_FIELD_OPTIONS_MAP.keys())
    
    selected_display_value_add = st.selectbox("Primary Field*", 
                                            options=primary_field_display_options_add, 
                                            index=0, # Default to the first option
                                            key="add_primary_field_jr_select")
    add_primary_field_snake = primary_field_keys_add[primary_field_display_options_add.index(selected_display_value_add)]

    add_description = st.text_area("Description (Optional)")
    
    st.markdown("**Skills** (Enter as comma-separated values)")
    add_skills_general_str = st.text_input("General Skills (e.g., Python, Java, CPR, Financial Modeling)")
    add_skills_soft_str = st.text_input("Soft Skills (e.g., Communication, Teamwork, Problem Solving)")
    
    min_experience_years = st.number_input("Minimum Experience (Years)", min_value=0, max_value=50, value=0, step=1)
    min_experience_entries = st.number_input("Minimum Experience Entries (Number of distinct work experiences)", min_value=0, max_value=20, value=0, step=1)
    min_cgpa = st.number_input("Minimum CGPA (e.g., 3.0)", min_value=0.0, max_value=4.0, value=3.0, step=0.01, format="%.2f")

    submitted = st.form_submit_button("Add Job Requirement")

    if submitted:
        if not add_job_title or not add_primary_field_snake:
            st.warning("Title and Primary Field are required.")
        elif not add_skills_general_str or not add_skills_soft_str:
            st.warning("Both General Skills and Soft Skills are required.")
        else:
            # Convert comma-separated skill strings to JSON arrays
            add_skills_general_list = [s.strip() for s in add_skills_general_str.split(',') if s.strip()]
            add_skills_soft_list = [s.strip() for s in add_skills_soft_str.split(',') if s.strip()]

            payload = {
                'job_title': add_job_title,
                'primary_field': add_primary_field_snake, # Use the selected snake_case key
                'description': add_description if add_description else None, # Ensure None if empty
                'required_skills_general': add_skills_general_list,
                'required_skills_soft': add_skills_soft_list,
                'required_experience_years': min_experience_years,
                'required_experience_entries': min_experience_entries,
                'required_cgpa': min_cgpa,
            }
            # Remove None values from payload keys like skills if they were empty strings
            payload = {k: v for k, v in payload.items() if v is not None}
            
            response, success, _ = make_api_request(JOB_REQUIREMENTS_ENDPOINT, "POST", data=payload)
            if success:
                st.success(f"Job Requirement '{add_job_title}' added successfully!")
                st.rerun()
            else:
                error_detail = response.get('details', response.get('error', 'Failed to add job requirement'))
                if isinstance(error_detail, list):
                    for err in error_detail: st.error(err)
                else:
                    st.error(error_detail)

# TODO: Implement Edit and Delete Modals/Forms 