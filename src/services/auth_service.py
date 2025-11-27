"""
Authentication Service for FinCA AI
Handles user registration, login, logout using custom authentication (no Supabase Auth)
"""

from typing import Dict, Optional, Tuple
from datetime import datetime
import streamlit as st
import hashlib
import uuid
from src.config.database import DatabaseClient
from src.utils.logger import logger


class AuthService:
    """Service for handling authentication operations"""
    
    def __init__(self):
        self.db = DatabaseClient.get_client()
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _generate_user_id(self) -> str:
        """Generate unique user ID"""
        return str(uuid.uuid4())
    
    def sign_up(self, email: str, password: str, user_data: Dict) -> Tuple[bool, str, Optional[Dict]]:
        """
        Register a new user (only in user_profiles table)
        
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
            
            # Check if email already exists
            existing_user = self.db.table('user_profiles').select('email').eq('email', email).execute()
            if existing_user.data:
                return False, "Email already registered", None
            
            # Generate unique user ID
            user_id = self._generate_user_id()
            
            # Hash password
            password_hash = self._hash_password(password)
            
            # Auto-assign admin role if email contains 'admin' (FOR TESTING PURPOSES)
            role = "admin" if "admin" in email else "user"
            
            # Create user profile with hashed password
            profile_data = {
                'user_id': user_id,
                'email': email,
                'password_hash': password_hash,
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
            
            result = self.db.table('user_profiles').insert(profile_data).execute()
            
            # Initialize user preferences
            self.db.table('user_preferences').insert({'user_id': user_id}).execute()
            
            # Initialize notification preferences
            self.db.table('notification_preferences').insert({'user_id': user_id}).execute()
            
            if not result.data:
                return False, "Failed to create user profile", None
            
            logger.info(f"User registered: {email}")
            
            user_profile = result.data[0]
            user_profile['id'] = user_id
            
            return True, "Registration successful! You can now login.", user_profile
            
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return False, f"Registration failed: {str(e)}", None
    
    def sign_in(self, email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Authenticate user with email and password
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Tuple of (success: bool, message: str, user_data: Optional[Dict])
        """
        try:
            # Normalize email
            email = email.lower().strip()
            
            # Hash the provided password
            password_hash = self._hash_password(password)
            
            # Fetch user profile
            profile_result = self.db.table('user_profiles').select('*').eq('email', email).execute()
            
            if not profile_result.data:
                logger.warning(f"Login failed: User {email} not found")
                return False, "Invalid email or password", None
            
            user_profile = profile_result.data[0]
            
            # Verify password
            if user_profile.get('password_hash') != password_hash:
                logger.warning(f"Login failed for {email}: Password mismatch")
                return False, "Invalid email or password", None
            
            # Check if user is active
            if not user_profile.get('is_active', True):
                return False, "Your account has been deactivated. Please contact support.", None
            
            # Update last login
            self.db.table('user_profiles').update({
                'updated_at': datetime.now().isoformat()
            }).eq('user_id', user_profile['user_id']).execute()
            
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
                'onboarding_completed': user_profile.get('onboarding_completed', False)
            }
            
            logger.info(f"Login successful: {email} (role: {user_data['role']})")
            return True, "Login successful!", user_data
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return False, f"Login failed: {str(e)}", None
    
    def sign_out(self) -> Tuple[bool, str]:
        """Sign out current user"""
        try:
            logger.info("User signed out successfully")
            return True, "Signed out successfully"
        except Exception as e:
            logger.error(f"Sign out error: {str(e)}")
            return False, f"Sign out failed: {str(e)}"
    
    def get_current_user(self) -> Optional[Dict]:
        """Get current user (not applicable for custom auth)"""
        return None
    
    def verify_role(self, user_id: str) -> str:
        """Get user role"""
        try:
            result = self.db.table('user_profiles').select('role').eq('user_id', user_id).execute()
            if result.data:
                return result.data[0].get('role', 'user')
            return 'user'
        except:
            return 'user'
    
    def reset_password(self, email: str) -> Tuple[bool, str]:
        """Send password reset email (not implemented for custom auth)"""
        return False, "Password reset not available. Please contact admin."
    
    def update_password(self, user_id: str, new_password: str) -> Tuple[bool, str]:
        """Update user password"""
        try:
            password_hash = self._hash_password(new_password)
            self.db.table('user_profiles').update({
                'password_hash': password_hash,
                'updated_at': datetime.now().isoformat()
            }).eq('user_id', user_id).execute()
            
            return True, "Password updated successfully"
        except Exception as e:
            return False, f"Failed to update password: {str(e)}"
    
    def verify_session(self) -> bool:
        """Verify if session is valid (always true for custom auth)"""
        return True
    
    def get_user_profile(self, email: str) -> Optional[Dict]:
        """Get user profile by email"""
        try:
            email = email.lower().strip()
            result = self.db.table('user_profiles').select('*').eq('email', email).execute()
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            logger.error(f"Error fetching user profile: {str(e)}")
            return None
