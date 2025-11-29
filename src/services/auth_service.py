"""
Authentication Service for FinCA AI
Enhanced with Supabase Auth for better security and JWT handling
"""

from typing import Dict, Optional, Tuple
from datetime import datetime
import streamlit as st
from src.config.database import DatabaseClient
from src.utils.logger import logger


class AuthService:
    """Service for handling authentication operations with Supabase Auth"""

    def __init__(self):
        self.db = DatabaseClient.get_client()
        self.service_db = DatabaseClient.get_service_client()

    def sign_up(self, email: str, password: str, user_data: Dict) -> Tuple[bool, str, Optional[Dict]]:
        """
        Register a new user using Supabase Auth

        Args:
            email: User email
            password: User password
            user_data: Additional user information

        Returns:
            Tuple of (success: bool, message: str, user_data: Optional[Dict])
        """
        try:
            # Normalize email
            email = email.lower().strip()

            # Check if email already exists in user_profiles
            existing_user = self.service_db.table('user_profiles').select('email').eq('email', email).execute()
            if existing_user.data:
                return False, "Email already registered", None

            # Create auth user in Supabase
            auth_response = self.db.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "full_name": user_data.get('full_name', ''),
                        "age": user_data.get('age'),
                        "city": user_data.get('city', ''),
                    }
                }
            })

            if not auth_response.user:
                return False, "Failed to create authentication account", None

            user_id = auth_response.user.id

            # Auto-confirm email for development (bypass email confirmation)
            try:
                self.service_db.auth.admin.update_user_by_id(
                    user_id,
                    {"email_confirm": True}
                )
                logger.info(f"Email auto-confirmed for development: {email}")
            except Exception as confirm_error:
                logger.warning(f"Failed to auto-confirm email: {str(confirm_error)}")
                # Continue anyway - user can still manually confirm

            # Auto-assign admin role if email contains 'admin' (FOR TESTING PURPOSES)
            role = "admin" if "admin" in email else "user"

            # Create user profile
            profile_data = {
                'user_id': user_id,
                'email': email,
                'password_hash': 'SUPABASE_AUTH',  # Dummy value since Supabase handles auth
                'full_name': user_data.get('full_name', ''),
                'age': user_data.get('age'),
                'city': user_data.get('city', ''),
                'monthly_income': user_data.get('monthly_income', 0),
                'risk_profile': user_data.get('risk_profile', 'moderate'),
                'role': role,
                'is_active': True,
                'onboarding_completed': False,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }

            result = self.service_db.table('user_profiles').insert(profile_data).execute()

            # Initialize user preferences
            self.service_db.table('user_preferences').insert({'user_id': user_id}).execute()

            # Initialize notification preferences
            self.service_db.table('notification_preferences').insert({'user_id': user_id}).execute()

            if not result.data:
                # Clean up auth user if profile creation failed
                self.db.auth.admin.delete_user(user_id)
                return False, "Failed to create user profile", None

            logger.info(f"User registered: {email}")

            user_profile = result.data[0]
            user_profile['id'] = user_id

            return True, "Registration successful! You can now log in with your credentials.", user_profile

        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return False, f"Registration failed: {str(e)}", None

    def sign_in(self, email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Authenticate user with Supabase Auth

        Args:
            email: User email
            password: User password

        Returns:
            Tuple of (success: bool, message: str, user_data: Optional[Dict])
        """
        try:
            # Normalize email
            email = email.lower().strip()

            # Sign in with Supabase Auth
            auth_response = self.db.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if not auth_response.user or not auth_response.session:
                return False, "Invalid email or password", None

            user_id = auth_response.user.id

            # Fetch user profile
            profile_result = self.service_db.table('user_profiles').select('*').eq('user_id', user_id).execute()

            if not profile_result.data:
                logger.warning(f"Login failed: Profile not found for {email}")
                return False, "User profile not found. Please contact support.", None

            user_profile = profile_result.data[0]

            # Check if user is active
            if not user_profile.get('is_active', True):
                return False, "Your account has been deactivated. Please contact support.", None

            # Update last login
            self.service_db.table('user_profiles').update({
                'updated_at': datetime.now().isoformat()
            }).eq('user_id', user_id).execute()

            # Prepare user data for session
            user_data = {
                'id': user_profile['user_id'],
                'email': user_profile['email'],
                'full_name': user_profile.get('full_name', ''),
                'role': user_profile.get('role', 'user'),
                'age': user_profile.get('age'),
                'city': user_profile.get('city', ''),
                'monthly_income': user_profile.get('monthly_income', 0),
                'risk_profile': user_profile.get('risk_profile', 'moderate'),
                'onboarding_completed': user_profile.get('onboarding_completed', False),
                'session': {
                    'access_token': auth_response.session.access_token,
                    'refresh_token': auth_response.session.refresh_token,
                    'expires_at': auth_response.session.expires_at
                }
            }

            # Authenticate the shared database client for RLS
            DatabaseClient.authenticate_client(
                auth_response.session.access_token,
                auth_response.session.refresh_token
            )

            logger.info(f"Login successful: {email} (role: {user_data['role']})")
            return True, "Login successful!", user_data

        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return False, f"Login failed: {str(e)}", None

    def sign_out(self) -> Tuple[bool, str]:
        """Sign out current user from Supabase Auth"""
        try:
            self.db.auth.sign_out()
            DatabaseClient.sign_out_client()
            logger.info("User signed out successfully")
            return True, "Signed out successfully"
        except Exception as e:
            logger.error(f"Sign out error: {str(e)}")
            return False, f"Sign out failed: {str(e)}"

    def get_current_user(self) -> Optional[Dict]:
        """Get current authenticated user from Supabase"""
        try:
            user = self.db.auth.get_user()
            if user and user.user:
                return {
                    'id': user.user.id,
                    'email': user.user.email,
                    'full_name': user.user.user_metadata.get('full_name', ''),
                }
            return None
        except Exception as e:
            logger.error(f"Error getting current user: {str(e)}")
            return None

    def verify_role(self, user_id: str) -> str:
        """Get user role"""
        try:
            result = self.service_db.table('user_profiles').select('role').eq('user_id', user_id).execute()
            if result.data:
                return result.data[0].get('role', 'user')
            return 'user'
        except:
            return 'user'

    def reset_password(self, email: str) -> Tuple[bool, str]:
        """Send password reset email using Supabase Auth"""
        try:
            email = email.lower().strip()
            self.db.auth.reset_password_email(email)
            return True, "Password reset email sent. Please check your inbox."
        except Exception as e:
            logger.error(f"Password reset error: {str(e)}")
            return False, f"Failed to send password reset email: {str(e)}"

    def update_password(self, new_password: str) -> Tuple[bool, str]:
        """Update user password using Supabase Auth"""
        try:
            self.db.auth.update_user({
                "password": new_password
            })
            return True, "Password updated successfully"
        except Exception as e:
            logger.error(f"Password update error: {str(e)}")
            return False, f"Failed to update password: {str(e)}"

    def verify_session(self) -> bool:
        """Verify if current session is valid"""
        try:
            session = self.db.auth.get_session()
            return session is not None and session.user is not None
        except:
            return False

    def refresh_session(self) -> bool:
        """Refresh the current session"""
        try:
            self.db.auth.refresh_session()
            return True
        except Exception as e:
            logger.error(f"Session refresh error: {str(e)}")
            return False

    def confirm_email(self, email: str) -> Tuple[bool, str]:
        """
        Manually confirm user email using admin API (for development/testing)

        Args:
            email: User email to confirm

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            email = email.lower().strip()

            # Get user by email using admin API
            users = self.service_db.auth.admin.list_users()
            user = None
            for u in users:
                if u.email.lower() == email:
                    user = u
                    break

            if not user:
                return False, "User not found"

            # Confirm the user's email
            self.service_db.auth.admin.update_user_by_id(
                user.id,
                {"email_confirm": True}
            )

            logger.info(f"Email confirmed for user: {email}")
            return True, "Email confirmed successfully"

        except Exception as e:
            logger.error(f"Email confirmation error: {str(e)}")
            return False, f"Failed to confirm email: {str(e)}"

    def get_user_profile(self, email: str) -> Optional[Dict]:
        """Get user profile by email"""
        try:
            email = email.lower().strip()
            result = self.service_db.table('user_profiles').select('*').eq('email', email).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Error fetching user profile: {str(e)}")
            return None
