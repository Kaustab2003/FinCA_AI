"""
Login Page for FinCA AI
Handles user authentication
"""

import streamlit as st
from src.services.auth_service import AuthService
from src.utils.session_manager import SessionManager
from src.utils.logger import logger


def show_login():
    """Display login page"""
    
    # Custom CSS for login page
    st.markdown("""
    <style>
        .login-container {
            max-width: 500px;
            margin: 0 auto;
            padding: 2rem;
        }
        .login-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        .login-header h1 {
            color: #667eea;
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        .login-header p {
            color: #666;
            font-size: 1.1rem;
        }
        .stButton button {
            width: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 0.75rem 1rem;
            font-size: 1rem;
            font-weight: 600;
            border-radius: 8px;
            transition: all 0.3s;
        }
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        .divider {
            text-align: center;
            margin: 1.5rem 0;
            color: #999;
        }
        .link-button {
            text-align: center;
            margin-top: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="login-header">
        <h1>💰 FinCA AI</h1>
        <p>Your Personal Finance Copilot for India</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize auth service
    auth_service = AuthService()
    
    # Login form
    with st.form("login_form", clear_on_submit=False):
        st.subheader("Welcome Back!")
        
        email = st.text_input(
            "Email Address",
            placeholder="your.email@example.com",
            help="Enter your registered email address"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            help="Your account password"
        )
        
        col1, col2 = st.columns([3, 2])
        with col1:
            remember_me = st.checkbox("Remember me")
        with col2:
            if st.form_submit_button("Forgot Password?", type="secondary"):
                st.session_state.show_reset_password = True
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        submitted = st.form_submit_button("🔐 Login", type="primary")
        
        if submitted:
            if not email or not password:
                st.error("⚠️ Please enter both email and password")
            else:
                # Normalize email
                email = email.lower().strip()
                
                with st.spinner("Authenticating..."):
                    success, message, user_data = auth_service.sign_in(email, password)
                    
                    if success and user_data:
                        # Initialize session
                        SessionManager.init_user_session(user_data)
                        st.success(f"✅ {message}")
                        st.balloons()
                        
                        # Log successful login
                        logger.info(f"User logged in: {email}")
                        
                        # Short delay to show success message
                        import time
                        time.sleep(1)
                        
                        # Redirect to dashboard
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
                        logger.warning(f"Failed login attempt: {email}")
    
    # Divider
    st.markdown('<div class="divider">────────  OR  ────────</div>', unsafe_allow_html=True)
    
    # Register link
    st.markdown('<div class="link-button">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📝 Create New Account", use_container_width=True):
            st.session_state.show_register = True
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Info section
    with st.expander("ℹ️ About FinCA AI"):
        st.markdown("""
        **FinCA AI** is your intelligent financial companion that helps you:
        - 📊 Track budgets and expenses
        - 🎯 Set and achieve financial goals
        - 💬 Get personalized financial advice
        - 📈 Plan investments and savings
        - 💳 Manage credit cards and bills
        
        **Secure & Private**: Your data is encrypted and protected with industry-standard security.
        """)


def show_reset_password_section():
    """Display password reset section"""
    st.markdown("""
    <div class="login-header">
        <h1>🔑 Reset Password</h1>
        <p>Enter your email to receive reset instructions</p>
    </div>
    """, unsafe_allow_html=True)
    
    auth_service = AuthService()
    
    with st.form("reset_password_form"):
        email = st.text_input(
            "Email Address",
            placeholder="your.email@example.com",
            help="We'll send a password reset link to this email"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("📧 Send Reset Link", type="primary", use_container_width=True)
        with col2:
            if st.form_submit_button("← Back to Login", type="secondary", use_container_width=True):
                st.session_state.show_reset_password = False
                st.rerun()
        
        if submitted:
            if not email:
                st.error("⚠️ Please enter your email address")
            else:
                # Normalize email
                email = email.lower().strip()
                
                with st.spinner("Sending reset email..."):
                    success, message = auth_service.reset_password(email)
                    if success:
                        st.success(f"✅ {message}")
                        st.info("Please check your email (including spam folder) for password reset instructions.")
                    else:
                        st.error(f"❌ {message}")
