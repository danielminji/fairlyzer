import sys
import os
import traceback

# Ensure the application root directory (streamlit_frontend) is in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
app_root_dir = os.path.dirname(current_dir)
if app_root_dir not in sys.path:
    sys.path.insert(0, app_root_dir)

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go # Added for more custom charts
from lib import ui
from lib.auth_client import require_auth
from lib import api
# Removed client-side: from lib.analyzer import get_job_recommendations

# Page configuration
st.set_page_config(
    page_title="Resume Analysis - Resume Analyzer",
    page_icon="📊",
    layout="wide"
)

# --- Helper Rendering Functions ---

def render_skills_overview(skills_data):
    st.subheader("🛠️ Skills Overview")
    if not skills_data or (not skills_data.get('general_skills') and not skills_data.get('soft_skills')):
        st.info("No skills data extracted.")
        return

    general_skills = skills_data.get('general_skills', [])
    soft_skills = skills_data.get('soft_skills', [])

    if not general_skills and not soft_skills:
        st.info("No skills data extracted.")
        return

    # Create a more visually appealing display for skills
    # Option 1: Two columns for General and Soft Skills
    col1, col2 = st.columns(2)

    with col1:
        # Using a more common icon that might render, or just text
        st.markdown("<h5>⚙️ General Skills</h5>", unsafe_allow_html=True)
        if general_skills:
            # Use st.chip for each skill or a more compact list
            skill_pills_html = "".join([f"<span style='display: inline-block; background-color: #1E90FF; color: white; padding: 5px 10px; margin: 3px 5px 3px 0; border-radius: 15px; font-size: 0.9em;'>{skill}</span>" for skill in general_skills])
            st.markdown(f"<div style='display: flex; flex-wrap: wrap;'>{skill_pills_html}</div>", unsafe_allow_html=True)
            with st.expander("View as List (General)"):
                 for skill in general_skills:
                    st.markdown(f"- {skill}")
        else:
            st.caption("No general skills extracted.")
    
    with col2:
        st.markdown("<h5>🤝 Soft Skills</h5>", unsafe_allow_html=True) # Changed icon
        if soft_skills:
            skill_pills_html = "".join([f"<span style='display: inline-block; background-color: #3CB371; color: white; padding: 5px 10px; margin: 3px 5px 3px 0; border-radius: 15px; font-size: 0.9em;'>{skill}</span>" for skill in soft_skills])
            st.markdown(f"<div style='display: flex; flex-wrap: wrap;'>{skill_pills_html}</div>", unsafe_allow_html=True)
            with st.expander("View as List (Soft)"):
                for skill in soft_skills:
                    st.markdown(f"- {skill}")
        else:
            st.caption("No soft skills extracted.")
    
    st.markdown("<br>", unsafe_allow_html=True)

    # A summary chart:
    if general_skills or soft_skills:
        st.markdown("##### Skills Count Summary")
        skill_counts_df = pd.DataFrame({
            'Skill Type': ['General Skills', 'Soft Skills'],
            'Count': [len(general_skills), len(soft_skills)]
        })
        # Using more distinct colors for the bar chart as well
        fig = px.bar(skill_counts_df, x='Skill Type', y='Count', color='Skill Type',
                     color_discrete_map={'General Skills': '#1E90FF', 'Soft Skills': '#3CB371'},
                     labels={'Count': 'Number of Skills'}, height=300)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)


def render_experience_section(experience):
    st.subheader("💼 Work Experience")
    if not experience:
        st.info("No work experience data extracted.")
        return
    for i, job in enumerate(experience):
        if not isinstance(job, dict):
            st.warning(f"Experience item {i+1} is not in the expected format.")
            continue
        title = job.get('title', 'N/A')
        company = job.get('company', 'N/A')
        date_range = job.get('date', 'N/A')
        location = job.get('location', 'N/A')
        responsibilities = job.get('responsibilities', [])

        st.markdown(f"**{title}** at **{company}**")
        st.caption(f"{location} | {date_range}")
        if responsibilities and responsibilities != ['N/A']:
            for resp in responsibilities:
                st.markdown(f"- {resp}")
        else:
            st.caption("No responsibilities listed.")
        if i < len(experience) - 1:
            st.markdown("---")
    st.markdown("<br>", unsafe_allow_html=True)

def render_education_section(education):
    st.subheader("🎓 Education") # Changed icon to 🎓
    if not education:
        st.info("No education data extracted.")
        return
    for i, edu_item in enumerate(education):
        if not isinstance(edu_item, dict):
            st.warning(f"Education item {i+1} is not in the expected format.")
            continue
        degree = edu_item.get('degree', 'N/A')
        institution = edu_item.get('institution', 'N/A')
        field = edu_item.get('field', '') # Assuming field might not always be present
        dates = edu_item.get('date', 'N/A')
        gpa = edu_item.get('gpa', edu_item.get('cgpa', '')) # Prefer 'cgpa' if available

        st.markdown(f"**{degree}** {f'in {field}' if field else ''}")
        st.markdown(f"*{institution}*")
        st.caption(f"{dates}{f' | CGPA: {gpa}' if gpa else ''}")
        if i < len(education) - 1:
            st.markdown("---")
    st.markdown("<br>", unsafe_allow_html=True)

