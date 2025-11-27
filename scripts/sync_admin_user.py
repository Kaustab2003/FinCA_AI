import sys
import os
from pathlib import Path
import hashlib
import uuid
from datetime import datetime

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config.settings import settings
from supabase import create_client, Client

def sync_supabase_auth_user(email: str, password: str, user_id: str):
    """
    Manually creates a user profile in our custom 'user_profiles' table 
    for a user that already exists in Supabase Auth.
    """
    print(f"Attempting to sync Supabase Auth user {email} to local user_profiles...")
    
    # Use service key to bypass RLS
    try:
        key = settings.SUPABASE_SERVICE_KEY
    except AttributeError:
        key = settings.SUPABASE_KEY

    supabase: Client = create_client(settings.SUPABASE_URL, key)
    
    # 1. Check if user already exists in user_profiles
    response = supabase.table("user_profiles").select("*").eq("email", email).execute()
    
    if response.data:
        print(f"✅ User {email} already exists in user_profiles table.")
        print("Updating role to admin...")
        supabase.table("user_profiles").update({"role": "admin"}).eq("email", email).execute()
        print("Done.")
        return

    # 2. Create new profile
    print(f"Creating new profile for {email}...")
    
    # Hash password (since our app uses custom auth logic on top of user_profiles)
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    profile_data = {
        'user_id': user_id,  # Use the ID from Supabase Auth
        'email': email,
        'password_hash': password_hash,
        'full_name': 'Admin User',
        'age': 30,
        'city': 'Headquarters',
        'monthly_income': 100000,
        'risk_profile': 'aggressive',
        'role': 'admin',  # Force admin role
        'is_active': True,
        'onboarding_completed': True,
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    try:
        result = supabase.table('user_profiles').insert(profile_data).execute()
        
        # Initialize preferences
        supabase.table('user_preferences').insert({'user_id': user_id}).execute()
        supabase.table('notification_preferences').insert({'user_id': user_id}).execute()
        
        if result.data:
            print(f"🎉 Successfully synced {email} to user_profiles with ADMIN role!")
            print("You can now login with this email and password.")
        else:
            print("❌ Failed to create user profile.")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    # Hardcoded values from user request
    EMAIL = "test@finca.ai"
    PASSWORD = "Admin@123456"
    USER_ID = "6789779f-dd1b-4ce6-b53b-a26a29f25c0e"
    
    sync_supabase_auth_user(EMAIL, PASSWORD, USER_ID)
