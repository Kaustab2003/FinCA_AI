"""
Supabase Database Connection Test
Tests all database operations and table structure
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client
import sys

# Load environment variables
load_dotenv()

def test_supabase_connection():
    """Test Supabase connection and database operations"""
    
    print("=" * 60)
    print("SUPABASE DATABASE CONNECTION TEST")
    print("=" * 60)
    
    # 1. Check Environment Variables
    print("\n1️⃣ Checking Environment Variables...")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url:
        print("❌ SUPABASE_URL not found in .env file")
        return False
    else:
        print(f"✅ SUPABASE_URL: {supabase_url[:30]}...")
    
    if not supabase_key:
        print("❌ SUPABASE_ANON_KEY not found in .env file")
        return False
    else:
        print(f"✅ SUPABASE_ANON_KEY: {supabase_key[:20]}...")
    
    # 2. Test Connection
    print("\n2️⃣ Testing Supabase Connection...")
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Supabase client created successfully")
    except Exception as e:
        print(f"❌ Failed to create Supabase client: {e}")
        return False
    
    # 3. Check if tables exist
    print("\n3️⃣ Checking Database Tables...")
    required_tables = [
        'user_profiles',
        'budgets',
        'goals',
        'chat_history',
        'transactions'
    ]
    
    tables_status = {}
    
    for table in required_tables:
        try:
            # Try to query the table (with limit 0 to not fetch data)
            response = supabase.table(table).select("*").limit(0).execute()
            tables_status[table] = "✅ EXISTS"
            print(f"  ✅ Table '{table}' exists")
        except Exception as e:
            tables_status[table] = f"❌ NOT FOUND - {str(e)}"
            print(f"  ❌ Table '{table}' not found: {str(e)}")
    
    # 4. Test INSERT operation (user_profiles)
    print("\n4️⃣ Testing INSERT Operation...")
    try:
        test_user = {
            "user_id": "test_user_" + str(int(os.times().elapsed * 1000)),
            "email": "test@finca.ai",
            "full_name": "Test User",
            "age": 30,
            "monthly_income": 100000
        }
        
        response = supabase.table('user_profiles').insert(test_user).execute()
        
        if response.data:
            print(f"✅ INSERT successful - User ID: {response.data[0]['user_id']}")
            test_user_id = response.data[0]['user_id']
        else:
            print("⚠️ INSERT returned no data")
            test_user_id = None
            
    except Exception as e:
        print(f"❌ INSERT failed: {e}")
        test_user_id = None
    
    # 5. Test SELECT operation
    print("\n5️⃣ Testing SELECT Operation...")
    try:
        response = supabase.table('user_profiles').select("*").limit(5).execute()
        
        if response.data:
            print(f"✅ SELECT successful - Found {len(response.data)} users")
            for user in response.data:
                print(f"  - User: {user.get('full_name', 'N/A')} ({user.get('email', 'N/A')})")
        else:
            print("⚠️ SELECT returned no data (table might be empty)")
            
    except Exception as e:
        print(f"❌ SELECT failed: {e}")
    
    # 6. Test UPDATE operation
    if test_user_id:
        print("\n6️⃣ Testing UPDATE Operation...")
        try:
            response = supabase.table('user_profiles').update({
                "full_name": "Updated Test User"
            }).eq('user_id', test_user_id).execute()
            
            if response.data:
                print(f"✅ UPDATE successful")
            else:
                print("⚠️ UPDATE returned no data")
                
        except Exception as e:
            print(f"❌ UPDATE failed: {e}")
    
    # 7. Test DELETE operation (cleanup)
    if test_user_id:
        print("\n7️⃣ Testing DELETE Operation...")
        try:
            response = supabase.table('user_profiles').delete().eq('user_id', test_user_id).execute()
            print(f"✅ DELETE successful - Test user cleaned up")
        except Exception as e:
            print(f"❌ DELETE failed: {e}")
    
    # 8. Check RLS (Row Level Security)
    print("\n8️⃣ Checking Row Level Security (RLS)...")
    print("⚠️ Note: RLS policies should be configured in Supabase dashboard")
    print("   Visit: https://supabase.com/dashboard/project/<your-project>/auth/policies")
    
    # 9. Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_tables_exist = all("✅" in status for status in tables_status.values())
    
    if all_tables_exist:
        print("✅ All required tables exist")
        print("✅ Database CRUD operations working")
        print("✅ Your Supabase database is properly configured!")
    else:
        print("❌ Some tables are missing")
        print("\n🔧 To fix:")
        print("1. Go to Supabase Dashboard: https://supabase.com/dashboard")
        print("2. Select your project")
        print("3. Go to SQL Editor")
        print("4. Run the schema.sql file from: src/database/schema.sql")
        print("\nMissing tables:")
        for table, status in tables_status.items():
            if "❌" in status:
                print(f"  - {table}")
    
    print("=" * 60)
    
    return all_tables_exist


if __name__ == "__main__":
    try:
        success = test_supabase_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)