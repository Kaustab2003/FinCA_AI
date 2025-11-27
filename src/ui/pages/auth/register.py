"""
Registration Page for FinCA AI
Handles new user registration
"""

import streamlit as st
import re
from src.services.auth_service import AuthService
from src.utils.session_manager import SessionManager
from src.utils.logger import logger


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password strength
    Returns: (is_valid, message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    return True, "Strong password"


def show_register():
    """Display registration page"""
    
    # Custom CSS
    st.markdown("""
    <style>
        .register-container {
            max-width: 600px;
            margin: 0 auto;
            padding: 2rem;
        }
        .register-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        .register-header h1 {
            color: #667eea;
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        .register-header p {
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
        }
        .password-strength {
            margin-top: 0.5rem;
            padding: 0.5rem;
            border-radius: 4px;
            font-size: 0.9rem;
        }
        .strength-weak {
            background-color: #ffebee;
            color: #c62828;
        }
        .strength-medium {
            background-color: #fff3e0;
            color: #ef6c00;
        }
        .strength-strong {
            background-color: #e8f5e9;
            color: #2e7d32;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="register-header">
        <h1>📝 Create Account</h1>
        <p>Join FinCA AI to start your financial journey</p>
    </div>
    """, unsafe_allow_html=True)
    
    auth_service = AuthService()
    
    # Registration form
    with st.form("registration_form", clear_on_submit=False):
        st.subheader("Personal Information")
        
        # Basic info
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input(
                "Full Name *",
                placeholder="John Doe",
                help="Your full name as it should appear"
            )
        with col2:
            age = st.number_input(
                "Age *",
                min_value=18,
                max_value=100,
                value=25,
                help="You must be 18 or older to register"
            )
        
        col1, col2 = st.columns(2)
        with col1:
            city = st.text_input(
                "City *",
                placeholder="Mumbai",
                help="Your current city of residence"
            )
        with col2:
            monthly_income = st.number_input(
                "Monthly Income (₹) *",
                min_value=0,
                value=50000,
                step=5000,
                help="Your approximate monthly income"
            )
        
        risk_profile = st.selectbox(
            "Risk Profile *",
            options=["conservative", "moderate", "aggressive"],
            index=1,
            help="Your investment risk tolerance"
        )
        
        st.markdown("---")
        st.subheader("Account Credentials")
        
        email = st.text_input(
            "Email Address *",
            placeholder="your.email@example.com",
            help="We'll use this for login and notifications"
        )
        
        # Email validation feedback
        if email and not validate_email(email):
            st.warning("⚠️ Please enter a valid email address")
        
        col1, col2 = st.columns(2)
        with col1:
            password = st.text_input(
                "Password *",
                type="password",
                placeholder="Create a strong password",
                help="Minimum 8 characters with uppercase, lowercase, and numbers"
            )
        with col2:
            confirm_password = st.text_input(
                "Confirm Password *",
                type="password",
                placeholder="Re-enter your password"
            )
        
        # Password strength indicator
        if password:
            is_valid, message = validate_password(password)
            if is_valid:
                st.markdown('<div class="password-strength strength-strong">✅ ' + message + '</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="password-strength strength-weak">❌ ' + message + '</div>', unsafe_allow_html=True)
        
        # Password match check
        if password and confirm_password and password != confirm_password:
            st.error("❌ Passwords do not match")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Terms and conditions
        agree_terms = st.checkbox(
            "I agree to the Terms of Service and Privacy Policy *",
            help="You must agree to continue"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Submit buttons
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("🚀 Create Account", type="primary", use_container_width=True)
        with col2:
            if st.form_submit_button("← Back to Login", type="secondary", use_container_width=True):
                st.session_state.show_register = False
                st.rerun()
        
        if submitted:
            # Normalize email
            email = email.lower().strip() if email else ""
            
            # Validation
            errors = []
            
            if not full_name:
                errors.append("Full name is required")
            if not city:
                errors.append("City is required")
            if not email:
                errors.append("Email is required")
            elif not validate_email(email):
                errors.append("Invalid email format")
            if not password:
                errors.append("Password is required")
            else:
                is_valid_pwd, pwd_message = validate_password(password)
                if not is_valid_pwd:
                    errors.append(pwd_message)
            if password != confirm_password:
                errors.append("Passwords do not match")
            if not agree_terms:
                errors.append("You must agree to the Terms of Service")
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                # Create account
                with st.spinner("Creating your account..."):
                    user_data = {
                        'full_name': full_name,
                        'age': age,
                        'city': city,
                        'monthly_income': monthly_income,
                        'risk_profile': risk_profile
                    }
                    
                    success, message, created_user = auth_service.sign_up(email, password, user_data)
                    
                    if success and created_user:
                        st.success(f"✅ {message}")
                        st.balloons()
                        
                        # Auto-login after registration
                        SessionManager.init_user_session(created_user)
                        logger.info(f"New user registered and logged in: {email}")
                        
                        # Show welcome message
                        st.info("🎉 Welcome to FinCA AI! Redirecting to your dashboard...")
                        
                        import time
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
                        logger.warning(f"Registration failed: {email} - {message}")
    
    # Info section
    with st.expander("ℹ️ Why do we need this information?"):
        st.markdown("""
        **Personal Information**: Helps us personalize your financial advice and recommendations.
        
        **Monthly Income**: Used to calculate appropriate budget allocations and savings goals.
        
        **Risk Profile**: Determines investment recommendations suitable for your comfort level.
        
        **Security**: All your data is encrypted and stored securely. We never share your information with third parties.
        """)
    
    # Privacy notice
    st.caption("🔒 Your privacy is important to us. Read our [Privacy Policy](#) and [Terms of Service](#).")
