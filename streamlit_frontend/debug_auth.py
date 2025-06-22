import streamlit as st
import requests
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")

st.set_page_config(page_title="Auth Debugger", layout="wide")
st.title("Authentication Debugger")

# Initialize session state
if "user_token" not in st.session_state:
    st.session_state.user_token = None
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Show current auth state
st.header("Current Authentication State")
col1, col2 = st.columns(2)
with col1:
    st.write(f"Authenticated: {st.session_state.get('authenticated', False)}")
    user = st.session_state.get('user', {})
    if user:
        st.write(f"User: {user.get('name')} ({user.get('email')})")
        st.write(f"Role: {user.get('role')}")

with col2:
    token = st.session_state.get('user_token', '')
    if token:
        st.write("Token (first 20 chars):")
        st.code(token[:20] + "..." if len(token) > 20 else token)
        st.write(f"Token length: {len(token)}")
    else:
        st.write("No token in session state")

# Login form
st.header("Login")
with st.form("login_form"):
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Login")

    if submitted:
        try:
            st.write(f"Attempting login for: {email}")
            response = requests.post(
                f"{API_BASE_URL}/login",
                json={"email": email, "password": password},
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                }
            )
            
            st.write(f"Login response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("token", "")
                user = data.get("user", {})
                
                st.session_state.authenticated = True
                st.session_state.user_token = token
                st.session_state.user = user
                
                st.success("Login successful!")
                st.json(data)
            else:
                try:
                    error_data = response.json()
                    st.error(f"Login failed: {error_data.get('message', 'Unknown error')}")
                except:
                    st.error(f"Login failed: {response.status_code} - {response.text[:100]}")
        except Exception as e:
            st.error(f"Exception during login: {str(e)}")

# Test authentication
st.header("Test Authentication")
test_tab1, test_tab2, test_tab3 = st.tabs(["Test with Session Token", "Test with Custom Token", "Test User API"])

with test_tab1:
    st.subheader("Test Protected API with Session Token")
    
    test_endpoint = st.selectbox(
        "Select endpoint to test",
        ["api/resumes", "api/user", "api/job-fairs", "sanctum/csrf-cookie"]
    )
    
    if st.button("Test Session Token"):
        token = st.session_state.get("user_token", "")
        if not token:
            st.error("No token in session. Please login first.")
        else:
            try:
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                }
                
                st.write("Headers being sent:")
                st.json(headers)
                
                full_url = f"{API_BASE_URL.replace('/api', '')}/{test_endpoint}"
                st.write(f"Requesting: {full_url}")
                
                response = requests.get(
                    full_url,
                    headers=headers
                )
                
                st.write(f"Response status: {response.status_code}")
                
                if response.status_code == 200:
                    st.success("Authentication successful!")
                    try:
                        st.json(response.json())
                    except:
                        st.code(response.text)
                else:
                    st.error("Authentication failed")
                    try:
                        st.json(response.json())
                    except:
                        st.code(response.text)
            except Exception as e:
                st.error(f"Exception during API test: {str(e)}")

with test_tab2:
    st.subheader("Test with Custom Token")
    
    custom_token = st.text_input("Enter token to test")
    custom_endpoint = st.selectbox(
        "Select endpoint to test",
        ["api/resumes", "api/user", "api/job-fairs", "sanctum/csrf-cookie"],
        key="custom_endpoint"
    )
    
    if st.button("Test Custom Token"):
        if not custom_token:
            st.error("Please enter a token to test")
        else:
            try:
                headers = {
                    "Authorization": f"Bearer {custom_token}",
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                }
                
                st.write("Headers being sent:")
                st.json(headers)
                
                full_url = f"{API_BASE_URL.replace('/api', '')}/{custom_endpoint}"
                st.write(f"Requesting: {full_url}")
                
                response = requests.get(
                    full_url,
                    headers=headers
                )
                
                st.write(f"Response status: {response.status_code}")
                
                if response.status_code == 200:
                    st.success("Authentication successful!")
                    try:
                        st.json(response.json())
                    except:
                        st.code(response.text)
                else:
                    st.error("Authentication failed")
                    try:
                        st.json(response.json())
                    except:
                        st.code(response.text)
            except Exception as e:
                st.error(f"Exception during API test: {str(e)}")

with test_tab3:
    st.subheader("Test User API")
    
    if st.button("Test User Endpoint"):
        try:
            # Try with and without token
            token = st.session_state.get("user_token", "")
            
            headers_with_token = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            headers_without_token = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            st.write("Testing without token first:")
            response1 = requests.get(
                f"{API_BASE_URL}/user",
                headers=headers_without_token
            )
            
            st.write(f"Response without token: {response1.status_code}")
            try:
                st.json(response1.json())
            except:
                st.code(response1.text[:200])
            
            st.write("Testing with token:")
            st.write(f"Token being used: {token[:20]}...")
            
            response2 = requests.get(
                f"{API_BASE_URL}/user",
                headers=headers_with_token
            )
            
            st.write(f"Response with token: {response2.status_code}")
            try:
                st.json(response2.json())
            except:
                st.code(response2.text[:200])
            
        except Exception as e:
            st.error(f"Exception during user API test: {str(e)}")

# Show JavaScript for debugging localStorage
st.header("Debug Local Storage")
st.markdown("""
<script>
// Print localStorage data to console
document.addEventListener('DOMContentLoaded', function() {
    console.log('localStorage debug:');
    console.log('authenticated:', localStorage.getItem('authenticated'));
    console.log('userToken:', localStorage.getItem('userToken'));
    
    // Show data on page
    const storageData = document.createElement('div');
    storageData.innerHTML = `
        <p>authenticated: ${localStorage.getItem('authenticated')}</p>
        <p>userToken: ${localStorage.getItem('userToken') ? localStorage.getItem('userToken').substring(0, 20) + '...' : 'null'}</p>
    `;
    
    // Append to a div with id 'localStorage-data' that will be created below
    setTimeout(() => {
        const container = document.getElementById('localStorage-data');
        if (container) {
            container.appendChild(storageData);
        }
    }, 500);
});
</script>
<div id="localStorage-data"></div>
""", unsafe_allow_html=True) 