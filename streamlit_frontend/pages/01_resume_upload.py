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
import pathlib

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

# Inject custom CSS for gradient background, glassmorphism, Lucide icons, and responsive layout
st.markdown('''
<style>
body {
    background: linear-gradient(120deg, #334155 0%, #2563eb 100%) !important;
    min-height: 100vh;
}
.resume-glass-card {
    background: rgba(30, 41, 59, 0.65);
    box-shadow: 0 8px 32px 0 rgba(31, 41, 55, 0.18);
    backdrop-filter: blur(16px) saturate(180%);
    -webkit-backdrop-filter: blur(16px) saturate(180%);
    border-radius: 18px;
    border: 1.5px solid rgba(51, 65, 85, 0.18);
    padding: 2.2rem 2rem 2rem 2rem;
    margin-bottom: 2rem;
    color: #f1f5f9;
    transition: box-shadow 0.2s, transform 0.2s;
}
.resume-glass-card:hover {
    box-shadow: 0 12px 36px 0 rgba(59, 130, 246, 0.18);
    transform: translateY(-2px) scale(1.01);
}
.resume-upload-drop {
    border: 2.5px dashed #64748b;
    border-radius: 16px;
    background: rgba(51, 65, 85, 0.18);
    padding: 2.5rem 1.5rem;
    text-align: center;
    transition: border-color 0.2s, background 0.2s;
    cursor: pointer;
    position: relative;
    margin-bottom: 1.2rem;
}
.resume-upload-drop:hover {
    border-color: #2563eb;
    background: rgba(37, 99, 235, 0.10);
}
.resume-upload-icon {
    width: 48px; height: 48px; margin-bottom: 0.5rem;
    display: inline-block;
}
.resume-upload-label {
    font-size: 1.1rem;
    color: #e0e7ef;
    font-weight: 500;
}
.resume-upload-desc {
    color: #a5b4fc;
    font-size: 0.95rem;
    margin-bottom: 0.5rem;
}
.resume-upload-btn {
    background: linear-gradient(90deg, #2563eb 0%, #6366f1 100%);
    color: #fff;
    border: none;
    border-radius: 10px;
    padding: 0.85rem 1.5rem;
    font-size: 1.1rem;
    font-weight: 600;
    box-shadow: 0 2px 8px rgba(59,130,246,0.10);
    transition: background 0.18s, box-shadow 0.18s, transform 0.18s;
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
}
.resume-upload-btn:hover {
    background: linear-gradient(90deg, #22d3ee 0%, #a21caf 100%);
    color: #fff;
    box-shadow: 0 4px 16px rgba(139,92,246,0.18);
    transform: translateY(-1px) scale(1.01);
}
.resume-guidelines-grid {
    display: flex;
    gap: 1.2rem;
    flex-wrap: wrap;
    justify-content: space-between;
    margin-bottom: 1.2rem;
}
@media (max-width: 900px) {
    .resume-guidelines-grid { flex-direction: column; gap: 1.2rem; }
}
.resume-guideline-card {
    background: rgba(30, 41, 59, 0.80);
    border-radius: 16px;
    box-shadow: 0 4px 18px 0 rgba(59, 130, 246, 0.10);
    padding: 1.3rem 1.1rem 1.1rem 1.1rem;
    min-width: 220px;
    flex: 1 1 0px;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    transition: box-shadow 0.18s, transform 0.18s;
    border: 1.5px solid rgba(51, 65, 85, 0.18);
    margin-bottom: 0.5rem;
}
.resume-guideline-card:hover {
    box-shadow: 0 8px 32px rgba(16,185,129,0.13);
    transform: scale(1.025);
}
.resume-guideline-icon {
    width: 36px; height: 36px; margin-bottom: 0.5rem;
}
.resume-guideline-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #a5b4fc;
    margin-bottom: 0.2rem;
}
.resume-guideline-desc {
    color: #cbd5e1;
    font-size: 0.97rem;
    margin-bottom: 0.7rem;
}
.resume-guideline-download {
    background: #22d3ee;
    color: #1e293b;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1.1rem;
    font-weight: 600;
    font-size: 1rem;
    margin-top: 0.2rem;
    margin-bottom: 0.2rem;
    box-shadow: 0 2px 8px rgba(16,185,129,0.10);
    transition: background 0.18s, color 0.18s, transform 0.18s;
    cursor: pointer;
}
.resume-guideline-download:hover {
    background: #a21caf;
    color: #fff;
    transform: scale(1.04);
}
.canva-link-btn {
    display: inline-block;
    background: #fff;
    color: #7c3aed;
    border: 2px solid #a21caf;
    border-radius: 8px;
    padding: 0.6rem 1.2rem;
    font-weight: 600;
    font-size: 1.05rem;
    margin-top: 0.7rem;
    margin-bottom: 0.7rem;
    box-shadow: 0 2px 8px rgba(168,85,247,0.10);
    transition: background 0.18s, color 0.18s, border 0.18s, transform 0.18s;
    text-decoration: none !important;
}
.canva-link-btn:hover {
    background: #a21caf;
    color: #fff;
    border: 2px solid #7c3aed;
    transform: scale(1.04);
}
.recent-upload-list {
    display: flex;
    flex-direction: column;
    gap: 1.1rem;
    margin-top: 0.5rem;
}
.recent-upload-card {
    background: rgba(30, 41, 59, 0.80);
    border-radius: 14px;
    box-shadow: 0 2px 8px 0 rgba(59, 130, 246, 0.10);
    padding: 1.1rem 1.1rem 0.7rem 1.1rem;
    display: flex;
    align-items: center;
    gap: 1.1rem;
    border: 1.5px solid rgba(51, 65, 85, 0.18);
    transition: box-shadow 0.18s, transform 0.18s;
}
.recent-upload-card:hover {
    box-shadow: 0 8px 32px rgba(139,92,246,0.13);
    transform: scale(1.015);
}
.recent-upload-icon {
    width: 32px; height: 32px;
    margin-right: 0.7rem;
}
.recent-upload-info {
    flex: 1 1 0px;
    color: #e0e7ef;
}
.recent-upload-date {
    color: #a5b4fc;
    font-size: 0.93rem;
}
@media (max-width: 900px) {
    .recent-upload-list { gap: 0.7rem; }
    .recent-upload-card { flex-direction: column; align-items: flex-start; gap: 0.5rem; }
}
</style>
''', unsafe_allow_html=True)

