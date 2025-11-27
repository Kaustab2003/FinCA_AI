"""
FinCA AI - Document Parser Page
Upload and parse financial documents using AI
"""
import streamlit as st
import tempfile
import os
from pathlib import Path
import sys
import asyncio
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from src.agents.document_parsing_agent import DocumentParsingAgent
from src.services.transaction_service import TransactionService
from src.services.goals_service import GoalsService
from src.utils.session_manager import SessionManager

def show_document_parser():
    """Display the document parser page"""

    st.title("📄 Document Parser")
    st.markdown("Upload financial documents to extract key information automatically")

    # Check authentication
    if not SessionManager.is_authenticated():
        st.warning("Please log in to use the document parser.")
        return

    user_id = SessionManager.get_user_id()

    # File upload section
    st.subheader("📤 Upload Document")

    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['pdf', 'txt', 'csv', 'png', 'jpg', 'jpeg'],
            help="Supported formats: PDF, TXT, CSV, PNG, JPG"
        )

    with col2:
        doc_type = st.selectbox(
            "Document Type",
            ["Bank Statement", "Salary Slip", "Tax Document", "Invoice/Bill",
             "Investment Statement", "Credit Card Statement", "Utility Bill", "Other"],
            help="Select the type of document for better parsing accuracy"
        )

    # File size validation
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    if uploaded_file:
        if uploaded_file.size > MAX_FILE_SIZE:
            st.error(f"File size ({uploaded_file.size / 1024 / 1024:.1f}MB) exceeds maximum limit of 10MB")
            return

        # Show file info
        st.info(f"📄 {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")

        # Process button
        if st.button("🔍 Parse Document", type="primary"):
            with st.spinner("Processing document..."):
                try:
                    # Extract text from file
                    document_text = extract_text_from_file(uploaded_file)

                    if not document_text.strip():
                        st.error("Could not extract text from the uploaded file. Please try a different file.")
                        return

                    # Parse document
                    agent = DocumentParsingAgent()
                    result = agent.parse_document_sync(document_text, doc_type.lower().replace(" ", "_"))

                    # Store result in session state
                    st.session_state.parsed_result = result
                    st.session_state.uploaded_file_name = uploaded_file.name

                    st.success("Document parsed successfully!")
                    st.rerun()

                except Exception as e:
                    st.error(f"Error processing document: {str(e)}")

    # Display results
    if 'parsed_result' in st.session_state:
        display_parsed_results(st.session_state.parsed_result, user_id)

def extract_text_from_file(uploaded_file) -> str:
    """Extract text content from uploaded file"""
    file_extension = uploaded_file.name.split('.')[-1].lower()

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name

    try:
        if file_extension == 'pdf':
            # Extract text from PDF
            try:
                from pypdf import PdfReader
                reader = PdfReader(tmp_path)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
            except ImportError:
                st.error("PDF processing requires pypdf. Please install with: pip install pypdf")
                return ""

        elif file_extension == 'txt':
            # Read text file
            with open(tmp_path, 'r', encoding='utf-8') as f:
                return f.read()

        elif file_extension == 'csv':
            # Read CSV file as text
            with open(tmp_path, 'r', encoding='utf-8') as f:
                return f.read()

        elif file_extension in ['png', 'jpg', 'jpeg']:
            # OCR for images (requires pytesseract and pillow)
            try:
                import pytesseract
                from PIL import Image
                img = Image.open(tmp_path)
                return pytesseract.image_to_string(img)
            except ImportError:
                st.error("Image processing requires pytesseract and Pillow. Please install with: pip install pytesseract Pillow")
                return ""
            except Exception as e:
                st.error(f"Error processing image: {str(e)}")
                return ""
        else:
            return ""

    finally:
        # Clean up temporary file
        try:
            os.unlink(tmp_path)
        except:
            pass

