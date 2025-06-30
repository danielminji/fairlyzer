"""
UI components for the Resume Analyzer & Booth Recommendations app
"""

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import os
from .api import get_all_job_fairs, get_job_fair_details, API_BASE_URL, register_user # Ensure register_user is imported
from .auth_client import logout as logout_function, login as login_function # Ensure login is imported

# No CSS loading here - moved to app.py after st.set_page_config

def display_landing_page():
    """
    Display the landing page for the Resume Analyzer & Booth Recommendations app
    """
    st.markdown(
        """
        <style>
        .hero-section {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            margin-top: 2.5rem;
            margin-bottom: 2rem;
        }
        .hero-title { font-size: 3.2rem; font-weight: 900; background: linear-gradient(90deg, #3b82f6, #60a5fa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .hero-sub { font-size: 1.3rem; color: #cbd5e1; margin-bottom: 1.5rem; }
        .feature-card {
            background: #232b3b;
            border-radius: 18px;
            padding: 2rem 1.5rem;
            box-shadow: 0 4px 24px rgba(0,0,0,0.08);
            text-align: center;
            min-height: 260px;
            min-width: 200px;
            max-width: 220px;
            width: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: space-between;
            transition: transform 0.18s cubic-bezier(.4,2,.6,1), box-shadow 0.18s cubic-bezier(.4,2,.6,1);
        }
        .feature-card:hover {
            transform: scale(1.045);
            box-shadow: 0 8px 32px rgba(59,130,246,0.18);
            background: #22304a;
        }
        .feature-icon { font-size: 2.5rem; margin-bottom: 0.5rem; }
        .jobfair-card {
            background: #232b3b;
            border-radius: 18px;
            padding: 1.5rem 1.2rem 1.2rem 1.2rem;
            box-shadow: 0 4px 24px rgba(0,0,0,0.10);
            margin-bottom: 2rem;
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            min-height: 420px;
        }
        .jobfair-map-img { border-radius: 12px; width: 100%; height: auto; margin-bottom: 1rem; }
        .status-badge {
            background: #3b82f6;
            color: white;
            border-radius: 8px;
            padding: 0.2rem 0.7rem;
            font-size: 0.9rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            display: inline-block;
        }
        .jobfair-header-row {
            width: 100%;
            display: flex;
            flex-direction: row;
            justify-content: space-between;
            align-items: center;
        }
        .jobfair-title { margin-top: 1rem; font-size: 1.2rem; font-weight: 700; }
        .jobfair-desc { color: #cbd5e1; margin-bottom: 0.7rem; }
        .jobfair-list { color: #cbd5e1; margin-top: 1rem; margin-bottom: 1.2rem; }
        .jobfair-btn-row { width: 100%; margin-top: 1.2rem; text-align: center; }
        .jobfair-btn-row button, .jobfair-btn-row .stButton > button {
            width: 100% !important;
            background: #3b82f6 !important;
            color: white !important;
            font-size: 1.1rem;
            padding: 0.7rem 0;
            border-radius: 8px;
        }
        @media (max-width: 900px) {
            .hero-title { font-size: 2.2rem; }
            .feature-card { padding: 1.2rem 0.5rem; min-width: 140px; max-width: 180px; }
            .jobfair-card { min-width: 90vw; }
        }
        @media (max-width: 600px) {
            .hero-title { font-size: 1.3rem; }
            .feature-card { padding: 0.7rem 0.2rem; min-width: 120px; max-width: 100%; }
            .hero-section { margin-top: 1rem; }
            .jobfair-card { min-width: 98vw; }
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown('<div class="hero-section">', unsafe_allow_html=True)
    st.markdown('<span class="hero-title">Resume Analyzer & Booth <span style="color:#3b82f6;">Recommendations</span></span>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Your AI-powered Job Fair Assistant</div>', unsafe_allow_html=True)
    st.write("Get personalized career insights and discover the perfect job fair booths tailored to your skills and aspirations")
    # Center login/register using columns
    col1, col2, col3 = st.columns([2,2,2])
    with col2:
        c1, c2 = st.columns([1,1])
        with c1:
            login_clicked = st.button("Login", key="landing_login_btn", use_container_width=True)
        with c2:
            register_clicked = st.button("Register", key="landing_register_btn", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    if login_clicked:
        st.session_state.view = "login"
        st.rerun()
    if register_clicked:
        st.session_state.view = "register"
        st.rerun()
    st.markdown("---")

    # --- HOW IT WORKS SECTION ---
    st.header("How It Works")
    st.write("Your AI-powered job fair assistant makes finding the right opportunities simple and efficient")
    features = [
        {"icon": "➡️", "title": "Login", "desc": "Create your account and login to get started with our platform"},
        {"icon": "📤", "title": "Upload Resume", "desc": "Upload your resume for AI-powered analysis and optimization"},
        {"icon": "📊", "title": "Get Analysis", "desc": "Receive detailed insights and recommendations for improvement"},
        {"icon": "📍", "title": "Find Booths", "desc": "Get personalized booth recommendations based on your resume"},
        {"icon": "🏢", "title": "Visit Booth", "desc": "Connect with employers at recommended job fair booths"},
    ]
    cols = st.columns(len(features), gap="large")
    for col, feat in zip(cols, features):
        with col:
            st.markdown(f'<div class="feature-card"><div class="feature-icon">{feat["icon"]}</div><b>{feat["title"]}</b><br><span style="color:#cbd5e1;">{feat["desc"]}</span></div>', unsafe_allow_html=True)
    st.markdown("---")

    # --- CURRENT & UPCOMING JOB FAIRS ---
    st.header("Current & Upcoming Job Fairs")
    st.write("Discover exciting career opportunities at upcoming job fairs tailored to your profile")
    try:
        job_fairs_data, success = get_all_job_fairs()
        job_fairs = []
        if success and job_fairs_data:
            if isinstance(job_fairs_data, dict) and 'data' in job_fairs_data:
                job_fairs = job_fairs_data['data']
            elif isinstance(job_fairs_data, list):
                job_fairs = job_fairs_data
            if not job_fairs:
                st.info("No job fairs available at the moment.")
            else:
                current_date = datetime.now().strftime("%Y-%m-%d")
                current_job_fairs = []
                upcoming_job_fairs = []
                for jf in job_fairs:
                    start_datetime_str = jf.get("start_datetime", "")
                    end_datetime_str = jf.get("end_datetime", "")
                    start_date = start_datetime_str.split("T")[0] if "T" in start_datetime_str else start_datetime_str
                    end_date = end_datetime_str.split("T")[0] if "T" in end_datetime_str else end_datetime_str
                    jf["_display_start_date"] = start_date
                    jf["_display_end_date"] = end_date
                    try:
                        if start_date and end_date and start_date <= current_date <= end_date:
                            jf["status"] = "current"
                            current_job_fairs.append(jf)
                        elif start_date and start_date > current_date:
                            jf["status"] = "upcoming"
                            upcoming_job_fairs.append(jf)
                    except (ValueError, TypeError):
                        if start_date and start_date > current_date:
                            upcoming_job_fairs.append(jf)
                upcoming_job_fairs = sorted(upcoming_job_fairs, key=lambda x: x.get("_display_start_date", ""))
                # Responsive: 2 columns desktop, 1 column mobile
                fair_cols = st.columns(2, gap="large")
                for idx, fair in enumerate(current_job_fairs[:2] + upcoming_job_fairs[:2]):
                    with fair_cols[idx % 2]:
                        lat = fair.get('latitude')
                        lon = fair.get('longitude')
                        geoapify_api_key = st.secrets.get("GEOAPIFY_API_KEY")
                        if lat and lon and geoapify_api_key:
                            static_map_url = f"https://maps.geoapify.com/v1/staticmap?style=osm-carto&width=600&height=300&center=lonlat:{lon},{lat}&zoom=15&marker=lonlat:{lon},{lat};color:%23ff0000;size:medium&apiKey={geoapify_api_key}"
                        else:
                            static_map_url = "https://via.placeholder.com/600x300?text=Map+Unavailable"
                        status_text = "Live Now" if fair.get("status") == "current" else "Upcoming"
                        booths_count = fair.get('booths_count', 0)
                        organizer_name = fair.get("organizer", {}).get("name", "N/A") if isinstance(fair.get("organizer"), dict) else "Administrator"
                        st.markdown(f"""
                        <div class='jobfair-card'>
                            <img src='{static_map_url}' class='jobfair-map-img' alt='Job Fair Map'/>
                            <div class='jobfair-header-row'>
                                <span class='status-badge'>{status_text}</span>
                                <span style='color:#cbd5e1; font-size:0.95rem;'>{booths_count} Booths</span>
                            </div>
                            <div class='jobfair-title'>{fair.get('title', 'No Title')}</div>
                            <div class='jobfair-desc'>{fair.get('description', '')}</div>
                            <ul class='jobfair-list'>
                                <li><b>Location:</b> {fair.get('formatted_address') or fair.get('location_query') or fair.get('location', 'N/A')}</li>
                                <li><b>Dates:</b> {fair.get('_display_start_date')} to {fair.get('_display_end_date')}</li>
                                <li><b>Organized by:</b> {organizer_name}</li>
                            </ul>
                            <div class='jobfair-btn-row'>
                                <button>Learn More</button>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
        elif not success:
            st.warning(f"Could not load job fairs. {job_fairs_data.get('error', 'The backend might be unavailable.') if isinstance(job_fairs_data, dict) else 'Please try again later.'}")
        else:
            st.info("No job fairs available at the moment.")
    except Exception as e:
        st.error(f"An error occurred while loading job fair data: {str(e)}")
        print(f"Exception in display_landing_page loading job fairs: {e}")
    st.markdown("---")

    # --- CALL TO ACTION ---
    st.markdown('<div class="cta-section">', unsafe_allow_html=True)
    st.header("Ready to Accelerate Your Career?")
    st.write("Join thousands of students and professionals who have found their dream opportunities")
    if st.button("Get Started Today", use_container_width=True):
        st.session_state.view = "login"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.caption("© 2025 Resume Analyzer & Booth Recommendations | Powered by AI")

def display_login_page():
    st.empty()
    st.markdown('''<div class="auth-container">''', unsafe_allow_html=True)
    # st.image("https://via.placeholder.com/150x50?text=App+Logo", width=150) # Placeholder logo
    st.header("Welcome Back!")
    st.caption("Sign in to continue to your dashboard.")

    with st.form("login_form"):
        email = st.text_input("Email Address", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")

        if submitted:
            success, message_or_data = login_function(email, password)
            if success:
                st.session_state.authenticated = True
                st.session_state.user_role = message_or_data.get("role", "user") # Store user role
                st.session_state.user_name = message_or_data.get("name", "User") # Store user name
                st.session_state.user_id = message_or_data.get("id") 
                st.session_state.view = "home" 
                st.success("Login successful! Redirecting...")
                st.rerun()
            else:
                # Check if the error message indicates an authentication failure (likely 401)
                if isinstance(message_or_data, str) and "Authentication failed" in message_or_data:
                    st.error("Incorrect email or password. Please try again.")
                elif isinstance(message_or_data, dict) and "Authentication failed" in message_or_data.get("error", ""):
                    st.error("Incorrect email or password. Please try again.")
                else:
                    # Display the original error message for other types of errors
                    st.error(message_or_data)
    
    col_back, col_register = st.columns(2)
    with col_back:
        if st.button("Back to Home", key="login_back_home", use_container_width=True):
            st.session_state.view = "landing"
            st.rerun()
    with col_register:
        if st.button("Create Account", key="login_create_account", use_container_width=True):
            st.session_state.view = "register"
            st.rerun()
    st.markdown('''</div>''', unsafe_allow_html=True)

def display_register_page():
    st.empty()
    st.markdown('''<div class="auth-container">''', unsafe_allow_html=True)
    # st.image("https://via.placeholder.com/150x50?text=App+Logo", width=150) # Placeholder logo
    st.header("Create Your Account")
    st.caption("Join us to find your next opportunity or talent.")

    with st.form("register_form"):
        name = st.text_input("Full Name", key="register_name")
        email = st.text_input("Email Address", key="register_email")
        password = st.text_input("Password (min. 8 characters)", type="password", key="register_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="register_confirm_password")
        
        role_display = st.radio("I am a:", ["Job Seeker", "Organizer"], horizontal=True, key="register_role_display")
        # Determine the value to be sent to the backend API
        api_user_type_value = "user" # Default to 'user' for "Job Seeker"
        if role_display == "Organizer":
            api_user_type_value = "organizer_applicant" # Use 'organizer_applicant' for backend
        
        company_name_value = None
        if role_display == "Organizer": # Keep UI conditional display based on "Organizer" selection
            company_name_value = st.text_input("Company Name (Required for Organizers)", key="register_company_name")

        submitted = st.form_submit_button("Register", use_container_width=True, type="primary")

        if submitted:
            if not name or not email or not password or not confirm_password:
                st.error("Please fill in all required fields.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            elif len(password) < 8:
                st.error("Password must be at least 8 characters long.")
            elif role_display == "Organizer" and not company_name_value: # Keep UI validation based on "Organizer"
                st.error("Company name is required for organizers.")
            else:
                # Call the unified register_user from api.py
                response, success = register_user(
                    name=name, 
                    email=email, 
                    password=password, 
                    password_confirmation=confirm_password, 
                    role=api_user_type_value, 
                    company=company_name_value 
                )
                if success:
                    if api_user_type_value == "organizer_applicant":
                        st.success("Organizer registration submitted! Your application is now pending admin approval. Please check your email for updates.")
                    else:
                        st.success("Registration successful! Please log in.")
                        st.session_state.view = "login" # Redirect to login page
                        st.rerun()
                else:
                    error_message = "Registration failed."
                    if isinstance(response, dict):
                        # Laravel validation errors are in response['error']['details']
                        error_details = response.get('error', {}).get('details', {})
                        if error_details:
                            # Display each validation error separately
                            for field, messages in error_details.items():
                                if isinstance(messages, list) and messages:
                                    st.error(f"{field.replace('_', ' ').capitalize()}: {messages[0]}")
                        else:
                            # Fallback for other types of errors
                            st.error(response.get('error', 'An unknown error occurred.'))
                    else:
                        st.error(error_message)

    col_back, col_login = st.columns(2)
    with col_back:
        if st.button("Back to Home", key="register_back_home", use_container_width=True):
            st.session_state.view = "landing"
            st.rerun()
    with col_login:
        if st.button("Already have an account? Sign In", key="register_sign_in", use_container_width=True):
            st.session_state.view = "login"
            st.rerun()
    st.markdown('''</div>''', unsafe_allow_html=True)

def display_navbar():
    # st.sidebar.image("https://via.placeholder.com/200x60?text=App+Logo", width=200) 
    st.sidebar.title("Navigation")
    
    user_role = st.session_state.get("user_role", "user") 
    user_name = st.session_state.get("user_name", "Guest")
    
    st.sidebar.markdown(f"Welcome, **{user_name}**!")
    st.sidebar.markdown(f"Role: _{user_role.capitalize()}_")
    st.sidebar.divider()

    if st.sidebar.button("🏠 Home", key="nav_home_main", use_container_width=True):
        st.session_state.view = "home" 
        st.switch_page("app.py") 

    if user_role == "admin":
        if st.sidebar.button("👑 Admin Dashboard", key="nav_admin_dashboard", use_container_width=True):
            st.switch_page("pages/admin_dashboard.py")
        if st.sidebar.button("👥 User Management", key="nav_user_management", use_container_width=True):
            st.switch_page("pages/admin_user_management.py")
    elif user_role == "organizer":
        if st.sidebar.button("💼 Organizer Job Fairs", key="nav_organizer_job_fairs", use_container_width=True):
            st.switch_page("pages/05_Organizer_Job_Fairs.py")
    elif user_role == "pending_organizer_approval":
        # For pending organizers, profile and logout are sufficient.
        # Home will show their pending status.
        pass # Home is already added above, no other specific links for pending other than profile/logout below
    else: # This is now primarily for 'user' (Job Seeker)  
        if st.sidebar.button("📤 Resume Upload", key="nav_resume_upload", use_container_width=True):
            st.switch_page("pages/01_resume_upload.py")
        if st.sidebar.button("📋 My Resumes", key="nav_my_resumes", use_container_width=True):
            st.switch_page("pages/02_my_resumes.py")

    if st.sidebar.button("👤 My Profile", key="nav_profile_all", use_container_width=True):
        st.switch_page("pages/05_profile.py")

    st.sidebar.divider()
    if st.sidebar.button("🚪 Logout", key="nav_logout_main", use_container_width=True):
        logout_function() 
        keys_to_keep = ['view', 'app_setup_complete'] # Persist view to redirect correctly
        for key in list(st.session_state.keys()):
            if key not in keys_to_keep and key not in ['authenticated', 'user_role', 'user_name', 'user_id', 'csrf_token', 'session_cookie']: # also clear auth tokens
                del st.session_state[key]
        st.session_state.authenticated = False
        st.session_state.view = "login" 
        st.success("Logged out successfully.")
        st.rerun()

def display_home_page():
    st.title(f"Welcome to your Dashboard, {st.session_state.get('user_name', 'User')}!")
    user_role = st.session_state.get("user_role", "user")

    if user_role == "admin":
        st.header("Admin Overview")
        st.write("Manage users, job fairs, and system settings.")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("👑 Admin Dashboard", use_container_width=True, key="home_admin_dashboard_btn"):
                st.switch_page("pages/admin_dashboard.py")
    elif user_role == "organizer":
        st.header("Organizer Dashboard")
        st.write("Manage your job fairs, booths, and view applicant data.")
        if st.button("💼 Manage Job Fairs", use_container_width=True, key="home_org_job_fairs_btn"):
            st.switch_page("pages/05_Organizer_Job_Fairs.py")

    elif user_role == "pending_organizer_approval":
        st.header("Application Pending Approval")
        st.info("Your organizer application is currently awaiting admin approval. Please check your email for updates. You will be notified once your application is processed.")
        st.warning("In the meantime, your access is limited. If you intended to register as a Job Seeker, please log out and create a new account with the 'Job Seeker' role.")

    else: # Job Seeker
        st.header("Job Seeker Dashboard")
        st.write("Upload your resume, view analysis, and get job recommendations.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 My Resumes", key="home_my_resumes", use_container_width=True):
                st.switch_page("pages/02_my_resumes.py")
        with col2:
            if st.button("📤 Upload New Resume", key="home_upload_resume", use_container_width=True):
                st.switch_page("pages/01_resume_upload.py")

    st.divider()
    st.subheader("Quick Links")
    if st.button("👤 My Profile", use_container_width=True, key="home_ql_profile_btn"):
        st.switch_page("pages/05_profile.py")

    st.subheader("Recent Activity (Placeholder)")
    st.info("No recent activity to display yet.")

    st.markdown("---")
    display_job_fair_calendar()

def display_job_fair_calendar():
    # Implementation of display_job_fair_calendar function
    pass

def display_api_error(response_data, default_message="An API error occurred."):
    if isinstance(response_data, dict):
        message = response_data.get("message", default_message)
        errors = response_data.get("errors")
        if errors and isinstance(errors, dict):
            for field, err_list in errors.items():
                if isinstance(err_list, list) and err_list:
                    message += f"\n- {field.replace('_', ' ').capitalize()}: {err_list[0]}"
        st.error(message)
    elif isinstance(response_data, str):
        st.error(response_data) # If the error is already a string
    else:
        st.error(default_message)