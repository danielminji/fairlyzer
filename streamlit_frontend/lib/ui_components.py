import streamlit as st
import os
from streamlit.components.v1 import html
from . import api
from .auth_client import login, register, register_organizer, logout, check_auth, get_current_user, get_user_display_name
from .css.ui import load_css

def load_css():
    """Load global CSS from a file"""
    css_file = os.path.join(os.path.dirname(__file__), "css", "global.css")
    with open(css_file, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def render_header():
    """Render the application header with auth status and theme toggle"""
    # This component is causing the black box, so we will comment it out.
    # with st.container():
    #     col1, col2, col3 = st.columns([6, 3, 1])
        
    #     with col1:
    #         st.title("Resume Analyzer & Booth Recommendations")
        
    #     with col2:
    #         if check_auth():
    #             user_name = get_user_display_name()
    #             st.write(f"👤 Logged in as: {user_name}")
        
    #     with col3:
    #         # Theme toggle button - uses JavaScript to toggle theme
    #         html("""
    #         <button 
    #             onclick="toggleTheme()" 
    #             style="background: transparent; border: none; cursor: pointer; float: right;">
    #             <svg width="24" height="24" viewBox="0 0 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    #                 <path d="M12 18C15.3137 18 18 15.3137 18 12C18 8.68629 15.3137 6 12 6C8.68629 6 6 8.68629 6 12C6 15.3137 8.68629 18 12 18Z" 
    #                       stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    #                 <path d="M12 2V4M12 20V22M4.93 4.93L6.34 6.34M17.66 17.66L19.07 19.07M2 12H4M20 12H22M4.93 19.07L6.34 17.66M17.66 6.34L19.07 4.93" 
    #                       stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    #             </svg>
    #         </button>
    #         """)
    
    # st.divider()
    pass

def render_footer():
    """Render the application footer"""
    st.divider()
    st.markdown("© 2025 Resume Analyzer & Booth Recommendations")

def render_admin_sidebar():
    """Render sidebar navigation options for admin users"""
    if st.sidebar.button("👨‍💼 Manage Organizers", key="manage_organizers_btn"):
        st.session_state.page = 'admin_organizers'
        st.rerun()
    if st.sidebar.button("🎪 Manage Job Fairs", key="manage_job_fairs_btn"):
        st.session_state.page = 'admin_job_fairs'
        st.rerun()
    if st.sidebar.button("📊 System Analytics", key="system_analytics_btn"):
        st.session_state.page = 'admin_analytics'
        st.rerun()

def render_organizer_sidebar():
    """Render sidebar navigation options for organizer users"""
    if st.sidebar.button("🎪 My Job Fairs", key="my_job_fairs_btn"):
        st.session_state.page = 'organizer_job_fairs'
        st.rerun()
    if st.sidebar.button("🏢 Manage Booths", key="manage_booths_btn"):
        st.session_state.page = 'organizer_booths'
        st.rerun()
    if st.sidebar.button("📊 Analytics", key="analytics_btn"):
        st.session_state.page = 'organizer_analytics'
        st.rerun()

def render_jobseeker_sidebar():
    """Render sidebar navigation options for job seeker users"""
    if st.sidebar.button("📄 My Resumes", key="my_resumes_btn"):
        st.session_state.page = 'my_resumes'
        st.rerun()
    if st.sidebar.button("📋 Resume Analysis", key="resume_analysis_btn"):
        st.session_state.page = 'resume_analysis'
        st.rerun()
    if st.sidebar.button("🎯 Booth Recommendations", key="booth_recommendations_btn"):
        st.session_state.page = 'booth_recommendations'
        st.rerun()
    if st.sidebar.button("🗺️ Job Fair Map", key="job_fair_map_btn"):
        st.session_state.page = 'job_fair_map'
        st.rerun()

def render_login_form():
    """Render the login form"""
    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if not email or not password:
                st.error("Email and password are required.")
            else:
                success, message = login(email, password)
                if success:
                    st.success("Login successful!")
                    st.session_state.page = 'home'
                    st.rerun()
                else:
                    st.error(f"Login failed: {message}")

def render_register_form():
    """Render the registration form for job seekers"""
    with st.form("register_form", clear_on_submit=True):
        name = st.text_input("Full Name", key="reg_name")
        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Password", type="password", key="reg_password")
        password_confirm = st.text_input("Confirm Password", type="password", key="reg_password_confirm")
        submit_button = st.form_submit_button("Register")
        
        if submit_button:
            if not name or not email or not password or not password_confirm:
                st.error("All fields are required.")
            elif password != password_confirm:
                st.error("Passwords do not match.")
            else:
                success, message = register(name, email, password, password_confirm)
                if success:
                    st.success("Registration successful! Please log in.")
                    st.session_state.page = 'login'
                    st.rerun()
                else:
                    st.error(f"Registration failed: {message}")

def render_organizer_signup_form():
    """Render the registration form for organizers"""
    with st.form("organizer_register_form", clear_on_submit=True):
        name = st.text_input("Full Name", key="org_name")
        email = st.text_input("Email", key="org_email")
        company = st.text_input("Company Name", key="org_company")
        password = st.text_input("Password", type="password", key="org_password")
        password_confirm = st.text_input("Confirm Password", type="password", key="org_password_confirm")
        submit_button = st.form_submit_button("Register as Organizer")
        
        if submit_button:
            if not name or not email or not company or not password or not password_confirm:
                st.error("All fields are required.")
            elif password != password_confirm:
                st.error("Passwords do not match.")
            else:
                success, message = register_organizer(name, email, password, password_confirm, company)
                if success:
                    st.success("Registration submitted for approval. You will be notified when your account is approved.")
                else:
                    st.error(f"Registration failed: {message}")

def render_card(title, content, actions=None, status=None):
    """Render a card with title, content, and optional actions and status"""
    card_classes = "card"
    if status:
        card_classes += f" card-{status}"
    
    html(f"""
    <div class="{card_classes}">
        <div class="card-title">{title}</div>
        <div class="card-content">{content}</div>
    </div>
    """)
    
    if actions:
        st.write(actions)

def render_status_indicator(status, message):
    """Render a status indicator with appropriate styling"""
    if status == "success":
        st.success(message)
    elif status == "info":
        st.info(message)
    elif status == "warning":
        st.warning(message)
    elif status == "error":
        st.error(message)
    else:
        st.write(message)

def render_job_fair_card(job_fair):
    """Render a job fair card with all relevant information"""
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader(job_fair.get('title', 'Unnamed Job Fair'))
            st.write(f"**Location:** {job_fair.get('location', 'TBD')}")
            
            # Process start_time and end_time for display (extract date part)
            start_time_str = job_fair.get('start_time', 'TBD')
            end_time_str = job_fair.get('end_time', 'TBD')
            
            display_start_date = start_time_str.split("T")[0] if "T" in start_time_str and start_time_str != 'TBD' else start_time_str
            display_end_date = end_time_str.split("T")[0] if "T" in end_time_str and end_time_str != 'TBD' else end_time_str
            
            st.write(f"**Dates:** {display_start_date} to {display_end_date}")
            if job_fair.get('description'):
                st.write(job_fair.get('description'))
        
        with col2:
            if st.button("View Details", key=f"view_{job_fair['id']}"):
                st.session_state.active_job_fair_id = job_fair['id']
                st.session_state.page = 'job_fair_details'
                st.rerun()
            
            if st.button("View Map", key=f"map_{job_fair['id']}"):
                st.session_state.active_job_fair_id = job_fair['id']
                st.session_state.page = 'job_fair_map'
                st.rerun()
        
        st.divider()

def render_booth_card(booth, show_match_score=False, match_score=None):
    """Render a booth card with company info and optional match score"""
    with st.container():
        cols = st.columns([3, 1]) if not show_match_score else st.columns([2, 1, 1])
        
        with cols[0]:
            st.subheader(booth.get('company_name', 'Unknown Company'))
            st.write(f"**Booth #:** {booth.get('booth_number', 'N/A')}")
            st.write(f"**Industry:** {booth.get('industry', 'N/A')}")
            if booth.get('description'):
                st.write(booth.get('description'))
        
        if show_match_score and match_score is not None:
            with cols[1]:
                st.metric("Match Score", f"{match_score}%")
        
        with cols[-1]:
            if st.button("View Details", key=f"booth_{booth['id']}"):
                st.session_state.active_booth_id = booth['id']
                st.session_state.page = 'booth_details'
                st.rerun()
        
        st.divider()

def render_job_card(job):
    """Render a job recommendation card using native Streamlit components"""
    with st.container():
        # Get job details with fallbacks
        job_title = job.get('title', job.get('role', 'Unknown Position'))
        match_score = job.get('match_percentage', job.get('match_score', 0))
        matching_skills = job.get('matching_skills', [])
        
        # Determine color based on match percentage
        if match_score >= 80:
            color = "green"
        elif match_score >= 60:
            color = "orange"
        else:
            color = "red"
        
        # Display job title
        st.subheader(job_title)
        
        # Show match score with progress bar
        col1, col2 = st.columns([4, 1])
        with col1:
            st.progress(match_score/100)
        with col2:
            st.markdown(f"<span style='color:{color}; font-weight:bold;'>{match_score}%</span>", unsafe_allow_html=True)
        
        # Display matching skills
        st.markdown("**Matching Skills:**")
        if matching_skills:
            skills_text = ', '.join(matching_skills[:3])
            if len(matching_skills) > 3:
                skills_text += f" and {len(matching_skills) - 3} more"
            st.write(skills_text)
        else:
            st.write("No specific skills matched")
        
        # Add a divider for visual separation
        st.divider()

def render_resume_card(resume):
    """Render a resume card with actions"""
    with st.container():
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.subheader(resume.get('file_name', resume.get('filename', 'Unnamed Resume')))
            st.write(f"Uploaded: {resume.get('created_at', 'Unknown')}")
        
        with col2:
            if st.button("View Analysis", key=f"view_{resume['id']}"):
                st.session_state.active_resume_id = resume['id']
                st.session_state.page = 'resume_analysis'
                st.rerun()
        
        with col3:
            if st.button("Get Recommendations", key=f"rec_{resume['id']}"):
                st.session_state.active_resume_id = resume['id']
                st.session_state.page = 'booth_recommendations'
                st.rerun()
        
        st.divider()

def render_user_card(user, user_type="general"):
    """Render a user card with user information"""
    with st.container():
        cols = st.columns([3, 1])
        with cols[0]:
            st.subheader(user.get('name', 'Unknown'))
            
            # Format role with proper styling
            role = user.get('role', 'user').upper()
            role_class = f"user-role user-role-{role.lower()}"
            
            # Format status with proper indicator
            status = "ACTIVE" if user.get('is_active', True) else "INACTIVE"
            status_class = f"status-indicator status-{'active' if user.get('is_active', True) else 'inactive'}"
            
            # Use html component for custom styling
            html(f"""
            <div class="user-card">
                <div style="margin-bottom: 10px;">
                    <span class="{role_class}">{role}</span>
                </div>
                <div>
                    <strong>Email:</strong> {user.get('email', 'No email')}
                </div>
                <div>
                    <strong>Status:</strong> <span class="{status_class}">{status}</span>
                </div>
            </div>
            """)
        
        with cols[1]:
            if user.get('profile_image'):
                st.image(user.get('profile_image'), width=100)
            else:
                # Placeholder image with user initials
                initials = ''.join([name[0].upper() for name in user.get('name', 'U U').split() if name])[:2]
                html(f"""
                <div style="width: 80px; height: 80px; border-radius: 50%; background-color: var(--primary-color); 
                           color: white; display: flex; align-items: center; justify-content: center; 
                           font-size: 24px; font-weight: bold; margin: 0 auto;">
                    {initials}
                </div>
                """)

def render_admin_card(icon, title, description, priority=3, action_btn=None):
    """Render an admin dashboard card with icon, title and description"""
    html(f"""
    <div class="admin-card priority-{priority}">
        <div class="card-icon">{icon}</div>
        <div class="card-title">{title}</div>
        <div>{description}</div>
    </div>
    """)
    
    if action_btn:
        st.button(action_btn, key=f"btn_{title.lower().replace(' ','_')}")

def render_tabs(tab_names, default_tab=0):
    """Render tabs and return the selected tab objects"""
    return st.tabs(tab_names)

def handle_api_error(error_message, response_text=None):
    """Handle API errors in a consistent way"""
    st.error(f"Error: {error_message}")
    if response_text:
        with st.expander("Response Details"):
            st.code(response_text)
    return False 