"""
Database setup script - Initialize Supabase with schema
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.database import DatabaseClient
from src.config.settings import settings
from src.utils.logger import logger

def read_sql_file(filepath: str) -> str:
    """Read SQL file content"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def setup_database():
    """Initialize database with schema"""
    try:
        logger.info("🚀 Starting database setup...")
        
        # Get service client (admin access)
        client = DatabaseClient.get_service_client()
        
        # Read schema file
        schema_path = Path(__file__).parent.parent / 'src' / 'database' / 'schema.sql'
        if not schema_path.exists():
            logger.error(f"Schema file not found: {schema_path}")
            return False
        
        logger.info(f"Reading schema from: {schema_path}")
        schema_sql = read_sql_file(str(schema_path))
        
        # Execute schema (note: Supabase doesn't support direct SQL execution via client)
        logger.info("📋 Schema SQL ready. Please execute manually in Supabase SQL Editor:")
        logger.info("=" * 80)
        logger.info("1. Go to your Supabase project")
        logger.info("2. Navigate to SQL Editor")
        logger.info(f"3. Copy and run the SQL from: {schema_path}")
        logger.info("=" * 80)
        
        # Verify connection
        logger.info("🔍 Verifying database connection...")
        result = client.table('schema_version').select('version').execute()
        
        if result.data:
            logger.info(f"✅ Database connected! Schema version: {result.data[0]['version']}")
        else:
            logger.warning("⚠️ Database connected but schema not initialized yet")
            logger.info("Please run the schema.sql file in Supabase SQL Editor")
        
        logger.info("✅ Database setup complete!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        logger.error("Please ensure:")
        logger.error("1. SUPABASE_SERVICE_KEY is set in .env")
        logger.error("2. Supabase project is accessible")
        logger.error("3. SQL Editor is used to run schema.sql")
        return False

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════╗
║         FinCA AI - Database Setup              ║
╚════════════════════════════════════════════════╝
    """)
    
    success = setup_database()
    
    if success:
        print("""
✅ Setup Instructions:
1. Open Supabase SQL Editor: https://supabase.com/dashboard
2. Copy schema from: src/database/schema.sql
3. Execute the SQL to create 25 tables
4. Run this script again to verify

📚 Next Steps:
- Generate encryption key: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
- Add to .env: ENCRYPTION_KEY=<generated_key>
- Run app: streamlit run src/ui/streamlit_app.py
        """)
    else:
        print("❌ Setup failed. Check logs above.")
        sys.exit(1)
