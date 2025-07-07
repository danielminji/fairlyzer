"""
Authentication Token Fix Utility

This script helps diagnose and fix authentication token issues by:
1. Testing token formats
2. Verifying authentication with the API
3. Repairing localStorage tokens
4. Forcing token refresh
"""

import streamlit as st
import requests
import json
import time
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")

# Set page config - MUST BE FIRST
st.set_page_config(
    page_title="Auth Token Fix",
    page_icon="🔐",
    layout="wide"
)

# Initialize session state
if "user_token" not in st.session_state:
    st.session_state.user_token = None
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "debugging_active" not in st.session_state:
    st.session_state.debugging_active = False

st.title("Authentication Token Fix Utility")

# Instructions
st.markdown("""
This tool helps diagnose and fix authentication issues with the Laravel API.

Common issues include:
- Missing or malformed authentication tokens
- CORS issues with the API
- Token expiration problems
- localStorage inconsistencies
""")

# Login form 
with st.expander("Step 1: Login and Get Fresh Token", expanded=not st.session_state.authenticated):
    st.subheader("Login to get a fresh token")
    
    col1, col2 = st.columns(2)
    with col1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/login",
                        json={"email": email, "password": password},
                        headers={
                            "Accept": "application/json",
                            "Content-Type": "application/json"
                        }
                    )
                    
                    st.write(f"Response status: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        token = data.get("token", "")
                        user = data.get("user", {})
                        
                        st.session_state.authenticated = True
                        st.session_state.user_token = token
                        st.session_state.user = user
                        
                        st.success("Login successful")
                        
                        # Save token to localStorage
                        js_code = f"""
                        <script>
                            localStorage.setItem('authenticated', 'true');
                            localStorage.setItem('userToken', '{token}');
                            localStorage.setItem('userData', '{json.dumps(user)}');
                            localStorage.setItem('lastActive', '{time.time()}');
                            console.log('Saved auth data to localStorage');
                        </script>
                        """
                        st.markdown(js_code, unsafe_allow_html=True)
                        
                        st.experimental_rerun()
                    else:
                        st.error(f"Login failed: {response.status_code}")
                        try:
                            st.error(response.json().get("message", "Unknown error"))
                        except:
                            st.error(response.text[:200])
                except Exception as e:
                    st.error(f"Error during login: {str(e)}")
    
    with col2:
        if st.session_state.authenticated:
            st.success("Authenticated!")
            token = st.session_state.get("user_token", "")
            if token:
                st.write("Token (first 20 chars):")
                st.code(token[:20] + "..." if len(token) > 20 else token)
                st.write(f"Token length: {len(token)}")
                
                user = st.session_state.get("user", {})
                if user:
                    st.write(f"User: {user.get('name')} ({user.get('email')})")
                    st.write(f"Role: {user.get('role')}")
                
                if st.button("Logout"):
                    st.session_state.authenticated = False
                    st.session_state.user_token = None
                    st.session_state.user = None
                    
                    js_code = """
                    <script>
                        localStorage.removeItem('authenticated');
                        localStorage.removeItem('userToken');
                        localStorage.removeItem('userData');
                        localStorage.removeItem('lastActive');
                        console.log('Cleared auth data from localStorage');
                    </script>
                    """
                    st.markdown(js_code, unsafe_allow_html=True)
                    
                    st.experimental_rerun()
            else:
                st.warning("No token found despite being authenticated")
        else:
            st.info("Please log in to get a token")

# Test endpoints
with st.expander("Step 2: Test API Endpoints", expanded=st.session_state.authenticated):
    st.subheader("Test API Authentication")
    
    test_endpoints = [
        "api/user",
        "api/auth-debug",
        "api/auth-test",
        "api/resumes",
        "sanctum/csrf-cookie"
    ]
    
    test_endpoint = st.selectbox("Select endpoint to test", test_endpoints)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Test Current Token"):
            token = st.session_state.get("user_token", "")
            if not token:
                st.error("No token available")
            else:
                try:
                    headers = {
                        "Authorization": f"Bearer {token}",
                        "Accept": "application/json",
                        "Content-Type": "application/json"
                    }
                    
                    st.write("Headers:")
                    st.json(headers)
                    
                    full_url = f"{API_BASE_URL.replace('/api', '')}/{test_endpoint}"
                    st.write(f"Requesting: {full_url}")
                    
                    response = requests.get(
                        full_url,
                        headers=headers
                    )
                    
                    st.write(f"Response status: {response.status_code}")
                    
                    if response.status_code == 200:
                        st.success("Success!")
                        try:
                            st.json(response.json())
                        except:
                            st.code(response.text)
                    else:
                        st.error("Failed")
                        try:
                            st.json(response.json())
                        except:
                            st.code(response.text)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with col2:
        st.subheader("Debug Token Format")
        
        token = st.session_state.get("user_token", "")
        if token:
            if " " in token:
                st.warning("⚠️ Token contains spaces")
            if "Bearer " in token:
                st.warning("⚠️ Token contains 'Bearer' prefix")
            if len(token) < 20:
                st.warning("⚠️ Token seems too short")
            
            # Check if it's a valid Sanctum token format
            if re.match(r'\d+\|[A-Za-z0-9]{40}', token):
                st.success("✓ Token has valid Sanctum format")
            else:
                st.warning("⚠️ Token doesn't match expected Sanctum format")
        else:
            st.info("No token to debug")

# Fix localStorage and session state
with st.expander("Step 3: Fix Authentication Storage", expanded=False):
    st.subheader("Repair localStorage and Session State")
    
    st.markdown("""
    This section helps repair authentication storage issues by:
    1. Synchronizing localStorage with session state
    2. Forcing a token refresh
    3. Clearing corrupted data
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("View localStorage Data"):
            # Use JavaScript to display localStorage data
            st.markdown("""
            <script>
                // Get localStorage data
                const authenticated = localStorage.getItem('authenticated');
                const userToken = localStorage.getItem('userToken');
                const userData = localStorage.getItem('userData');
                const lastActive = localStorage.getItem('lastActive');
                
                // Create a div to display data
                const div = document.createElement('div');
                div.innerHTML = `
                    <h4>localStorage Data:</h4>
                    <p>authenticated: ${authenticated || 'null'}</p>
                    <p>userToken: ${userToken ? userToken.substring(0, 20) + '...' : 'null'} (${userToken ? userToken.length : 0} chars)</p>
                    <p>userData: ${userData ? JSON.stringify(JSON.parse(userData), null, 2) : 'null'}</p>
                    <p>lastActive: ${lastActive ? new Date(parseInt(lastActive)).toLocaleString() : 'null'}</p>
                `;
                
                // Append to a special element
                setTimeout(() => {
                    const container = document.getElementById('localstorage-data');
                    if (container) {
                        container.innerHTML = '';
                        container.appendChild(div);
                    }
                }, 500);
            </script>
            <div id="localstorage-data">Loading localStorage data...</div>
            """, unsafe_allow_html=True)
        
        if st.button("Fix localStorage"):
            token = st.session_state.get("user_token", "")
            user = st.session_state.get("user", {})
            
            if token and user:
                # Update localStorage from session state
                js_code = f"""
                <script>
                    localStorage.setItem('authenticated', 'true');
                    localStorage.setItem('userToken', '{token}');
                    localStorage.setItem('userData', '{json.dumps(user)}');
                    localStorage.setItem('lastActive', '{time.time()}');
                    console.log('Updated localStorage from session state');
                    
                    // Show confirmation
                    const container = document.getElementById('fix-confirmation');
                    if (container) {{
                        container.innerHTML = '<div style="color: green; margin-top: 10px;">✓ localStorage updated successfully</div>';
                    }}
                </script>
                <div id="fix-confirmation"></div>
                """
                st.markdown(js_code, unsafe_allow_html=True)
                st.success("localStorage updated from session state")
            else:
                st.error("No valid token or user data in session state")
    
    with col2:
        if st.button("Force Token Refresh"):
            # Call the user endpoint to get a fresh token
            token = st.session_state.get("user_token", "")
            
            if token:
                try:
                    headers = {
                        "Authorization": f"Bearer {token}",
                        "Accept": "application/json"
                    }
                    
                    response = requests.get(
                        f"{API_BASE_URL}/user",
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        new_token = data.get("token", "")
                        user = data.get("user", {})
                        
                        if new_token:
                            st.session_state.user_token = new_token
                            st.session_state.user = user
                            
                            # Update localStorage with new token
                            js_code = f"""
                            <script>
                                localStorage.setItem('authenticated', 'true');
                                localStorage.setItem('userToken', '{new_token}');
                                localStorage.setItem('userData', '{json.dumps(user)}');
                                localStorage.setItem('lastActive', '{time.time()}');
                                console.log('Updated token in localStorage');
                                
                                // Show confirmation
                                const container = document.getElementById('refresh-confirmation');
                                if (container) {{
                                    container.innerHTML = '<div style="color: green; margin-top: 10px;">✓ Token refreshed successfully</div>';
                                }}
                            </script>
                            <div id="refresh-confirmation"></div>
                            """
                            st.markdown(js_code, unsafe_allow_html=True)
                            
                            st.success(f"Token refreshed. New token length: {len(new_token)}")
                        else:
                            st.warning("No new token received from server")
                    else:
                        st.error(f"Failed to refresh token: {response.status_code}")
                        try:
                            st.error(response.json().get("message", "Unknown error"))
                        except:
                            st.error(response.text[:200])
                except Exception as e:
                    st.error(f"Error refreshing token: {str(e)}")
            else:
                st.error("No token available")
        
        if st.button("Clear All Auth Data"):
            # Clear session state
            st.session_state.authenticated = False
            st.session_state.user_token = None
            st.session_state.user = None
            
            # Clear localStorage
            js_code = """
            <script>
                localStorage.removeItem('authenticated');
                localStorage.removeItem('userToken');
                localStorage.removeItem('userData');
                localStorage.removeItem('lastActive');
                console.log('Cleared all auth data');
                
                // Show confirmation
                const container = document.getElementById('clear-confirmation');
                if (container) {
                    container.innerHTML = '<div style="color: green; margin-top: 10px;">✓ All auth data cleared</div>';
                }
            </script>
            <div id="clear-confirmation"></div>
            """
            st.markdown(js_code, unsafe_allow_html=True)
            
            st.success("All authentication data cleared")

# Real-time connection test
with st.expander("Step 4: Test API Connection", expanded=False):
    st.subheader("Test Connection to API")
    
    if st.button("Run Connection Test"):
        st.session_state.debugging_active = True
    
    if st.session_state.debugging_active:
        # Create a placeholder for results
        results = st.empty()
        
        # Run tests sequentially
        test_results = []
        
        # Test 1: Basic connectivity
        try:
            results.info("Testing basic connectivity...")
            response = requests.get(
                f"{API_BASE_URL.replace('/api', '')}/sanctum/csrf-cookie",
                timeout=5
            )
            test_results.append((
                "Basic connectivity", 
                "✅ Success" if response.status_code == 200 else f"❌ Failed ({response.status_code})"
            ))
        except Exception as e:
            test_results.append(("Basic connectivity", f"❌ Error: {str(e)}"))
        
        # Test 2: CORS headers
        try:
            results.info("Testing CORS headers...")
            response = requests.options(
                f"{API_BASE_URL}/auth-debug",
                headers={
                    "Origin": "http://localhost:8501",
                    "Access-Control-Request-Method": "GET",
                    "Access-Control-Request-Headers": "Authorization"
                },
                timeout=5
            )
            
            cors_headers = [
                "Access-Control-Allow-Origin",
                "Access-Control-Allow-Methods",
                "Access-Control-Allow-Headers",
                "Access-Control-Allow-Credentials"
            ]
            
            missing_headers = [h for h in cors_headers if h not in response.headers]
            
            if not missing_headers:
                test_results.append(("CORS headers", "✅ All required headers present"))
            else:
                test_results.append(("CORS headers", f"❌ Missing headers: {', '.join(missing_headers)}"))
        except Exception as e:
            test_results.append(("CORS headers", f"❌ Error: {str(e)}"))
        
        # Test 3: Auth endpoint
        try:
            results.info("Testing auth endpoint...")
            token = st.session_state.get("user_token", "")
            
            if token:
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/json"
                }
                
                response = requests.get(
                    f"{API_BASE_URL}/auth-debug",
                    headers=headers,
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    auth_header_exists = data.get("auth_header_exists", False)
                    token_exists = data.get("token_exists", False)
                    auth_check = data.get("auth_check", False)
                    
                    if auth_header_exists and token_exists and auth_check:
                        test_results.append(("Auth verification", "✅ Complete authentication success"))
                    elif auth_header_exists and token_exists:
                        test_results.append(("Auth verification", "⚠️ Headers and token OK, but auth check failed"))
                    elif auth_header_exists:
                        test_results.append(("Auth verification", "⚠️ Auth header received but token extraction failed"))
                    else:
                        test_results.append(("Auth verification", "❌ Auth header not received by server"))
                else:
                    test_results.append(("Auth verification", f"❌ Failed with status {response.status_code}"))
            else:
                test_results.append(("Auth verification", "❌ No token available for testing"))
        except Exception as e:
            test_results.append(("Auth verification", f"❌ Error: {str(e)}"))
        
        # Display test results
        result_md = "## Connection Test Results\n\n"
        for test, result in test_results:
            result_md += f"**{test}**: {result}\n\n"
        
        results.markdown(result_md)
        
        if all("✅" in result for _, result in test_results):
            st.success("🎉 All tests passed! Authentication should be working properly.")
        elif any("❌" in result for _, result in test_results):
            st.error("Some tests failed. See details above.")
        else:
            st.warning("Tests completed with some warnings. Authentication may still work.")

# Help and information
st.markdown("""
---
### Next Steps

If you're still having authentication issues:

1. **Clear all auth data** and try logging in again
2. **Restart both the Laravel API server** and the Streamlit server
3. Check Laravel logs for detailed authentication errors
4. Verify your database connection is working properly

Remember to always check the Laravel logs for detailed authentication debugging information.
""") 