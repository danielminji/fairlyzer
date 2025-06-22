#!/usr/bin/env python

"""
Resume Analyzer & Booth Recommendations - Library

This package contains the core functionality for the Resume Analyzer application.
"""

# Import main modules
# from .analyzer import ResumeAnalyzer, analyzer, analyze_resume_file, analyze_resume_bytes, match_resume_to_booths
from .enhanced_parser import EnhancedParser

# Import API client
from . import api

# Import authentication client
from . import auth_client

# Import modules for better package organization
from .api import (
    API_BASE_URL,
    # get_auth_headers,
    get_job_fair_details,
    get_job_fair_booths,
    get_resume,
    get_resume_analysis,
    get_resume_analysis_with_fallback,
    debug_resume_analysis
)

from .auth_client import (
    check_auth,
    init_session,
    login,
    logout,
    get_current_user,
    is_admin,
    is_organizer,
    is_job_seeker,
    require_auth
)

from .ui_components import (
    load_css,
    render_header,
    render_footer,
    render_sidebar,
    render_status_indicator,
    render_card,
    render_job_fair_card,
    render_booth_card,
    render_resume_card,
    render_user_card,
    render_admin_card,
    render_tabs,
    handle_api_error
)

__all__ = [
    # Analyzer
    # 'ResumeAnalyzer',
    # 'analyzer',
    # 'analyze_resume_file',
    # 'analyze_resume_bytes',
    # 'match_resume_to_booths',
    'EnhancedParser',
    
    # API
    'api',
    'API_BASE_URL',
    # 'get_auth_headers',
    'get_job_fair_details',
    'get_job_fair_booths',
    'get_resume',
    'get_resume_analysis',
    'get_resume_analysis_with_fallback',
    'debug_resume_analysis',
    
    # Auth
    'auth_client',
    'check_auth',
    'init_session',
    'login',
    'logout',
    'get_current_user',
    'is_admin',
    'is_organizer',
    'is_job_seeker',
    'require_auth',
    
    # UI Components
    'load_css',
    'render_header',
    'render_footer',
    'render_sidebar',
    'render_status_indicator',
    'render_card',
    'render_job_fair_card',
    'render_booth_card',
    'render_resume_card',
    'render_user_card',
    'render_admin_card',
    'render_tabs',
    'handle_api_error'
]

# Define version
__version__ = '1.0.0' 

# This file makes Python treat the 'lib' directory as a package. 