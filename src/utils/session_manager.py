"""
Session Manager Utility for FinCA AI
Handles Streamlit session state management for authenticated users
"""

import streamlit as st
from typing import Dict, Optional
from src.utils.logger import logger


class SessionManager:
    """Manages user session state in Streamlit"""
    
    @staticmethod
    def init_user_session(user_data: Dict) -> None:
        """
        Initialize session state for authenticated user
        
        Args:
            user_data: Dictionary containing user information from auth service
        """
        try:
            # Clear any existing session data first
            SessionManager.clear_user_session()
            
            # Set authentication status
            st.session_state.authenticated = True
            st.session_state.user_id = user_data['id']
            st.session_state.email = user_data['email']
            st.session_state.role = user_data.get('role', 'user')
            
            # Set user context for app usage
            st.session_state.user_context = {
                'full_name': user_data.get('full_name', ''),
                'email': user_data['email'],
                'age': user_data.get('age'),
                'city': user_data.get('city', ''),
                'salary': user_data.get('monthly_income', 0),
                'risk_profile': user_data.get('risk_profile', 'moderate'),
                'role': user_data.get('role', 'user'),
                'onboarding_completed': user_data.get('onboarding_completed', False)
            }
            
            # Store tokens for API calls
            if 'session' in user_data and user_data['session']:
                session_data = user_data['session']
                if 'access_token' in session_data:
                    st.session_state.access_token = session_data['access_token']
                if 'refresh_token' in session_data:
                    st.session_state.refresh_token = session_data['refresh_token']
            elif 'access_token' in user_data:
                st.session_state.access_token = user_data['access_token']
            if 'refresh_token' in user_data:
                st.session_state.refresh_token = user_data['refresh_token']
            
            # Initialize empty data containers (user-specific)
            st.session_state.chat_messages = []
            st.session_state.current_budget = {}
            st.session_state.expense_data = []
            st.session_state.expense_history = []
            st.session_state.financial_goals = []
            
            # Clear caches to prevent data leakage
            st.cache_data.clear()
            
            logger.info(f"Session initialized for user: {user_data['email']} (role: {user_data.get('role', 'user')})")
            
        except Exception as e:
            logger.error(f"Failed to initialize user session: {str(e)}")
            raise
    
    @staticmethod
    def clear_user_session() -> None:
        """
        Clear all user session data (for logout or switching users)
        """
        try:
            # List of keys to preserve (app-level, not user-specific)
            preserved_keys = {'theme', 'language'}
            
            # Remove all session state except preserved keys
            keys_to_remove = [key for key in st.session_state.keys() if key not in preserved_keys]
            for key in keys_to_remove:
                del st.session_state[key]
            
            # Clear all caches
            st.cache_data.clear()
            
            logger.info("User session cleared")
            
        except Exception as e:
            logger.error(f"Failed to clear user session: {str(e)}")
    
    @staticmethod
    def is_authenticated() -> bool:
        """
        Check if user is currently authenticated
        
        Returns:
            True if authenticated, False otherwise
        """
        return st.session_state.get('authenticated', False)
    
    @staticmethod
    def is_admin() -> bool:
        """
        Check if current user has admin role
        
        Returns:
            True if admin, False otherwise
        """
        return st.session_state.get('role') == 'admin'
    
    @staticmethod
    def get_user_id() -> Optional[str]:
        """
        Get current user ID from session
        
        Returns:
            User ID or None if not authenticated
        """
        return st.session_state.get('user_id')
    
    @staticmethod
    def get_user_email() -> Optional[str]:
        """
        Get current user email from session
        
        Returns:
            User email or None if not authenticated
        """
        return st.session_state.get('email')
    
    @staticmethod
    def get_user_role() -> Optional[str]:
        """
        Get current user role from session
        
        Returns:
            User role ('user' or 'admin') or None if not authenticated
        """
        return st.session_state.get('role')
    
    @staticmethod
    def validate_session() -> bool:
        """
        Validate that session has all required data
        
        Returns:
            True if session is valid, False otherwise
        """
        required_keys = ['authenticated', 'user_id', 'email', 'role', 'user_context']
        
        for key in required_keys:
            if key not in st.session_state:
                logger.warning(f"Session validation failed: missing key '{key}'")
                return False
        
        return st.session_state.authenticated
    
    @staticmethod
    def require_auth() -> bool:
        """
        Check authentication and redirect to login if not authenticated
        Used as a gate in protected pages
        
        Returns:
            True if authenticated, redirects to login otherwise
        """
        if not SessionManager.is_authenticated():
            st.warning("🔒 Please login to access this feature")
            st.stop()
            return False
        
        if not SessionManager.validate_session():
            logger.warning("Invalid session detected, clearing...")
            SessionManager.clear_user_session()
            st.warning("🔒 Session expired. Please login again.")
            st.stop()
            return False
        
        return True
    
    @staticmethod
    def require_admin() -> bool:
        """
        Check admin role and show error if not admin
        Used as a gate in admin-only pages
        
        Returns:
            True if admin, stops execution otherwise
        """
        SessionManager.require_auth()
        
        if not SessionManager.is_admin():
            st.error("🚫 Access Denied: Admin privileges required")
            st.stop()
            return False
        
        return True
    
    @staticmethod
    def get_budget_data() -> Optional[Dict]:
        """
        Get current user's latest budget data from database
        
        Returns:
            Budget data dictionary or None if no budget exists
        """
        try:
            from src.services.budget_service import BudgetService
            import asyncio
            
            user_id = SessionManager.get_user_id()
            if not user_id:
                return None
            
            budget_service = BudgetService()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            budget = loop.run_until_complete(budget_service.get_latest_budget(user_id))
            
            return budget
            
        except Exception as e:
            logger.error(f"Failed to get budget data: {str(e)}")
            return None
    
    @staticmethod
    def get_access_token() -> Optional[str]:
        """
        Get access token from session
        
        Returns:
            Access token or None if not available
        """
        return st.session_state.get('access_token')
    
    @staticmethod
    def get_refresh_token() -> Optional[str]:
        """
        Get refresh token from session
        
        Returns:
            Refresh token or None if not available
        """
        return st.session_state.get('refresh_token')
