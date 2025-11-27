"""
Document Parsing Agent - Extracts information from financial documents
"""
from typing import Dict, Any, Optional
from src.agents.base_agent import BaseAgent, AgentResponse
from src.utils.ai_client import AIClient
import structlog
import re

logger = structlog.get_logger()

class DocumentParsingAgent(BaseAgent):
    """Agent for parsing financial documents and extracting key information"""

    def _get_agent_type(self) -> str:
        return "document_parsing"

    def _build_system_prompt(self) -> str:
        base_prompt = super()._build_system_prompt()
        return f"""{base_prompt}

You are a Document Parsing Agent that extracts key financial information from documents.

Your task is to analyze financial documents and extract:
- Transaction details (amount, date, description, type)
- Account information (balance, account number)
- Personal details (name, address)
- Tax information (income, deductions, tax paid)
- Investment details (holdings, values, returns)
- Bill/Invoice details (amount due, due date, vendor)

For each document type, return structured data in JSON format.

Supported document types:
- Bank statements
- Salary slips
- Tax documents
- Invoices/Bills
- Investment statements
- Credit card statements
- Utility bills

Be precise and only extract factual information from the document text."""

    async def process(self, query: str, user_context: Dict[str, Any]) -> AgentResponse:
        """
        Parse document text and extract financial information

        Args:
            query: Document text to parse
            user_context: Additional context (document type, etc.)

        Returns:
            AgentResponse with extracted information
        """
        try:
            document_type = user_context.get('document_type', 'general')
            document_text = query  # The query contains the document text

            # Check if this is CSV data and parse directly
            if self._is_csv_data(document_text):
                return await self._parse_csv_document(document_text, document_type)

            ai_client = AIClient()

            # Preprocess text for better parsing
            cleaned_text = self._preprocess_text(document_text)

            prompt = f"""Extract key financial information from this {document_type} document.

Document Text:
{cleaned_text}

{self._build_system_prompt()}

Return the extracted information in this JSON format:
{{
  "document_type": "{document_type}",
  "extracted_data": {{
    "transactions": [],
    "account_info": {{}},
    "personal_info": {{}},
    "financial_summary": {{}},
    "key_dates": [],
    "amounts": []
  }},
  "confidence": 0.0,
  "notes": ""
}}

Focus on factual extraction. If information is not available, use empty arrays/objects."""

            response = await ai_client.generate_response(
                prompt=prompt,
                model=self.model,
                temperature=0.1  # Low temperature for accurate extraction
            )

            # Parse JSON response
            import json
            import re
            try:
                # Try to extract JSON from the response
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group(1))
                else:
                    # Try to find JSON-like structure
                    json_match = re.search(r'\{.*\}', response, re.DOTALL)
                    if json_match:
                        result = json.loads(json_match.group(0))
                    else:
                        # Fallback: create basic structure from response
                        result = {
                            'document_type': document_type,
                            'extracted_data': {
                                'transactions': [],
                                'account_info': {},
                                'personal_info': {},
                                'financial_summary': {},
                                'key_dates': [],
                                'amounts': []
                            },
                            'confidence': 0.1,
                            'notes': 'Could not parse structured data'
                        }

                extracted_data = result.get('extracted_data', {})
                confidence = result.get('confidence', 0.5)
                notes = result.get('notes', '')

                # Format response for display
                content = self._format_extracted_data(extracted_data, confidence, notes)

                return AgentResponse(
                    content=content,
                    agent_name=self.agent_name,
                    agent_type=self.agent_type,
                    confidence=confidence,
                    metadata={
                        'document_type': document_type,
                        'extracted_data': extracted_data,
                        'raw_response': response
                    }
                )

            except json.JSONDecodeError:
                return AgentResponse(
                    content=f"**Document Analysis:**\n\n{response}\n\n⚠️ Could not parse structured data from response.",
                    agent_name=self.agent_name,
                    agent_type=self.agent_type,
                    confidence=0.3,
                    metadata={'error': 'JSON parsing failed', 'raw_response': response}
                )

        except Exception as e:
            logger.error(f"Error parsing document: {e}")
            return AgentResponse(
                content="❌ Sorry, I couldn't parse this document. Please ensure it's a clear financial document and try again.",
                agent_name=self.agent_name,
                agent_type=self.agent_type,
                confidence=0.0,
                metadata={'error': str(e)}
            )

    def _is_csv_data(self, text: str) -> bool:
        """Check if the text appears to be CSV data"""
        lines = text.strip().split('\n')
        if len(lines) < 2:
            return False

        # Check if first line looks like headers
        header_line = lines[0].strip()
        if ',' not in header_line:
            return False

        # Check if we have multiple columns (at least 3 commas)
        headers = header_line.split(',')
        if len(headers) < 3:
            return False

        # Check if second line has similar structure
        if len(lines) > 1:
            data_line = lines[1].strip()
            data_cols = data_line.split(',')
            if len(data_cols) != len(headers):
                return False

        # Check for common financial CSV headers
        financial_headers = ['date', 'amount', 'description', 'category', 'type']
        header_lower = header_line.lower()
        if any(header in header_lower for header in financial_headers):
            return True

        return False

    async def _parse_csv_document(self, csv_text: str, document_type: str) -> AgentResponse:
        """Parse CSV data directly without AI processing"""
        try:
            import csv
            import io
            from datetime import datetime

            # Parse CSV
            csv_reader = csv.DictReader(io.StringIO(csv_text))
            rows = list(csv_reader)

            if not rows:
                return AgentResponse(
                    content="❌ CSV file appears to be empty or invalid.",
                    agent_name=self.agent_name,
                    agent_type=self.agent_type,
                    confidence=0.0,
                    metadata={'error': 'Empty CSV'}
                )

            # Extract transactions
            transactions = []
            total_income = 0.0
            total_expenses = 0.0
            key_dates = []

            for row in rows:
                # Extract transaction data
                date_str = row.get('Date', row.get('date', ''))
                description = row.get('Description', row.get('description', ''))
                amount_str = row.get('Amount', row.get('amount', '0'))
                category = row.get('Category', row.get('category', 'Other'))
                txn_type = row.get('Type', row.get('type', 'expense'))

                # Parse amount
                try:
                    # Remove currency symbols and clean
                    amount_clean = amount_str.replace('₹', '').replace('$', '').replace(',', '').strip()
                    amount = float(amount_clean)
                except (ValueError, AttributeError):
                    amount = 0.0

                # Parse date
                try:
                    if date_str:
                        parsed_date = datetime.strptime(date_str, '%Y-%m-%d').strftime('%d/%m/%Y')
                    else:
                        parsed_date = 'N/A'
                except ValueError:
                    parsed_date = date_str or 'N/A'

                # Build transaction
                transaction = {
                    'date': parsed_date,
                    'description': description,
                    'amount': f"₹{amount:,.2f}",
                    'category': category,
                    'type': 'Credit' if txn_type.lower() == 'income' else 'Debit'
                }
                transactions.append(transaction)

                # Track dates
                if parsed_date != 'N/A' and parsed_date not in key_dates:
                    key_dates.append(parsed_date)

                # Calculate totals (use absolute values for expenses)
                if txn_type.lower() == 'income':
                    total_income += amount
                else:
                    total_expenses += abs(amount)  # Use absolute value for expenses

            # Create financial summary
            net_balance = total_income - total_expenses
            financial_summary = {
                'total_income': f"₹{total_income:,.2f}",
                'total_expenses': f"₹{total_expenses:,.2f}",
                'net_balance': f"₹{net_balance:,.2f}"
            }

            # Build extracted data
            extracted_data = {
                'transactions': transactions,
                'account_info': {
                    'account_number': 'CSV-IMPORT-001',
                    'account_type': 'General'
                },
                'personal_info': {},
                'financial_summary': financial_summary,
                'key_dates': sorted(key_dates),
                'amounts': [f"₹{total_income:,.2f}", f"₹{total_expenses:,.2f}", f"₹{net_balance:,.2f}"]
            }

            # Format response for display
            content = self._format_extracted_data(extracted_data, 0.95, f"Successfully parsed {len(transactions)} transactions from CSV data.")

            return AgentResponse(
                content=content,
                agent_name=self.agent_name,
                agent_type=self.agent_type,
                confidence=0.95,  # High confidence for structured CSV data
                metadata={
                    'document_type': 'csv_financial_data',
                    'extracted_data': extracted_data,
                    'parsing_method': 'direct_csv_parsing',
                    'transaction_count': len(transactions)
                }
            )

        except Exception as e:
            logger.error(f"Error parsing CSV: {e}")
            return AgentResponse(
                content="❌ Error parsing CSV file. Please ensure it's a valid financial transaction CSV.",
                agent_name=self.agent_name,
                agent_type=self.agent_type,
                confidence=0.0,
                metadata={'error': str(e), 'parsing_method': 'csv_failed'}
            )

    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess document text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())

        # Remove common OCR artifacts
        text = re.sub(r'[|]', ' ', text)

        # Normalize currency symbols
        text = re.sub(r'[₹$£€]\s*', '₹', text)

        return text

    def _format_extracted_data(self, data: Dict[str, Any], confidence: float, notes: str) -> str:
        """Format extracted data for display"""
        sections = []

        sections.append(f"## 📄 Document Analysis (Confidence: {confidence:.1%})")

        # Transactions
        transactions = data.get('transactions', [])
        if transactions:
            sections.append("### 💳 Transactions Found")
            for i, txn in enumerate(transactions[:5]):  # Limit to 5
                amount = txn.get('amount', 'N/A')
                date = txn.get('date', 'N/A')
                desc = txn.get('description', 'N/A')
                sections.append(f"{i+1}. {amount} on {date} - {desc}")
            if len(transactions) > 5:
                sections.append(f"... and {len(transactions) - 5} more transactions")

        # Account Info
        account_info = data.get('account_info', {})
        if account_info:
            sections.append("### 🏦 Account Information")
            for key, value in account_info.items():
                sections.append(f"- **{key.title()}:** {value}")

        # Financial Summary
        financial_summary = data.get('financial_summary', {})
        if financial_summary:
            sections.append("### 💰 Financial Summary")
            for key, value in financial_summary.items():
                sections.append(f"- **{key.title()}:** ₹{value}")

        # Key Dates
        key_dates = data.get('key_dates', [])
        if key_dates:
            sections.append("### 📅 Key Dates")
            for date_info in key_dates[:3]:
                sections.append(f"- {date_info}")

        # Notes
        if notes:
            sections.append(f"### 📝 Notes\n{notes}")

        if not any(data.values()):
            sections.append("### ⚠️ No structured data extracted\nThe document may not contain clear financial information or may need manual review.")

        return "\n\n".join(sections)

    def parse_document_sync(self, document_text: str, document_type: str = "general") -> Dict[str, Any]:
        """Synchronous version for use in services"""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            self.process(document_text, {'document_type': document_type})
        )
        loop.close()

        return {
            'parsed_data': result.metadata.get('extracted_data', {}),
            'confidence': result.confidence,
            'formatted_content': result.content,
            'agent_response': result
        }