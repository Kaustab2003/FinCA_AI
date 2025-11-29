"""
Main application entry point with authentication
This file wraps the main app and handles authentication flow
"""

import sys
import os

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
from src.ui.pages.auth.login import show_login, show_reset_password_section
from src.ui.pages.auth.register import show_register
from src.utils.session_manager import SessionManager
from src.services.auth_service import AuthService


def show_auth_page():
    """Display authentication page (login/register/reset)"""
    
    # Check which page to show
    if st.session_state.get('show_register', False):
        show_register()
    elif st.session_state.get('show_reset_password', False):
        show_reset_password_section()
    else:
        show_login()


def main():
    """Main entry point with authentication gate"""
    
    # Initialize session state for auth flow
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'show_register' not in st.session_state:
        st.session_state.show_register = False
    if 'show_reset_password' not in st.session_state:
        st.session_state.show_reset_password = False
    
    # Check if user is authenticated
    if not SessionManager.is_authenticated():
        # Show login/register page
        show_auth_page()
    else:
        # User is authenticated, load main app
        import app as app
        app.main()


if __name__ == "__main__":
    main()
