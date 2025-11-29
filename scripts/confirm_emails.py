#!/usr/bin/env python3
"""
Script to confirm unconfirmed emails in Supabase for development
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.auth_service import AuthService

def confirm_existing_emails():
    """Confirm emails for existing users who haven't confirmed yet"""
    auth_service = AuthService()

    try:
        # Get all users from auth
        users = auth_service.service_db.auth.admin.list_users()

        confirmed_count = 0
        for user in users:
            if not user.email_confirmed_at:  # If email not confirmed
                try:
                    auth_service.service_db.auth.admin.update_user_by_id(
                        user.id,
                        {"email_confirm": True}
                    )
                    print(f"✓ Confirmed email for: {user.email}")
                    confirmed_count += 1
                except Exception as e:
                    print(f"✗ Failed to confirm {user.email}: {str(e)}")

        if confirmed_count > 0:
            print(f"\n✅ Confirmed {confirmed_count} email(s)")
        else:
            print("\nℹ️  No unconfirmed emails found")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    confirm_existing_emails()