def display_parsed_results(result: dict, user_id: str):
    """Display parsed results with action buttons"""

    st.subheader("📊 Parsed Results")

    # Display confidence and summary
    confidence = result.get('confidence', 0)
    confidence_color = "🟢" if confidence > 0.8 else "🟡" if confidence > 0.6 else "🔴"

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.metric("Confidence Score", f"{confidence:.1%}",
                 help="How confident the AI is in the extracted data")
    with col2:
        if st.button("🔄 Re-parse", help="Parse the document again"):
            if 'parsed_result' in st.session_state:
                del st.session_state.parsed_result
            st.rerun()
    with col3:
        if st.button("🗑️ Clear", help="Clear current results"):
            if 'parsed_result' in st.session_state:
                del st.session_state.parsed_result
            st.rerun()

    # Display formatted content
    formatted_content = result.get('formatted_content', 'No content available')
    st.markdown(formatted_content)

    # Extracted data for actions
    parsed_data = result.get('parsed_data', {})

    # Transactions section
    transactions = parsed_data.get('transactions', [])
    if transactions:
        st.subheader("💳 Extracted Transactions")

        # Display transactions in a table
        txn_df = []
        for txn in transactions:
            txn_df.append({
                'Date': txn.get('date', 'N/A'),
                'Amount': f"₹{txn.get('amount', 0)}",
                'Description': txn.get('description', 'N/A'),
                'Type': txn.get('type', 'expense')
            })

        if txn_df:
            import pandas as pd
            df = pd.DataFrame(txn_df)
            st.dataframe(df, use_container_width=True)

            # Bulk import button
            if st.button("📥 Import All Transactions", type="primary"):
                import_transactions_bulk(transactions, user_id)

    # Quick actions for goals
    financial_summary = parsed_data.get('financial_summary', {})
    if financial_summary:
        st.subheader("🎯 Suggested Goals")

        # Suggest goals based on financial summary
        suggestions = generate_goal_suggestions(financial_summary)

        for suggestion in suggestions:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{suggestion['title']}**")
                st.caption(suggestion['description'])
            with col2:
                if st.button(f"Create Goal", key=f"goal_{suggestion['title']}"):
                    create_goal_from_suggestion(suggestion, user_id)

    # Processing Summary Section
    st.markdown("---")
    st.subheader("📋 Processing Summary")

    col1, col2, col3 = st.columns([2, 2, 2])

    with col1:
        st.metric("Confidence Score", f"{result.get('confidence', 0):.1%}")
        st.caption("AI confidence in extracted data")

    with col2:
        transactions_count = len(result.get('parsed_data', {}).get('transactions', []))
        st.metric("Transactions Found", transactions_count)
        st.caption("Total transactions extracted")

    with col3:
        st.metric("Processing Time", "< 30 seconds")
        st.caption("Typical processing time")

    # Helpful Tips Section
    st.markdown("---")
    st.subheader("💡 Helpful Tips")

    tips_col1, tips_col2 = st.columns(2)

    with tips_col1:
        st.markdown("""
        **📄 Supported Formats:**
        - PDF bank statements
        - CSV transaction files
        - Clear text documents
        - Scanned images (OCR)

        **🔍 Best Results:**
        - Use high-quality scans
        - Ensure text is readable
        - Include date ranges
        """)

    with tips_col2:
        st.markdown("""
        **⚙️ Troubleshooting:**
        - Low confidence? Try different file
        - Missing transactions? Check file format
        - Import errors? Verify data format

        **📞 Support:**
        - Check import results
        - Use debug mode in dashboard
        - Contact support if issues persist
        """)

    # Support Information
    st.markdown("---")
    st.subheader("📞 Support & Resources")

    st.markdown("""
    **Need Help?**
    - 📧 Contact: support@fincai.com
    - 📚 Docs: Check our documentation
    - 🐛 Report Issues: Use the feedback form

    **🔄 Data Persistence:**
    - Transactions are saved to database
    - Available across all sessions
    - Backup recommended for important data
    """)