def render_job_recommendations_section(recommendations):
    st.subheader("🎯 Job Recommendations")
    
    # This section will now solely rely on backend-provided recommendations
    # The 'recommendations' parameter is expected to be analysis_data.get('job_recommendations', [])
    
    if recommendations:
        st.success("Here are some job roles you might be a good fit for based on your resume:")
        for i, rec in enumerate(recommendations):
            if not isinstance(rec, dict):
                st.warning(f"Recommendation item {i+1} is not in the expected format.")
                continue

            title = rec.get('job_title', 'N/A')
            score = rec.get('score', 0)
            # Assuming the backend might provide a summary or matched skills later
            # For now, just title and score.
            
            st.markdown(f"#### {title}")
            st.progress(int(score), text=f"Match Score: {score}%")
            
            score_details = rec.get('score_details')
            if score_details:
                with st.expander("View Score Breakdown"):
                    st.markdown(f"- **Skills Score:** {score_details.get('skills', 0):.2f} / 40")
                    st.markdown(f"- **Experience Score:** {score_details.get('experience', 0):.2f} / 30")
                    st.markdown(f"- **Education Score:** {score_details.get('education', 0):.2f} / 30")

                    match_details = rec.get('match_details')
                    if match_details:
                        st.markdown("**Skills Match:**")
                        if match_details.get('matched_general_skills'):
                            matched_general_str = ", ".join(match_details['matched_general_skills'])
                            st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;Matched General: {matched_general_str}")
                        if match_details.get('missing_general_skills'):
                            missing_general_str = ", ".join(match_details['missing_general_skills'])
                            st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;<span style='color: orange;'>Missing General: {missing_general_str}</span>", unsafe_allow_html=True)
                        if match_details.get('matched_soft_skills'):
                            matched_soft_str = ", ".join(match_details['matched_soft_skills'])
                            st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;Matched Soft: {matched_soft_str}")
                        if match_details.get('missing_soft_skills'):
                            missing_soft_str = ", ".join(match_details['missing_soft_skills'])
                            st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;<span style='color: orange;'>Missing Soft: {missing_soft_str}</span>", unsafe_allow_html=True)
                        
                        st.markdown("**Experience Match:**")
                        exp_met_text = "Met" if match_details.get('experience_met') else "Not Met"
                        req_exp_years = match_details.get('required_experience_years', 'N/A')
                        resume_exp_formatted = match_details.get('resume_formatted_total_experience', 'N/A')
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;Requirement: {req_exp_years} years - Status: {exp_met_text} (Your Experience: {resume_exp_formatted})")

                        st.markdown("**Education Match:**")
                        edu_met_text = "Met" if match_details.get('education_met') else "Not Met"
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;Requirement (CGPA >= {match_details.get('required_cgpa', 'N/A')}): {edu_met_text} (Your CGPA: {match_details.get('resume_cgpa', 'N/A')})")
            
            description = rec.get('description')
            if description:
                with st.expander("View Job Description"):
                    st.markdown(description)

            if i < len(recommendations) - 1:
                st.markdown("---")
        st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("No job recommendations available at the moment. This could be because your resume data is still being processed by the backend, or no suitable matches were found based on the defined criteria (minimum 50% score).")

