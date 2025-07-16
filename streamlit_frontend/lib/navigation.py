"""
Navigation utilities for the Resume Analyzer & Booth Recommendations app.
Provides consistent navigation across all pages.
"""

import streamlit as st
from .auth_client import get_user_display_name, get_user_role, logout

st.markdown(
    """
    <style>
    /* Hide the default Streamlit sidebar navigation */
    [data-testid="stSidebarNav"] { display: none !important; }
    /* Hide the sidebar search input */
    [data-testid="stSidebarSearch"] { display: none !important; }
    /* Hide the sidebar header */
    [data-testid="stSidebarHeader"] { display: none !important; }
    </style>
    """,
    unsafe_allow_html=True
)

def display_sidebar_navigation():
    # --- SIDEBAR OPEN/CLOSE LOGIC (from ui.py) ---
    if 'sidebar_open' not in st.session_state:
        st.session_state['sidebar_open'] = True

    if st.session_state['sidebar_open']:
        st.markdown(
            """
            <style>
            .hide-sidebar-btn {
                position: absolute;
                top: 1.2rem;
                left: 1.2rem;
                z-index: 1002;
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background: #232b3b !important;
                color: #fff !important;
                border: none !important;
                box-shadow: 0 2px 8px rgba(0,0,0,0.12) !important;
                font-size: 1.3rem !important;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                transition: background 0.2s, box-shadow 0.2s;
            }
            .hide-sidebar-btn:hover, .hide-sidebar-btn:focus {
                background: #3b82f6 !important;
                box-shadow: 0 4px 16px rgba(59,130,246,0.18) !important;
                outline: none !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        with st.sidebar:
            if st.button('\u25c0', key='sidebar_collapse_navigation', help='Hide sidebar', use_container_width=True, type='secondary', kwargs={"className": "hide-sidebar-btn"}):
                st.session_state['sidebar_open'] = False
                st.rerun()
            # --- ORIGINAL SIDEBAR CONTENT BELOW ---
            st.sidebar.title("Navigation")
            user_role = st.session_state.get("user_role", "user")
            user_name = st.session_state.get("user_name", "Guest")
            st.sidebar.markdown(f"**Welcome, {user_name}!**")
            st.sidebar.markdown("---")
            st.sidebar.page_link("app.py", label="App Home", icon="\U0001F3E0")
            if user_role == "admin":
                st.sidebar.markdown("### Admin Menu")
                if st.sidebar.button("\U0001F451 Admin Dashboard", key="nav_admin_dashboard_main", use_container_width=True):
                    st.switch_page("pages/admin_dashboard.py")
                if st.sidebar.button("\U0001F465 User Management", key="nav_user_management_main", use_container_width=True):
                    st.switch_page("pages/admin_user_management.py")
                if st.sidebar.button("\U0001F4C4 Job Requirements", key="nav_job_req_main", use_container_width=True):
                    st.switch_page("pages/admin_job_requirements.py")
                if st.sidebar.button("\U0001F3E2 Job Fair Admin", key="nav_job_fair_admin_main", use_container_width=True):
                    st.switch_page("pages/admin_job_fair_management.py")
            elif user_role == "organizer":
                st.sidebar.markdown("### Organizer Menu")
                st.sidebar.page_link("pages/05_Organizer_Job_Fairs.py", label="Job Fairs", icon="\U0001F3E2")
                st.sidebar.page_link("pages/06_Organizer_Booth_Management.py", label="Booth Management", icon="\U0001F3EA")
            else:
                st.sidebar.markdown("### Job Seeker Menu")
                st.sidebar.page_link("pages/01_resume_upload.py", label="Resume Upload", icon="\U0001F4E4")
                st.sidebar.page_link("pages/02_my_resumes.py", label="My Resumes", icon="\U0001F4CB")
                st.sidebar.page_link("pages/02_resume_analysis.py", label="Resume Analysis", icon="\U0001F50D")
                st.sidebar.page_link("pages/08_Booth_Recommendations.py", label="Booth Recommendations", icon="\U0001F3AF")
            st.sidebar.markdown("---")
            st.sidebar.page_link("pages/05_profile.py", label="Profile", icon="\U0001F464")
            if st.sidebar.button("\U0001F6AA Logout", key="nav_logout_button"):
                from lib.auth_client import logout
                logout_response, success = logout()
                if success:
                    st.session_state.authenticated = False
                    st.session_state.user_token = None
                    st.session_state.user_role = None
                    st.session_state.clear()
                    st.switch_page("app.py")
                else:
                    st.sidebar.error("Logout failed. Please try again.")
                    st.switch_page("app.py")
    else:
        st.markdown(
            '<style>\n'
            'section[data-testid="stSidebar"] {\n'
            '    min-width: 0 !important;\n'
            '    width: 0 !important;\n'
            '    padding: 0 !important;\n'
            '    overflow: hidden !important;\n'
            '}\n'
            '.stButton>button.sidebar-round-btn {\n'
            '    border-radius: 50% !important;\n'
            '    width: 40px !important;\n'
            '    height: 40px !important;\n'
            '    min-width: 40px !important;\n'
            '    min-height: 40px !important;\n'
            '    background: #232b3b !important;\n'
            '    color: #fff !important;\n'
            '    border: none !important;\n'
            '    box-shadow: 0 2px 8px rgba(0,0,0,0.12) !important;\n'
            '    font-size: 1.3rem !important;\n'
            '    padding: 0 !important;\n'
            '    margin: 0.2rem 0.2rem 0.2rem 0.2rem !important;\n'
            '    transition: background 0.2s, box-shadow 0.2s;\n'
            '    margin-top: -0.7rem !important;\n'
            '    margin-left: -0.7rem !important;\n'
            '}\n'
            '.stButton>button.sidebar-round-btn:hover, .stButton>button.sidebar-round-btn:focus {\n'
            '    background: #3b82f6 !important;\n'
            '    box-shadow: 0 4px 16px rgba(59,130,246,0.18) !important;\n'
            '    outline: none !important;\n'
            '}\n'
            '</style>',
            unsafe_allow_html=True)
        open_col, _ = st.columns([0.07, 0.93])
        with open_col:
            open_btn = st.button('\u2630', key='sidebar_expand_navigation', help='Open sidebar', use_container_width=True, type='secondary', kwargs={"className": "sidebar-round-btn"})
        if open_btn:
            st.session_state['sidebar_open'] = True
            st.rerun()

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