def import_transactions_bulk(transactions: list, user_id: str):
    """Import multiple transactions from parsed data with improved error handling"""
    if not user_id:
        st.error("❌ User ID not found. Please log in again.")
        return

    if not transactions:
        st.warning("⚠️ No transactions to import.")
        return

    transaction_service = TransactionService()

    success_count = 0
    error_messages = []
    imported_ids = []

    # Show progress
    progress_bar = st.progress(0)
    status_text = st.empty()

    total_transactions = len(transactions)

    for i, txn in enumerate(transactions):
        try:
            status_text.text(f"Importing transaction {i+1}/{total_transactions}: {txn.get('description', 'Unknown')}")

            # Clean and format the amount (remove ₹ symbol and formatting)
            amount_str = str(txn.get('amount', '0')).replace('₹', '').replace(',', '').strip()
            try:
                amount = float(amount_str)
            except (ValueError, TypeError):
                amount = 0.0

            # Convert date format from dd/mm/YYYY to YYYY-MM-DD
            date_str = txn.get('date', '')
            if date_str and date_str != 'N/A':
                try:
                    # Try parsing dd/mm/YYYY format
                    day, month, year = date_str.split('/')
                    formatted_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                except (ValueError, IndexError):
                    # If parsing fails, use current date
                    from datetime import datetime
                    formatted_date = datetime.now().date().isoformat()
            else:
                from datetime import datetime
                formatted_date = datetime.now().date().isoformat()

            # Map transaction type to database format
            txn_type = txn.get('type', 'expense').lower()
            if txn_type == 'credit':
                txn_type = 'income'
            elif txn_type == 'debit':
                txn_type = 'expense'

            # Map parsed transaction to service format
            txn_data = {
                'date': formatted_date,
                'amount': amount,
                'type': txn_type,
                'category': txn.get('category', categorize_transaction(txn.get('description', ''))),
                'description': txn.get('description', ''),
                'source': 'document_parser'
            }

            # Validate data before saving
            if amount <= 0:
                error_messages.append(f"Invalid amount for: {txn.get('description', 'Unknown')}")
                continue

            # Use asyncio for async call
            import asyncio
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    transaction_service.create_transaction(user_id, txn_data)
                )
                loop.close()

                if result and result.get('success'):
                    success_count += 1
                    imported_ids.append(result.get('transaction_id'))
                else:
                    error_messages.append(f"Failed to save: {txn.get('description', 'Unknown')}")

            except Exception as e:
                error_messages.append(f"Async error for {txn.get('description', 'Unknown')}: {str(e)}")
                # Try fallback sync method if available
                try:
                    # Fallback: try to save directly to database
                    db = transaction_service.db
                    transaction_record = {
                        'user_id': user_id,
                        'date': formatted_date,
                        'amount': amount,
                        'type': txn_type,
                        'category': txn.get('category', categorize_transaction(txn.get('description', ''))),
                        'description': txn.get('description', ''),
                        'source': 'document_parser'
                    }

                    result = db.table('transactions').insert(transaction_record).execute()
                    if result.data:
                        success_count += 1
                        imported_ids.append(result.data[0]['id'])
                    else:
                        error_messages.append(f"Fallback failed for: {txn.get('description', 'Unknown')}")
                except Exception as fallback_e:
                    error_messages.append(f"Fallback error for {txn.get('description', 'Unknown')}: {str(fallback_e)}")

        except Exception as e:
            error_messages.append(f"General error for {txn.get('description', 'Unknown')}: {str(e)}")

        # Update progress
        progress_bar.progress((i + 1) / total_transactions)

    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()

    # Show results
    if success_count > 0:
        st.success(f"✅ Successfully imported {success_count} transactions!")

        # Force refresh of dashboard data by clearing any cached data
        if 'dashboard_data' in st.session_state:
            del st.session_state.dashboard_data

        # Show imported transaction IDs for verification
        with st.expander("📋 Imported Transactions"):
            st.write("Transaction IDs:")
            for txn_id in imported_ids:
                st.code(txn_id, language=None)

    if error_messages:
        with st.expander("⚠️ Import Errors"):
            for error in error_messages:
                st.error(error)

    # Add verification section
    if success_count > 0:
        st.info("💡 **Verification**: Check your Dashboard to see the imported transactions. If they don't appear after logout/login, there might be a session issue.")
        
        # Show current database status
        try:
            db = transaction_service.db
            current_transactions = db.table('transactions').select('*').eq('user_id', user_id).execute()
            st.success(f"📊 Database Status: {len(current_transactions.data) if current_transactions.data else 0} total transactions in database")
        except Exception as db_e:
            st.warning(f"Could not verify database status: {str(db_e)}")

