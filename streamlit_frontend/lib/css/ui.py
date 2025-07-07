"""
CSS UI Module for Resume Analyzer Application.
This module provides functions to load and apply CSS to the Streamlit app.
"""

import streamlit as st
from streamlit.components.v1 import html
import os

def load_css():
    """
    Load global CSS for the application.
    This should be called AFTER st.set_page_config.
    """
    # Add CSS styles
    st.markdown("""
    <style>
        /* Loading animation for processing status */
        .loading-pulse {
            background: linear-gradient(90deg, #0ea5e9 0%, #7dd3fc 50%, #0ea5e9 100%);
            background-size: 200% 100%;
            animation: gradient-move 1.5s infinite ease-in-out;
            border-radius: 2px;
        }
        
        @keyframes gradient-move {
            0% {
                background-position: 0% 50%;
            }
            50% {
                background-position: 100% 50%;
            }
            100% {
                background-position: 0% 50%;
            }
        }
        
        /* Job fair card styles */
        .job-fair-card {
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .job-fair-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
        }
        
        .job-fair-status {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 50px;
            font-size: 0.8rem;
            font-weight: 500;
            margin-bottom: 0.5rem;
        }
        
        .status-current {
            background-color: #dcfce7;
            color: #166534;
        }
        
        .status-upcoming {
            background-color: #e0f2fe;
            color: #075985;
        }
        
        .status-past {
            background-color: #f1f5f9;
            color: #64748b;
        }
        
        /* Additional styles for theme variables */
        .loading-pulse {
            background: linear-gradient(90deg, var(--accent-color, #0ea5e9) 0%, var(--primary-light, #7dd3fc) 50%, var(--accent-color, #0ea5e9) 100%);
        }
        
        .job-fair-card {
            background-color: var(--card-bg, white);
            border-radius: var(--border-radius, 12px);
            box-shadow: var(--shadow, 0 4px 8px rgba(0, 0, 0, 0.1));
        }
        
        .status-current {
            background-color: rgba(16, 185, 129, 0.2);
            color: var(--success-color, #166534);
        }
        
        .status-upcoming {
            background-color: rgba(14, 165, 233, 0.2);
            color: var(--accent-color, #075985);
        }
        
        .status-past {
            background-color: rgba(100, 116, 139, 0.2);
            color: var(--text-light, #64748b);
        }
    </style>
    """, unsafe_allow_html=True)

def load_local_css(css_file_path):
    """
    Load CSS from a file.
    This is useful for loading external CSS files.
    
    Args:
        css_file_path (str): Path to the CSS file
    """
    if os.path.exists(css_file_path):
        with open(css_file_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"CSS file not found: {css_file_path}")

def add_html_js(content):
    """
    Safely add HTML or JavaScript to the page
    
    Args:
        content (str): HTML or JavaScript content
    """
    html(content)

def apply_theme_css():
    """
    Apply CSS for theme handling to the Streamlit app.
    This injects JavaScript that checks localStorage for theme preference.
    """
    theme_js = """
    <script>
        // Function to apply the theme (light or dark)
        function applyTheme() {
            // Get theme from localStorage or default to light
            const theme = localStorage.getItem('theme') || 'light';
            
            // Set data-theme attribute on document elements
            document.documentElement.setAttribute('data-theme', theme);
            document.body.setAttribute('data-theme', theme);
            
            console.log(`Applied theme: ${theme}`);
        }
        
        // Apply theme on page load
        document.addEventListener('DOMContentLoaded', applyTheme);
        
        // Also try to apply theme immediately
        applyTheme();
    </script>
    """
    
    # Inject the script
    html(theme_js)

def load_custom_font():
    """
    Load custom fonts for the application.
    This injects CSS that imports and applies custom fonts.
    """
    font_css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        :root {
            --font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        html, body, .stApp, .st-emotion-cache-all {
            font-family: var(--font-family) !important;
        }
    </style>
    """
    
    # Inject the CSS
    html(font_css)

def apply_responsive_layout():
    """
    Apply CSS to enhance the responsiveness of the layout.
    """
    responsive_css = """
    <style>
        /* Responsive layout adjustments */
        @media (max-width: 768px) {
            /* Make columns stack on mobile */
            .row-widget > div {
                flex-direction: column !important;
            }
            
            /* Full width for inputs on mobile */
            .stTextInput, .stSelectbox, .stMultiselect {
                width: 100% !important;
            }
        }
    </style>
    """
    
    # Inject the CSS
    html(responsive_css)

def style_authentication_forms():
    """
    Apply custom styling to authentication forms.
    """
    auth_css = """
    <style>
        /* Authentication form styling */
        form[data-testid="stForm"] {
            background-color: var(--card-bg);
            padding: 1.5rem;
            border-radius: var(--border-radius);
            box-shadow: var(--shadow);
        }
        
        form[data-testid="stForm"] .stButton button {
            width: 100%;
            background-color: var(--primary-color);
            color: white;
        }
    </style>
    """
    
    # Inject the CSS
    html(auth_css)

def apply_complete_styling():
    """
    Apply all styling to the application at once.
    """
    load_css()
    load_custom_font()
    apply_responsive_layout()
    style_authentication_forms() 