import sys
import os
from pathlib import Path

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config.settings import settings
from supabase import create_client, Client

def promote_user(email: str):
    """Promotes a user to admin role."""
    print(f"Attempting to promote user {email} to admin...")
    
    # Use SERVICE_KEY for admin operations to bypass RLS
    try:
        key = settings.SUPABASE_SERVICE_KEY
    except AttributeError:
        print("⚠️  SUPABASE_SERVICE_KEY not found in settings. Trying SUPABASE_KEY...")
        try:
            key = settings.SUPABASE_KEY
        except AttributeError:
            print("❌ Could not find SUPABASE_SERVICE_KEY or SUPABASE_KEY in settings.")
            return

    supabase: Client = create_client(settings.SUPABASE_URL, key)
    
    # 1. Check if user exists (Exact match)
    response = supabase.table("user_profiles").select("*").eq("email", email).execute()
    
    if not response.data:
        # 2. If not found, try case-insensitive search manually (fetch all and filter)
        # Note: Supabase/PostgREST 'ilike' filter is better if available, but let's debug by listing.
        print(f"❌ User with email {email} not found (exact match).")
        
        print("\nChecking for similar emails in database...")
        all_users = supabase.table("user_profiles").select("email").execute()
        
        found_similar = False
        if all_users.data:
            for user in all_users.data:
                db_email = user.get('email', '')
                if db_email.lower() == email.lower():
                    print(f"💡 Found user with different casing: {db_email}")
                    print(f"   Please run: python scripts/promote_user.py {db_email}")
                    found_similar = True
                elif email.lower() in db_email.lower():
                     print(f"❓ Did you mean: {db_email}?")
                     found_similar = True
        
        if not found_similar:
            print("\n⚠️  Available emails in database:")
            for user in all_users.data:
                print(f"   - {user.get('email')}")
        return

    user = response.data[0]
    user_id = user['user_id']
    current_role = user.get('role')
    
    if current_role == 'admin':
        print(f"✅ User {email} is already an admin.")
        return

    # 3. Update role
    update_response = supabase.table("user_profiles").update({"role": "admin"}).eq("user_id", user_id).execute()
    
    if update_response.data:
        print(f"🎉 Successfully promoted {email} to admin!")
        print("Please log out and log back in to see the Admin Dashboard.")
    else:
        print("❌ Failed to update user role.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/promote_user.py <email>")
        sys.exit(1)
    
    email_arg = sys.argv[1].strip()
    promote_user(email_arg)