def categorize_transaction(description: str) -> str:
    """Categorize transaction based on description"""
    desc_lower = description.lower()

    categories = {
        'food': ['restaurant', 'food', 'cafe', 'dining', 'swiggy', 'zomato'],
        'transport': ['uber', 'ola', 'taxi', 'bus', 'train', 'fuel', 'petrol', 'auto'],
        'shopping': ['amazon', 'flipkart', 'myntra', 'shopping', 'bigbasket'],
        'entertainment': ['movie', 'netflix', 'spotify', 'game', 'bookmyshow'],
        'utilities': ['electricity', 'water', 'gas', 'internet', 'phone', 'airtel', 'jio', 'vi'],
        'healthcare': ['medical', 'hospital', 'pharmacy', 'doctor', 'apollo', 'max'],
        'education': ['book', 'course', 'tuition', 'udemy', 'coursera']
    }

    for category, keywords in categories.items():
        if any(keyword in desc_lower for keyword in keywords):
            return category

    return 'other'

def generate_goal_suggestions(financial_summary: dict) -> list:
    """Generate goal suggestions based on financial summary"""
    suggestions = []

    # Emergency fund suggestion
    monthly_income = financial_summary.get('monthly_income', 0)
    if monthly_income > 0:
        emergency_amount = monthly_income * 6  # 6 months of expenses
        suggestions.append({
            'title': 'Build Emergency Fund',
            'description': f'Save ₹{emergency_amount:,.0f} for 6 months of expenses',
            'target_amount': emergency_amount,
            'target_date': None,
            'category': 'emergency'
        })

    # Debt reduction
    total_debt = financial_summary.get('total_debt', 0)
    if total_debt > 0:
        suggestions.append({
            'title': 'Pay Off Debt',
            'description': f'Clear ₹{total_debt:,.0f} in outstanding debt',
            'target_amount': total_debt,
            'target_date': None,
            'category': 'debt_reduction'
        })

    # Investment goal
    monthly_savings = financial_summary.get('monthly_savings', 0)
    if monthly_savings > 0:
        investment_goal = monthly_savings * 12 * 5  # 5 years of savings
        suggestions.append({
            'title': 'Investment Portfolio',
            'description': f'Grow investments to ₹{investment_goal:,.0f} over 5 years',
            'target_amount': investment_goal,
            'target_date': None,
            'category': 'investment'
        })

    return suggestions

def create_goal_from_suggestion(suggestion: dict, user_id: str):
    """Create a goal from suggestion"""
    goals_service = GoalsService()

    goal_data = {
        'goal_name': suggestion['title'],
        'target_amount': suggestion['target_amount'],
        'current_amount': 0,
        'target_date': suggestion.get('target_date'),
        'category': suggestion['category'],
        'priority': 'medium',
        'notes': suggestion['description']
    }

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            goals_service.create_goal(user_id, goal_data)
        )
        loop.close()

        st.success(f"✅ Goal '{suggestion['title']}' created successfully!")

    except Exception as e:
        st.error(f"❌ Failed to create goal: {str(e)}")