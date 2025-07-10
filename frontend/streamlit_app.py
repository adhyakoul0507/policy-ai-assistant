import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from firebase_config import firebase_config, auth, database
import time
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize session state for persistence
if 'user_authenticated' not in st.session_state:
    st.session_state.user_authenticated = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = None
if 'login_timestamp' not in st.session_state:
    st.session_state.login_timestamp = None

st.set_page_config(
    page_title="Policy Chatbot",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = os.getenv('API_BASE_URL', "http://localhost:5000")

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        color: white;
        text-align: center;
        margin: 0;
        font-size: 2.5rem;
    }
    .main-header p {
        color: white;
        text-align: center;
        margin: 0;
        font-size: 1.2rem;
        margin-top: 0.5rem;
    }
    .feature-card {
        background: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 4px solid #4ECDC4;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        border: 1px solid #c3e6cb;
    }
    .error-message {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        border: 1px solid #f5c6cb;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        text-align: center;
    }
    .stButton > button {
        background: transparent;
        color: #4ECDC4;
        border: 1px solid #4ECDC4;
        border-radius: 5px;
        padding: 0.3rem 0.8rem;
        font-weight: normal;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background: #4ECDC4;
        color: white;
    }
    /* Primary buttons get the gradient styling */
    .stButton button[kind="primary"] {
        background: linear-gradient(90deg, #4ECDC4, #44A08D) !important;
        color: white !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        font-weight: bold !important;
    }
    .stButton button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2) !important;
    }
    .sidebar .stSelectbox {
        background: white;
        border-radius: 8px;
    }
    .user-info {
        background: #ffe6f0;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 4px solid #FF6B6B;
        color: #333;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        max-width: 80%;
    }
    .user-message {
        background: #4ECDC4;
        color: white;
        margin-left: auto;
    }
    .bot-message {
        background: #f8f9fa;
        color: #333;
        border-left: 4px solid #4ECDC4;
    }
    .demo-banner {
        background: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        border: 1px solid #ffeaa7;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def check_auth():
    """Enhanced authentication check with session persistence"""
    # Check for existing session
    if st.session_state.user_authenticated and 'user' in st.session_state and st.session_state.user:
        return True
    
    # Check if Firebase token is still valid
    if 'user' in st.session_state and st.session_state.user:
        try:
            # Try to refresh the token
            if 'refreshToken' in st.session_state.user:
                refreshed_user = auth.refresh(st.session_state.user['refreshToken'])
                st.session_state.user = refreshed_user
                st.session_state.user_authenticated = True
                return True
        except:
            # Token expired or invalid
            st.session_state.user = None
            st.session_state.user_authenticated = False
    
    return False

def auth_section():
    """Authentication section for login/signup with demo mode"""
    st.markdown("""
    <div class="main-header">
        <h1>Policy Chatbot</h1>
        <p>Your AI-powered Government Policy Assistant</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="demo-banner">
        <h4>Quick Demo Mode Available</h4>
        <p>For demonstration purposes, you can skip authentication and explore the features</p>
    </div>
    """, unsafe_allow_html=True)

    col_demo1, col_demo2, col_demo3 = st.columns([1, 2, 1])
    with col_demo2:
        if st.button("Enter Demo Mode (Skip Login)", type="primary", use_container_width=True):
            st.session_state.user = {
                "idToken": "demo_token", 
                "localId": "demo_user",
                "refreshToken": "demo_refresh"
            }
            st.session_state.user_email = "demo@policychatbot.com"
            st.session_state.user_authenticated = True
            st.session_state.login_timestamp = datetime.now()
            st.success("Demo mode activated")
            time.sleep(1)
            st.rerun()

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div class='feature-card'>", unsafe_allow_html=True)
        st.markdown("### Authentication Required")
        
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            st.markdown("#### Welcome Back!")
            email = st.text_input("Email", placeholder="Enter your email")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            # Remember me checkbox
            remember_me = st.checkbox("Remember me for this session")
            
            col_login1, col_login2 = st.columns(2)
            with col_login1:
                if st.button("Login", type="primary", use_container_width=True):
                    if email and password:
                        try:
                            with st.spinner("Logging in..."):
                                user = auth.sign_in_with_email_and_password(email, password)
                                st.session_state.user = {
                                    "idToken": user["idToken"], 
                                    "localId": user["localId"],
                                    "refreshToken": user.get("refreshToken", "")
                                }
                                st.session_state.user_email = email
                                st.session_state.user_authenticated = True
                                st.session_state.login_timestamp = datetime.now()
                                
                                if remember_me:
                                    st.session_state.remember_login = True
                                
                                st.success("Login successful!")
                                time.sleep(1)
                                st.rerun()
                        except Exception as e:
                            error_message = str(e)
                            if "INVALID_LOGIN_CREDENTIALS" in error_message or "INVALID_PASSWORD" in error_message:
                                st.error("Invalid email or password")
                            else:
                                st.error(f"Login failed: {error_message}")
                    else:
                        st.warning("Please fill in all fields")
            
            with col_login2:
                if st.button("Reset Password", use_container_width=True):
                    if email:
                        try:
                            auth.send_password_reset_email(email)
                            st.success("Password reset email sent!")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
                    else:
                        st.warning("Please enter your email first")
        
        with tab2:
            st.markdown("#### Create New Account")
            new_email = st.text_input("Email", placeholder="Enter your email", key="signup_email")
            new_password = st.text_input("Password", type="password", placeholder="Create a password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
            
            if st.button("Create Account", type="primary", use_container_width=True):
                if new_email and new_password and confirm_password:
                    if new_password == confirm_password:
                        if len(new_password) >= 6:
                            try:
                                with st.spinner("Creating account..."):
                                    user = auth.create_user_with_email_and_password(new_email, new_password)
                                    st.success("Account created successfully! Please login.")
                                    time.sleep(1)
                            except Exception as e:
                                error_message = str(e)
                                if "EMAIL_EXISTS" in error_message:
                                    st.error("Email already exists")
                                else:
                                    st.error(f"Error creating account: {error_message}")
                        else:
                            st.error("Password must be at least 6 characters")
                    else:
                        st.error("Passwords do not match")
                else:
                    st.warning("Please fill in all fields")
        
        st.markdown("</div>", unsafe_allow_html=True)

def get_auth_header():
    """Get authentication header for API requests"""
    if check_auth():
        return {
            'Authorization': f'Bearer {st.session_state.user["idToken"]}',
            'Content-Type': 'application/json'
        }
    return {'Content-Type': 'application/json'}

def make_api_request(endpoint, data):
    """Make API request to Flask backend with authentication"""
    try:
        headers = get_auth_header()
        
        response = requests.post(f"{API_BASE_URL}/api/{endpoint}", json=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            st.error("Session expired. Please login again.")
            st.session_state.user = None
            st.session_state.user_authenticated = False
            st.rerun()
        else:
            return {"success": False, "error": f"API Error: {response.status_code}"}
    except requests.exceptions.RequestException as e:
        error_message = str(e).lower()
        if "quota" in error_message or "rate limit" in error_message or "429" in error_message:
            return {"success": False, "error": "API quota exceeded. Please try again later or upgrade your plan."}
        elif "timeout" in error_message:
            return {"success": False, "error": "Request timeout. The API is taking too long to respond."}
        elif "connection" in error_message:
            return {"success": False, "error": "Connection error. Please check your internet connection."}
        else:
            return {"success": False, "error": f"Connection Error: {str(e)}"}

def display_user_info():
    """Display user information in sidebar with session info"""
    if check_auth():
        is_demo = st.session_state.user.get("idToken") == "demo_token"
        user_type = "Demo User" if is_demo else "Authenticated User"
        
        st.sidebar.markdown(f"""
        <div class="user-info">
            <p><strong>User:</strong> {st.session_state.get('user_email', 'Unknown')}</p>
            <p><strong>Type:</strong> {user_type}</p>
            <p><strong>Session:</strong> Active</p>
            {f"<p><strong>Login:</strong> {st.session_state.login_timestamp.strftime('%H:%M')}</p>" if st.session_state.login_timestamp else ""}
        </div>
        """, unsafe_allow_html=True)

def main():
    """Main application function with enhanced session management"""
    
    # Check authentication
    if not check_auth():
        st.session_state.user = None
        st.session_state.user_authenticated = False
        st.rerun()
    
    display_user_info()
    
    st.markdown("""
    <div class="main-header">
        <h1>Policy Chatbot</h1>
        <p>Analyze, Compare, and Understand Government Policies</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.title("Choose a Feature")
    
    feature = st.sidebar.selectbox(
        "Select Feature",
        [
            "Policy Comparison",
            "Sentiment Analysis",
            "Eligibility Checker",
            "Regional Policies",
            "General Query"
        ]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Language Settings**")
    language_preference = st.sidebar.selectbox(
        "Preferred Language",
        ["English", "Hindi", "Punjabi"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Location Settings**")
    state = st.sidebar.selectbox(
        "Select State",
        [
            "Andhra Pradesh", "Assam", "Bihar", "Chhattisgarh", "Gujarat",
            "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala",
            "Maharashtra", "Odisha", "Punjab", "Rajasthan", "Tamil Nadu",
            "Uttar Pradesh", "West Bengal", "Delhi", "Goa"
        ]
    )
    
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.user = None
        st.session_state.user_email = None
        st.session_state.user_authenticated = False
        st.session_state.login_timestamp = None
        st.success("Logged out successfully!")
        time.sleep(1)
        st.rerun()
    
    if feature == "Policy Comparison":
        policy_comparison()
    elif feature == "Sentiment Analysis":
        sentiment_analysis()
    elif feature == "Eligibility Checker":
        eligibility_checker()
    elif feature == "Regional Policies":
        regional_policies(state)
    elif feature == "General Query":
        general_query(language_preference)

# [Keep all your existing functions: policy_comparison, sentiment_analysis, etc. - they remain exactly the same]

def policy_comparison():
    """Policy comparison feature"""
    st.header("Policy vs Policy Comparison")
    
    if 'policy1' not in st.session_state:
        st.session_state.policy1 = ""
    if 'policy2' not in st.session_state:
        st.session_state.policy2 = ""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Policy 1")
        
        st.write("**Popular Policies:**")
        if st.button("MNREGA", key="mnrega1"):
            st.session_state.policy1 = "MNREGA"
        if st.button("PM-KISAN", key="pmkisan1"):
            st.session_state.policy1 = "PM-KISAN"
        if st.button("Ayushman Bharat", key="ayushman1"):
            st.session_state.policy1 = "Ayushman Bharat"
        
        policy1 = st.text_input("Enter first policy name", value=st.session_state.policy1, placeholder="e.g., MNREGA", key="policy1_input")
        st.session_state.policy1 = policy1
    
    with col2:
        st.subheader("Policy 2")
        
        st.write("**Popular Policies:**")
        if st.button("Jan Aushadhi Yojana", key="jan_aushadhi2"):
            st.session_state.policy2 = "Jan Aushadhi Yojana"
        if st.button("Pradhan Mantri Awas Yojana", key="awas2"):
            st.session_state.policy2 = "Pradhan Mantri Awas Yojana"
        if st.button("Swachh Bharat Mission", key="swachh2"):
            st.session_state.policy2 = "Swachh Bharat Mission"
        
        policy2 = st.text_input("Enter second policy name", value=st.session_state.policy2, placeholder="e.g., PM-KISAN", key="policy2_input")
        st.session_state.policy2 = policy2
    
    if st.button("Compare Policies", type="primary"):
        if policy1 and policy2:
            with st.spinner("Analyzing policies..."):
                result = make_api_request("compare-policies", {
                    "policy1": policy1,
                    "policy2": policy2
                })
                
                if result.get("success"):
                    st.success("Analysis Complete!")
                    
                    st.markdown("---")
                    st.subheader("Policy Comparison Analysis")
                    st.markdown(result["comparison"])
                else:
                    st.error(f"Error: {result.get('error', 'Unknown error')}")
        else:
            st.warning("Please enter both policy names")

def sentiment_analysis():
    """Sentiment analysis feature"""
    st.header("Sentiment & Stakeholder Analysis")
    
    if 'sentiment_policy' not in st.session_state:
        st.session_state.sentiment_policy = ""
    
    st.write("**Quick Select:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("MNREGA", key="mnrega_sentiment"):
            st.session_state.sentiment_policy = "MNREGA"
    with col2:
        if st.button("PM-KISAN", key="pmkisan_sentiment"):
            st.session_state.sentiment_policy = "PM-KISAN"
    with col3:
        if st.button("Ayushman Bharat", key="ayushman_sentiment"):
            st.session_state.sentiment_policy = "Ayushman Bharat"
    
    policy_name = st.text_input("Enter policy name", value=st.session_state.sentiment_policy, placeholder="e.g., Ayushman Bharat", key="sentiment_input")
    st.session_state.sentiment_policy = policy_name
    
    if st.button("Analyze Sentiment", type="primary"):
        if policy_name:
            with st.spinner("Analyzing stakeholder sentiment..."):
                result = make_api_request("sentiment-analysis", {
                    "policy_name": policy_name
                })
                
                if result.get("success"):
                    st.success("Analysis Complete!")
                    
                    st.markdown("---")
                    st.subheader("Sentiment Analysis Results")
                    st.markdown(result["analysis"])
                else:
                    st.error(f"Error: {result.get('error', 'Unknown error')}")
        else:
            st.warning("Please enter a policy name")

def eligibility_checker():
    """Eligibility checker feature"""
    st.header("Government Scheme Eligibility Checker")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Personal Information")
        age = st.number_input("Age", min_value=0, max_value=100, value=30)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        income = st.number_input("Annual Income (₹)", min_value=0, value=200000)
        occupation = st.selectbox("Occupation", [
            "Farmer", "Student", "Employee", "Business", "Unemployed",
            "Self-employed", "Retired", "Other"
        ])
    
    with col2:
        st.subheader("Location & Background")
        caste = st.selectbox("Category", ["General", "OBC", "SC", "ST", "EWS"])
        location = st.selectbox("Location Type", ["Urban", "Rural"])
        state = st.selectbox("State", [
            "Andhra Pradesh", "Bihar", "Gujarat", "Haryana", "Karnataka",
            "Maharashtra", "Punjab", "Rajasthan", "Tamil Nadu", "Uttar Pradesh"
        ])
        
        family_size = st.number_input("Family Size", min_value=1, max_value=20, value=4)
    
    if st.button("Check Eligibility", type="primary"):
        with st.spinner("Checking eligibility for government schemes..."):
            result = make_api_request("check-eligibility", {
                "age": age,
                "gender": gender,
                "income": income,
                "caste": caste,
                "occupation": occupation,
                "state": state,
                "location": location.lower()
            })
            
            if result.get("success"):
                st.success("Eligibility Check Complete!")
                
                eligible_schemes = result.get("eligible_schemes", [])
                
                if eligible_schemes:
                    st.markdown("---")
                    st.subheader("You are eligible for:")
                    
                    for i, scheme in enumerate(eligible_schemes):
                        with st.expander(f"{scheme['name']}"):
                            st.write(f"**Benefits:** {scheme['benefits']}")
                            st.write(f"**Application:** {scheme['application']}")
                            st.write("**Criteria:** " + ", ".join([f"{k}: {v}" for k, v in scheme['criteria'].items()]))
                    
                    st.markdown("---")
                    st.subheader("Detailed Analysis")
                    st.markdown(result["detailed_analysis"])
                
                else:
                    st.warning("No schemes found matching your criteria. Please check the detailed analysis below for suggestions.")
                    st.markdown(result["detailed_analysis"])
                    
            else:
                st.error(f"Error: {result.get('error', 'Unknown error')}")

def regional_policies(state):
    """Regional policies feature"""
    st.header(f"Regional Policy Insights: {state}")
    
    with st.spinner("Fetching regional policy details..."):
        result = make_api_request("regional-policies", {
            "state": state
        })

        if result.get("success"):
            st.success("Regional Information Retrieved!")

            st.markdown("---")
            st.subheader("Regional Policy Details")
            st.markdown(result["regional_info"])
        else:
            st.error(f"Error: {result.get('error', 'Unknown error')}")

def general_query(language_preference):
    """General query feature"""
    st.header("General Policy Query")
    
    if 'query_text' not in st.session_state:
        st.session_state.query_text = ""
    
    st.write("**Popular Questions:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("What is the GST structure in India?", key="gst_query"):
            st.session_state.query_text = "What is the GST structure in India?"
        if st.button("How does the PM Awas Yojana work?", key="awas_query"):
            st.session_state.query_text = "How does the PM Awas Yojana work?"
        if st.button("What are the benefits of Digital India?", key="digital_query"):
            st.session_state.query_text = "What are the benefits of Digital India?"
    
    with col2:
        if st.button("How to apply for Ayushman Bharat?", key="ayushman_query"):
            st.session_state.query_text = "How to apply for Ayushman Bharat?"
        if st.button("What is the status of farm laws?", key="farm_query"):
            st.session_state.query_text = "What is the status of farm laws?"
        if st.button("How does the new education policy work?", key="nep_query"):
            st.session_state.query_text = "How does the new education policy work?"
    
    query = st.text_area("Ask any policy-related question:", value=st.session_state.query_text,
                        placeholder="e.g., What are the benefits of Digital India initiative?",
                        height=100, key="query_input")
    st.session_state.query_text = query
    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("Get Answer", type="primary"):
            if query:
                with st.spinner("Searching for answer..."):
                    result = make_api_request("general-query", {
                        "query": query,
                        "language": language_preference
                    })
                    
                    if result.get("success"):
                        st.success("Answer Retrieved!")
                        
                        st.markdown("---")
                        st.subheader("Answer")
                        st.markdown(result["answer"])
                        
                        st.markdown("---")
                        st.subheader("Related Topics")
                        st.write("• Government Schemes Portal")
                        st.write("• Policy Implementation Guidelines")
                        st.write("• Budget Allocation Reports")
                        st.write("• Ministry Contact Information")
                        
                    else:
                        st.error(f"Error: {result.get('error', 'Unknown error')}")
            else:
                st.warning("Please enter a question")
    
    with col_btn2:
        if st.button("Test Quota Error"):
            st.error("API quota exceeded. Please try again later or upgrade your plan.")

def show_footer():
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p><strong>Policy Chatbot</strong> | Built with Streamlit & Flask | Powered by Google Gemini</p>
        <p>Firebase + Google IDX + Render</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    if not check_auth():
        auth_section()
    else:
        main()
        show_footer()
