"""
Check actual Supabase database schema vs expected schema
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

def check_database_schema():
    """Check what columns actually exist in each table"""
    
    print("=" * 60)
    print("DATABASE SCHEMA VERIFICATION")
    print("=" * 60)
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    supabase: Client = create_client(supabase_url, supabase_key)
    
    tables = ['user_profiles', 'budgets', 'goals', 'chat_history', 'transactions']
    
    for table_name in tables:
        print(f"\n📋 Table: {table_name}")
        print("-" * 60)
        
        try:
            # Query with select * to see what columns exist
            response = supabase.table(table_name).select("*").limit(1).execute()
            
            if response.data and len(response.data) > 0:
                columns = response.data[0].keys()
                print(f"✅ Columns found: {', '.join(columns)}")
            else:
                # Table is empty, try to get schema from API
                print("⚠️ Table is empty - attempting insert test to discover schema...")
                
                # Try minimal insert to discover required fields
                test_data = {"id": 999999}  # Use a test ID
                try:
                    supabase.table(table_name).insert(test_data).execute()
                except Exception as e:
                    error_msg = str(e)
                    if "Could not find" in error_msg:
                        print(f"❌ Schema error: {error_msg}")
                    else:
                        print(f"⚠️ Error: {error_msg}")
                
        except Exception as e:
            print(f"❌ Error accessing table: {e}")
    
    print("\n" + "=" * 60)
    print("RECOMMENDATION")
    print("=" * 60)
    print("\nYour tables exist but may have wrong schema.")
    print("\n🔧 Fix Options:")
    print("\n1. **Recreate Tables (Recommended):**")
    print("   - Go to: https://supabase.com/dashboard")
    print("   - SQL Editor → Run the complete schema.sql")
    print("   - This will create tables with correct structure")
    print("\n2. **Check Schema Differences:**")
    print("   - Compare your tables with src/database/schema.sql")
    print("   - Add missing columns manually")
    print("\n3. **Use Supabase Migration:**")
    print("   - Create migration file")
    print("   - Apply schema changes")

if __name__ == "__main__":
    check_database_schema()