# --- Main Page Logic ---
@require_auth()
def main():
    ui.display_navbar()
    st.title("📄 Resume Analysis")

    default_session_state = {
        'selected_resume_id': None,
        'analysis_data': None,
        # 'client_job_recommendations': None, # REMOVED
        'selected_job_fair_id': "UITM_Job_Fair_2025",
        'analysis_loading': False,
        # 'scoring_weights': SCORING_WEIGHTS, # REMOVED
        'analyzed_resume_id_for_cached_data': None
    }
    for key, value in default_session_state.items():
        if key not in st.session_state:
            st.session_state[key] = value

    resume_id = st.session_state.selected_resume_id
    
    if not resume_id:
        st.warning("Please upload or select a resume first from the 'Upload Resume' or 'My Resumes' page.")
        if st.button("Go to Upload Page"):
            st.switch_page("pages/01_resume_upload.py")
        return
    
    # --- Modify Force Refresh Button Label ---
    if st.button("🔄 Refresh Analysis", key="force_refresh_analysis_btn"):
        st.session_state.analysis_data = None
        # st.session_state.client_job_recommendations = None # REMOVED
        st.session_state.analyzed_resume_id_for_cached_data = None
        st.success("Cleared cached analysis. Data will be re-fetched.")
        # st.rerun() # Re-run to immediately trigger re-fetch block, careful with loops if not placed correctly

    if st.session_state.analysis_data is not None and st.session_state.analyzed_resume_id_for_cached_data != resume_id:
        st.session_state.analysis_data = None
        # st.session_state.client_job_recommendations = None # REMOVED
        st.session_state.analyzed_resume_id_for_cached_data = None

    if st.session_state.analysis_data is None or st.session_state.analysis_data == {}:
        st.session_state.analysis_loading = True 
        api_response_data = None
        api_success_status = None
        try:
            # Use the fallback method that tries both cookie auth and explicit token auth
            api_response_data, api_success_status = api.get_resume_analysis_with_fallback(resume_id)
            
            if api_success_status:
                st.session_state.analysis_data = api_response_data.get('data', api_response_data) # data can be directly under api_response_data or under 'data' key
                st.session_state.analyzed_resume_id_for_cached_data = resume_id
            else:
                st.error(f"API Error: {api_response_data.get('error', 'Unknown API error')}")
                st.session_state.analysis_data = {}
        except Exception as e:
            st.error(f"An unexpected error occurred while fetching analysis: {str(e)}")
            st.write(f"Traceback: {traceback.format_exc()}") # Keep traceback for unexpected errors
            st.session_state.analysis_data = {} 
        finally:
            st.session_state.analysis_loading = False
            # st.rerun() # Keep commented, rerun can cause loops if not handled carefully
            
    if st.session_state.analysis_loading:
        st.info("Loading resume analysis...")
        return 
    
    analysis_output = st.session_state.analysis_data
    
    if analysis_output and isinstance(analysis_output, dict) and analysis_output.get('filename'):
        st.success(f"Displaying analysis for resume: **{analysis_output.get('filename', f'ID: {resume_id}')}**")
        
        primary_field = analysis_output.get('primary_field', 'general')
        st.metric(label="Identified Primary Field", value=primary_field.replace('_', ' ').title() if primary_field != 'N/A' else 'Not Available')

        # Display Formatted Total Experience - CORRECTED PLACEMENT
        formatted_exp = analysis_output.get('formatted_total_experience')
        if formatted_exp:
            st.markdown(f"**Total Work Experience:** {formatted_exp}")
        # st.markdown("---") # Separator will be handled by the next major section or tab display

        tab_titles = ["Skills", "Experience", "Education", "Job Recommendations"]
        tabs = st.tabs(tab_titles)

        with tabs[0]: 
            skills_data = analysis_output.get('skills', {})
            render_skills_overview(skills_data)
        with tabs[1]: 
            experience_data = analysis_output.get('experience', [])
            render_experience_section(experience_data)
        with tabs[2]: 
            education_data = analysis_output.get('education', [])
            render_education_section(education_data)
        with tabs[3]: 
            # REMOVED Client-Side Recommendation Generation Block
            # st.subheader("Client-Generated Job Recommendations")
            # if st.button("🔄 Generate Job Recommendations", key="generate_client_job_recs_btn", type="primary"):
            # ... (entire block removed) ...
            #
            # if st.session_state.client_job_recommendations is not None:
            #     render_job_recommendations_section(st.session_state.client_job_recommendations)
            # else:
            #     st.caption("Click the button above to generate job recommendations.")
            # st.markdown("---") # This separator can also be removed if client-side is gone

            st.subheader("Job Recommendations") # Changed from "Backend-Provided Job Recommendations" to just "Job Recommendations"
            backend_recommendations = analysis_output.get('job_recommendations', [])
            if backend_recommendations:
                 render_job_recommendations_section(backend_recommendations)
            else:
                 st.info("No job recommendations were provided for this resume, or they are still being generated. Please ensure the backend processing is complete. If this persists, there might be no suitable matches based on the defined criteria (minimum 50% score).")

            st.markdown("---")
            if st.session_state.get("analysis_data") and st.session_state.analysis_data.get("resume_id"):
                st.subheader("Next Steps at the Job Fair")
                if st.button("🎯 Find Recommended Booths & View Map", key="find_booths_button"):
                    # Store resume_id in session_state for the next page to pick up
                    st.session_state.current_resume_id_for_booth_recommendation = st.session_state.analysis_data.get("resume_id")
                    st.switch_page("pages/08_Booth_Recommendations.py")

    elif st.session_state.analysis_data == {}: 
        st.error("Failed to load resume analysis. Please try again or select a different resume.")
    else: 
        st.info("Select a resume to view its analysis.")

if __name__ == "__main__":
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if st.session_state.get('authenticated', False):
        main()
    else:
        st.error("Please login to access this page.")
        if st.button("Go to Login"):
            st.switch_page("app.py") # Corrected to app.py