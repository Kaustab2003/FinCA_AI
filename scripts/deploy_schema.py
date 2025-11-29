"""
Deploy Supabase Schema Updates
Run this script to deploy the complete schema to your Supabase instance
"""

import os
import sys
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in .env")
    sys.exit(1)

def deploy_schema_via_api():
    """Deploy schema using Supabase REST API"""

    print("🚀 Deploying FinCA AI schema to Supabase...")

    try:
        # Initialize Supabase client with service role
        assert SUPABASE_URL is not None
        assert SUPABASE_SERVICE_KEY is not None
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

        # Read the schema file
        schema_path = "database/complete_schema.sql"
        if not os.path.exists(schema_path):
            print(f"❌ Schema file not found: {schema_path}")
            sys.exit(1)

        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        # Split the schema into individual statements
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]

        print(f"📄 Found {len(statements)} SQL statements to execute")

        # For Supabase, we need to execute DDL through their SQL API
        # Since direct DDL execution isn't available via REST API,
        # we'll create a migration approach

        print("⚠️ Direct DDL execution via REST API is not supported by Supabase")
        print("📋 Please copy and paste the following SQL into your Supabase SQL Editor:")
        print("=" * 80)
        print(schema_sql)
        print("=" * 80)

        print("\n📖 Instructions:")
        print("1. Go to your Supabase Dashboard")
        print("2. Navigate to SQL Editor")
        print("3. Create a new query")
        print("4. Paste the SQL above")
        print("5. Click 'Run' to execute")

        # Instead of executing, let's verify current state
        verify_current_state(supabase)

    except Exception as e:
        print(f"❌ Schema deployment preparation failed: {str(e)}")
        sys.exit(1)

def verify_current_state(supabase):
    """Check current database state"""

    print("\n🔍 Checking current database state...")

    test_tables = [
        'user_profiles',
        'budgets',
        'goals',
        'transactions',
        'chat_history'
    ]

    existing_tables = []
    missing_tables = []

    for table in test_tables:
        try:
            # Try to select from the table
            result = supabase.table(table).select('count').limit(1).execute()
            existing_tables.append(table)
            print(f"✅ Table '{table}' exists")
        except Exception as e:
            missing_tables.append(table)
            print(f"❌ Table '{table}' missing or inaccessible")

    if missing_tables:
        print(f"\n⚠️ Missing tables that need to be created: {', '.join(missing_tables)}")
        print("Please run the SQL in Supabase SQL Editor to create them.")
    else:
        print("\n✅ All required tables exist!")

    # Check RLS status (this is approximate)
    print("\n🔒 Checking RLS status...")
    try:
        # This will fail if RLS is enabled and user doesn't have access
        result = supabase.table('user_profiles').select('*').limit(1).execute()
        print("⚠️ RLS may not be properly configured (able to access without auth)")
    except Exception as e:
        if "permission denied" in str(e).lower():
            print("✅ RLS appears to be working (permission denied without auth)")
        else:
            print(f"⚠️ RLS check inconclusive: {str(e)}")

def create_migration_script():
    """Create a migration script for manual execution"""

    print("\n📝 Creating migration script...")

    migration_file = "database/migration.sql"

    try:
        # Read the complete schema
        with open("database/complete_schema.sql", 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        # Create migration script with instructions
        migration_content = f"""-- =====================================================
-- FinCA AI - Database Migration Script
-- =====================================================
-- This script updates your Supabase database with the latest schema
-- Run this in your Supabase SQL Editor
--
-- Generated: {os.popen('date /t').read().strip() if os.name == 'nt' else os.popen('date').read().strip()}
-- =====================================================

{schema_sql}

-- =====================================================
-- Migration Complete
-- =====================================================
-- Verify the migration by checking that all tables exist
-- and RLS policies are properly configured
-- =====================================================
"""

        with open(migration_file, 'w', encoding='utf-8') as f:
            f.write(migration_content)

        print(f"✅ Migration script created: {migration_file}")
        print("📋 Copy the contents of this file to your Supabase SQL Editor")

    except Exception as e:
        print(f"❌ Failed to create migration script: {str(e)}")

if __name__ == "__main__":
    print("🔄 FinCA AI - Schema Deployment Tool")
    print("=" * 50)

    # Confirm before proceeding
    confirm = input("⚠️ This will prepare your Supabase database schema for deployment. Continue? (y/N): ")
    if confirm.lower() != 'y':
        print("Deployment cancelled.")
        sys.exit(0)

    deploy_schema_via_api()
    create_migration_script()

    print("\n🎯 Next Steps:")
    print("1. Copy the SQL from the output above (or from database/migration.sql)")
    print("2. Go to https://supabase.com/dashboard/project/[your-project]/sql")
    print("3. Create a new query and paste the SQL")
    print("4. Click 'Run' to execute the migration")
    print("5. Verify that all tables were created successfully")
    print("6. Run the user migration script: python scripts/migrate_to_supabase_auth.py")