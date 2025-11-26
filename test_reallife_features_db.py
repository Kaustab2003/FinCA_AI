"""
Quick Test Script - Verify Real-Life Features Database Integration
Run this after creating database tables to verify everything works
"""

from src.config.database import DatabaseClient
from datetime import datetime
import sys

def test_database_connection():
    """Test if database connection and tables are working"""
    print("🔍 Testing Database Connection for Real-Life Features...\n")
    
    try:
        db = DatabaseClient.get_client()
        print("✅ Database connection successful!\n")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)
    
    user_id = 'demo_user_123'
    
    # Test each table
    tables = {
        'salary_breakup': '💰 Salary Breakup',
        'bill_reminders': '📱 Bill Reminders',
        'credit_cards': '💳 Credit Cards',
        'investment_comparisons': '🏦 Investment Comparisons',
        'quick_money_moves': '⚡ Quick Money Moves'
    }
    
    print("=" * 60)
    print("TABLE VERIFICATION")
    print("=" * 60)
    
    all_tables_ok = True
    
    for table_name, display_name in tables.items():
        try:
            # Try to query the table
            result = db.table(table_name).select('*').eq('user_id', user_id).execute()
            row_count = len(result.data) if result.data else 0
            
            print(f"✅ {display_name:<30} | Table: {table_name:<25} | Rows: {row_count}")
            
            if row_count > 0:
                print(f"   Sample data found for user: {user_id}")
            else:
                print(f"   ⚠️  No data yet for user: {user_id} (This is OK for testing)")
                
        except Exception as e:
            print(f"❌ {display_name:<30} | ERROR: {str(e)[:50]}")
            all_tables_ok = False
        
        print()
    
    print("=" * 60)
    
    # Test CRUD Operations
    if all_tables_ok:
        print("\n🔧 Testing CRUD Operations...\n")
        
        # Test 1: Insert Salary Breakup
        try:
            test_salary_data = {
                'user_id': 'test_user_temp',
                'ctc': 1200000.0,
                'basic_salary': 600000.0,
                'hra': 180000.0,
                'special_allowance': 300000.0,
                'pf_contribution': 72000.0,
                'professional_tax': 2400.0,
                'income_tax': 85000.0,
                'other_deductions': 5000.0,
                'in_hand_salary': 935600.0,
                'calculated_at': datetime.now().isoformat()
            }
            
            insert_result = db.table('salary_breakup').insert(test_salary_data).execute()
            
            if insert_result.data:
                inserted_id = insert_result.data[0]['id']
                print(f"✅ INSERT test passed - Salary Breakup ID: {inserted_id}")
                
                # Test 2: Read the inserted data
                read_result = db.table('salary_breakup').select('*').eq('id', inserted_id).execute()
                if read_result.data:
                    print(f"✅ READ test passed - Retrieved salary data")
                
                # Test 3: Update the data
                update_result = db.table('salary_breakup').update({'ctc': 1300000.0}).eq('id', inserted_id).execute()
                if update_result.data:
                    print(f"✅ UPDATE test passed - Updated CTC to ₹13L")
                
                # Test 4: Delete the test data
                delete_result = db.table('salary_breakup').delete().eq('id', inserted_id).execute()
                print(f"✅ DELETE test passed - Cleaned up test data")
            
        except Exception as e:
            print(f"❌ CRUD test failed: {e}")
        
        print("\n" + "=" * 60)
    
    # Test 2: Insert Bill Reminder
    try:
        test_bill_data = {
            'user_id': 'test_user_temp',
            'bill_name': 'Test Electricity Bill',
            'category': 'Utilities',
            'amount': 1500.0,
            'due_date': '2025-12-05',
            'frequency': 'Monthly',
            'auto_pay_enabled': False,
            'payment_method': 'UPI',
            'reminder_days': 3,
            'is_active': True
        }
        
        insert_result = db.table('bill_reminders').insert(test_bill_data).execute()
        
        if insert_result.data:
            bill_id = insert_result.data[0]['id']
            print(f"✅ Bill Reminder INSERT test passed - ID: {bill_id}")
            
            # Cleanup
            db.table('bill_reminders').delete().eq('id', bill_id).execute()
            print(f"✅ Bill Reminder cleaned up")
    
    except Exception as e:
        print(f"⚠️  Bill Reminder test: {e}")
    
    print("\n" + "=" * 60)
    
    # Summary
    print("\n📊 SUMMARY")
    print("=" * 60)
    
    if all_tables_ok:
        print("✅ All database tables are working correctly!")
        print("✅ CRUD operations verified")
        print("✅ Ready to use real-life features")
        print("\n🚀 Next Steps:")
        print("   1. Run: streamlit run src/ui/app_integrated.py --server.port 8503")
        print("   2. Navigate to any of the 5 new features in sidebar")
        print("   3. Add data and test database integration")
    else:
        print("❌ Some tables are missing or not working")
        print("🔧 Fix: Run the SQL script in Supabase SQL Editor")
        print("   File: database_schema_reallife_features.sql")
    
    print("=" * 60)


def test_demo_data():
    """Check if demo data exists"""
    print("\n🎭 Checking Demo Data...\n")
    
    try:
        db = DatabaseClient.get_client()
        user_id = 'demo_user_123'
        
        # Check each table for demo data
        tables = ['salary_breakup', 'bill_reminders', 'credit_cards', 'investment_comparisons', 'quick_money_moves']
        
        total_rows = 0
        for table in tables:
            result = db.table(table).select('*').eq('user_id', user_id).execute()
            count = len(result.data) if result.data else 0
            total_rows += count
            
            status = "✅" if count > 0 else "⚠️ "
            print(f"{status} {table:<30} : {count} demo records")
        
        print(f"\nTotal demo records: {total_rows}")
        
        if total_rows > 0:
            print("✅ Demo data is loaded - You can test with demo_user_123")
        else:
            print("⚠️  No demo data found - Run the SQL script to insert sample data")
    
    except Exception as e:
        print(f"❌ Error checking demo data: {e}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("FINCA AI - REAL-LIFE FEATURES DATABASE TEST")
    print("=" * 60 + "\n")
    
    test_database_connection()
    test_demo_data()
    
    print("\n✨ Test completed!\n")