# Apply authentication requirement
@require_auth()
def main():
    """Main function for the resume upload page"""
    display_sidebar_navigation()
    
    st.markdown(
        """
        <style>
        /* Hide the default Streamlit sidebar navigation */
        [data-testid='stSidebarNav'] { display: none !important; }
        /* Hide the sidebar search input */
        [data-testid='stSidebarSearch'] { display: none !important; }
        /* Hide the sidebar header */
        [data-testid='stSidebarHeader'] { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True
    )

    # --- Responsive two-column layout ---
    col_left, col_right = st.columns([1.15, 1], gap="large")
    with col_left:
        st.markdown('<div class="resume-glass-card">\n<h2 style="margin-bottom:0.2em;">Upload Your Resume</h2>\n<div class="resume-upload-desc">Upload your resume to get started with analysis and booth recommendations.</div>', unsafe_allow_html=True)
        # --- Drag-and-drop upload UI ---
        uploaded_file = st.file_uploader(
            "Drag and drop your PDF resume here or click to select",
            type=["pdf"],
            help="PDF only, max 200MB."
        )
        if uploaded_file is None:
            st.info("No file detected. Drag-and-drop and Browse files are both supported.")
        description = st.text_input(
            "Description (optional)",
            help="Add a short description to identify this resume"
        )
        # --- Upload button with progress ---
        upload_btn = st.button("Upload Resume", key="upload_resume_btn", use_container_width=True)
        # --- File validation and upload logic ---
        file_valid = True
        if upload_btn:
            if uploaded_file is None:
                file_valid = False
                if hasattr(st, "toast"):
                    st.toast("Please select a PDF file to upload.", icon="❌")
                else:
                    st.error("Please select a PDF file to upload.")
            elif not uploaded_file.name.lower().endswith(".pdf"):
                file_valid = False
                if hasattr(st, "toast"):
                    st.toast("Only PDF files are allowed.", icon="❌")
                else:
                    st.error("Only PDF files are allowed.")
            elif uploaded_file.size > 200 * 1024 * 1024:
                file_valid = False
                if hasattr(st, "toast"):
                    st.toast("File size exceeds 200MB limit.", icon="❌")
                else:
                    st.error("File size exceeds 200MB limit.")
        if upload_btn and file_valid and uploaded_file is not None:
            with st.spinner("Uploading and processing your resume..."):
                try:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    status_text.text("Processing file...")
                    progress_bar.progress(10)
                    time.sleep(0.5)
                    original_filename = getattr(uploaded_file, "name", "Unknown")
                    status_text.text("Preparing file for upload...")
                    progress_bar.progress(30)
                    time.sleep(0.5)
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
                        if hasattr(st, "toast"):
                            st.toast("Resume uploaded successfully!", icon="✅")
                        else:
                            st.success("Resume uploaded successfully!")
                        st.session_state.upload_success = True
                    else:
                        status_text.text("Upload failed")
                        progress_bar.empty()
                        status_text.empty()
                        error_msg = response.get('error', 'Unknown error occurred')
                    if hasattr(st, "toast"):
                        st.toast(f"Error uploading resume: {error_msg}", icon="❌")
                    else:
                        st.error(f"Error uploading resume: {error_msg}")
                except Exception as e:
                    pass
        # --- Always show Go to My Resumes button below upload section ---
        if st.button("Go to My Resumes", key="go_to_my_resumes_btn", use_container_width=True):
            try:
                st.switch_page("02_my_resumes.py")
            except Exception:
                try:
                    st.switch_page("pages/02_my_resumes.py")
                except Exception as e:
                    st.error(f"Navigation failed: {e}")
    with col_right:
        st.markdown('<div class="resume-glass-card">\n<h3 style="margin-bottom:0.2em;">Resume Format Guidelines</h3>\n<div style="color:#cbd5e1; font-size:1.01rem; margin-bottom:1.1rem;">Your resume must follow one of the 3 formats below and must be in PDF format for accurate analysis.</div>\n<div class="resume-guidelines-grid">', unsafe_allow_html=True)
        # --- Resume Guidelines: All samples in one card ---
        sample_files = [
            ("Finance Resume", "Perfect for financial analysts, accountants, and banking professionals", "financeResume.pdf", "📊"),
            ("Computer Science Resume", "Ideal for software engineers, developers, and IT professionals", "computerscienceResume.pdf", "💻"),
            ("Medical Resume", "Designed for healthcare professionals, doctors, and medical staff", "medicalResume.pdf", "🏥"),
        ]
        seed_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../database/seeders/assets/resume'))
        for title, desc, filename, icon in sample_files:
            file_path = pathlib.Path(seed_dir) / filename
            if file_path.exists():
                st.markdown(f'''
<div class="resume-guideline-card" style="display:flex;align-items:center;gap:1.1rem;margin-bottom:0.2rem;padding-bottom:0.2rem;flex-direction:column;align-items:flex-start;">
  <div style="display:flex;align-items:center;gap:0.7rem;">
    <span class="resume-guideline-icon">{icon}</span>
    <div>
      <span class="resume-guideline-title" style="font-size:1.08rem;vertical-align:middle;">{title}</span><br>
      <span class="resume-guideline-desc">{desc}</span>
    </div>
  </div>
</div>
''', unsafe_allow_html=True)
                with open(file_path, "rb") as f:
                    st.download_button(
                        label="Download",
                        data=f.read(),
                        file_name=filename,
                        mime="application/pdf",
                        key=filename
                    )
        st.markdown('''<div style="margin-top:1.2em; margin-bottom:0.5em;">
        <b>Want to edit your own resume? Use the Canva link below to create your resume.</b><br>
        <a href="https://www.canva.com/design/DAGnSVLF_pU/RstMgJTQTM0Qe8PR9IOSbQ/edit?utm_content=DAGnSVLF_pU&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton" target="_blank" class="canva-link-btn">Edit Resume in Canva</a>
        </div>''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    # --- Recent Uploads Section ---
    response, success = api.get_user_resumes()
    resumes = []
    if success:
        resumes = response.get('data', [])
    if resumes:
        resumes.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        recent_resumes = [r for r in resumes[:5] if (r.get('file_name') or r.get('filename')) and r.get('created_at')]
        if len(recent_resumes) > 0:
            st.markdown('''
<div class="resume-glass-card" style="margin-top:0.2em;">
  <h4 style="margin-bottom:0.2em; font-size:1.5rem; color:#a5b4fc;">Your Recent Uploads</h4>
  <div class="recent-upload-list">
''', unsafe_allow_html=True)
            for resume_item_recent in recent_resumes:
                file_icon = "<span class='recent-upload-icon'>📄</span>"
                file_name = resume_item_recent.get('file_name', resume_item_recent.get('filename', 'Unnamed Resume'))
                upload_date = resume_item_recent.get('created_at', 'Unknown')
                try:
                    date_obj_utc = datetime.fromisoformat(upload_date.replace('Z', '+00:00'))
                    date_obj_myt = date_obj_utc + timedelta(hours=8)
                    formatted_date = date_obj_myt.strftime("%B %d, %Y at %I:%M %p MYT")
                except:
                    formatted_date = f"{upload_date} (raw UTC)"
                st.markdown(f"""
                <div class='recent-upload-card' style='display:flex;align-items:center;gap:1.1rem;padding:1.1rem 1.1rem 0.7rem 1.1rem;background:rgba(30,41,59,0.80);border-radius:14px;margin-bottom:0.7rem;'>
                    {file_icon}
                    <div class='recent-upload-info' style='flex:1 1 0px;color:#e0e7ef;'>
                        <b style='font-size:1.08rem;'>{file_name}</b><br>
                        <span class='recent-upload-date' style='color:#a5b4fc;font-size:0.93rem;'>Uploaded: {formatted_date}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div></div>', unsafe_allow_html=True)
    elif success:
        st.info("You haven't uploaded any resumes yet.")
    else:
        st.error(f"Error loading resumes: {response.get('error', 'Unknown error')}")
    render_footer()

if __name__ == "__main__":
    main() 