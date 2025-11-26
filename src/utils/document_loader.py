"""
Document loader utilities for financial knowledge base
Supports PDF, TXT, and web scraping for financial documents
"""

import os
from typing import List
from langchain.schema import Document
from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


class FinancialDocumentLoader:
    """
    Load and process financial documents for RAG
    """
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", " "]
        )
    
    def load_pdf(self, file_path: str, metadata: dict = None) -> List[Document]:
        """
        Load PDF document
        
        Args:
            file_path: Path to PDF file
            metadata: Additional metadata to add
        
        Returns:
            List of Document objects
        """
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            
            # Add custom metadata
            if metadata:
                for doc in documents:
                    doc.metadata.update(metadata)
            
            # Split into chunks
            splits = self.text_splitter.split_documents(documents)
            
            print(f"✅ Loaded PDF: {len(splits)} chunks from {file_path}")
            return splits
        except Exception as e:
            print(f"❌ Error loading PDF {file_path}: {str(e)}")
            return []
    
    def load_text(self, file_path: str, metadata: dict = None) -> List[Document]:
        """
        Load text file
        
        Args:
            file_path: Path to text file
            metadata: Additional metadata to add
        
        Returns:
            List of Document objects
        """
        try:
            loader = TextLoader(file_path, encoding='utf-8')
            documents = loader.load()
            
            # Add custom metadata
            if metadata:
                for doc in documents:
                    doc.metadata.update(metadata)
            
            # Split into chunks
            splits = self.text_splitter.split_documents(documents)
            
            print(f"✅ Loaded text file: {len(splits)} chunks from {file_path}")
            return splits
        except Exception as e:
            print(f"❌ Error loading text file {file_path}: {str(e)}")
            return []
    
    def load_from_string(self, content: str, metadata: dict = None) -> List[Document]:
        """
        Create documents from string content
        
        Args:
            content: Text content
            metadata: Document metadata
        
        Returns:
            List of Document objects
        """
        document = Document(
            page_content=content,
            metadata=metadata or {}
        )
        
        # Split into chunks
        splits = self.text_splitter.split_documents([document])
        
        print(f"✅ Created {len(splits)} chunks from string")
        return splits
    
    def load_directory(self, directory_path: str, file_types: List[str] = None) -> List[Document]:
        """
        Load all supported files from a directory
        
        Args:
            directory_path: Path to directory
            file_types: List of file extensions to load (e.g., ['.pdf', '.txt'])
        
        Returns:
            List of all Document objects
        """
        if file_types is None:
            file_types = ['.pdf', '.txt']
        
        all_documents = []
        
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_ext = os.path.splitext(file)[1].lower()
                
                if file_ext in file_types:
                    file_path = os.path.join(root, file)
                    
                    if file_ext == '.pdf':
                        docs = self.load_pdf(file_path, metadata={"source_file": file})
                    elif file_ext == '.txt':
                        docs = self.load_text(file_path, metadata={"source_file": file})
                    else:
                        continue
                    
                    all_documents.extend(docs)
        
        print(f"✅ Loaded {len(all_documents)} total chunks from {directory_path}")
        return all_documents


# Predefined Indian financial document templates
class IndianFinancialDocuments:
    """
    Pre-defined financial knowledge for Indian market
    """
    
    @staticmethod
    def get_tax_documents() -> List[Document]:
        """Get comprehensive tax-related documents"""
        documents = []
        
        # More detailed tax information
        tax_content = """
        COMPREHENSIVE GUIDE TO INCOME TAX IN INDIA (FY 2024-25)
        
        1. TAX REGIMES COMPARISON
        
        OLD TAX REGIME:
        - Allows deductions under 80C, 80D, HRA, etc.
        - Higher tax rates
        - Suitable for: People with home loans, high deductions
        
        NEW TAX REGIME:
        - Lower tax rates
        - Limited deductions (only standard deduction ₹50,000)
        - No HRA, 80C, home loan interest exemption
        - Suitable for: People with minimal deductions
        
        2. DEDUCTIONS UNDER SECTION 80
        
        80C (Max ₹1.5L):
        - EPF, PPF, ELSS, NSC
        - Life insurance premium
        - Home loan principal
        - Tuition fees (2 children)
        - SSY, Senior Citizen Savings Scheme
        
        80D (Max ₹1L):
        - Health insurance: Self ₹25K, Parents ₹25-50K
        - Preventive health checkup: ₹5K
        
        80CCD(1B) (Additional ₹50K):
        - NPS contribution
        
        80E:
        - Education loan interest (no limit)
        
        80G:
        - Donations to charitable institutions
        
        3. TDS (Tax Deducted at Source):
        - Salary: As per slab
        - Interest (FD/Savings): 10% if > ₹40K (50K for seniors)
        - Rent: 10% if > ₹2.4L annually
        - Professional fees: 10%
        
        Submit Form 15G/15H if no tax liability to avoid TDS.
        
        4. ITR FILING:
        - Due date: July 31 (for individuals)
        - Forms:
          * ITR-1: Salary + 1 house property
          * ITR-2: Multiple house properties, capital gains
          * ITR-3: Business/profession income
        
        Penalty for late filing: ₹5,000 (₹1,000 if income < ₹5L)
        
        5. TAX SAVING TIPS:
        - Max out 80C investments early in year
        - Claim HRA if paying rent
        - Keep medical insurance active
        - Invest in NPS for extra ₹50K deduction
        - Plan capital gains to use ₹1L exemption
        - Submit investment proofs to employer for lower TDS
        """
        
        documents.append(Document(
            page_content=tax_content,
            metadata={"source": "Income Tax Comprehensive Guide", "year": "2024-25"}
        ))
        
        return documents
    
    @staticmethod
    def get_investment_documents() -> List[Document]:
        """Get investment-related documents"""
        documents = []
        
        investment_content = """
        INVESTMENT GUIDE FOR INDIAN INVESTORS
        
        1. ASSET ALLOCATION BY AGE
        
        Age 20-30:
        - Equity: 70-80%
        - Debt: 20-30%
        - High risk appetite, long time horizon
        
        Age 30-40:
        - Equity: 60-70%
        - Debt: 30-40%
        - Balancing growth with stability
        
        Age 40-50:
        - Equity: 50-60%
        - Debt: 40-50%
        - Reducing risk as retirement nears
        
        Age 50-60:
        - Equity: 30-40%
        - Debt: 60-70%
        - Capital preservation focus
        
        2. MUTUAL FUND SELECTION CRITERIA
        
        Key factors:
        - 5-year returns vs benchmark
        - Expense ratio (lower is better)
        - Fund manager tenure
        - AUM (Assets Under Management)
        - Portfolio composition
        - Exit load
        
        Red flags:
        - Frequent fund manager changes
        - High expense ratio (>2% for equity)
        - Consistently underperforming benchmark
        - Very high or very low AUM
        
        3. SIP INVESTMENT STRATEGY
        
        When to increase SIP:
        - Annual salary increment
        - Bonus received
        - Market correction (opportunity)
        
        When to stop/pause SIP:
        - Financial emergency
        - Goal achieved
        - Fundamental change in fund (not market fluctuation)
        
        SIP mistakes to avoid:
        - Stopping during market fall
        - Too many funds (over-diversification)
        - Chasing recent performance
        - Ignoring expense ratio
        
        4. TAX ON INVESTMENTS
        
        Equity (Stocks/Equity MF):
        - STCG (<1 year): 15%
        - LTCG (>1 year): 10% on gains > ₹1L
        
        Debt (Debt MF/Bonds):
        - Any duration: As per income slab
        - No indexation benefit from April 2023
        
        Real Estate:
        - STCG (<2 years): As per slab
        - LTCG (>2 years): 20% with indexation
        
        Gold:
        - STCG (<3 years): As per slab
        - LTCG (>3 years): 20% with indexation
        
        5. GOAL-BASED INVESTING
        
        Emergency Fund (0-1 year):
        - Liquid funds, savings account
        - Priority #1
        
        Short-term goals (1-3 years):
        - Short duration debt funds
        - Arbitrage funds
        
        Medium-term goals (3-5 years):
        - Balanced advantage funds
        - Conservative hybrid funds
        
        Long-term goals (5+ years):
        - Equity mutual funds
        - Index funds
        - Direct stocks (if knowledge available)
        """
        
        documents.append(Document(
            page_content=investment_content,
            metadata={"source": "Investment Strategy Guide"}
        ))
        
        return documents
    
    @staticmethod
    def get_banking_documents() -> List[Document]:
        """Get banking and savings documents"""
        documents = []
        
        banking_content = """
        BANKING & SAVINGS GUIDE FOR INDIA
        
        1. SAVINGS ACCOUNT TYPES
        
        Regular Savings:
        - Interest: 2.7-3% (varies by bank)
        - Min balance: ₹5K-10K
        - Suitable for: Daily transactions
        
        Salary Account:
        - Zero balance
        - Additional benefits
        - Converts to regular if no salary for 2-3 months
        
        Senior Citizen Account:
        - Higher interest: 3.5-4%
        - Lower min balance
        - Special FD rates
        
        2. FIXED DEPOSITS
        
        Features:
        - Guaranteed returns
        - Tenure: 7 days to 10 years
        - Premature withdrawal: Penalty 0.5-1%
        
        FD Laddering Strategy:
        - Split amount into multiple FDs
        - Different maturity dates
        - Balance liquidity + returns
        
        Example: ₹3L split into:
        - ₹1L for 1 year
        - ₹1L for 2 years
        - ₹1L for 3 years
        
        3. RECURRING DEPOSITS
        
        Features:
        - Fixed monthly investment
        - Fixed tenure (6 months - 10 years)
        - Interest: Similar to FD
        - Penalty for missed installments
        
        Suitable for: Building corpus for specific goal
        
        4. POST OFFICE SCHEMES
        
        PPF (Public Provident Fund):
        - Tenure: 15 years
        - Interest: 7.1% (Q4 FY24)
        - Max: ₹1.5L/year
        - Tax: EEE status
        - Partial withdrawal after 7 years
        
        NSC (National Savings Certificate):
        - Tenure: 5 years
        - Interest: 7.7%
        - 80C deduction
        - Interest taxable
        
        SCSS (Senior Citizen Savings Scheme):
        - Age: 60+ years
        - Max: ₹30L
        - Interest: 8.2%
        - Tenure: 5 years (extendable)
        - Quarterly interest payout
        
        SSY (Sukanya Samriddhi Yojana):
        - For girl child
        - Max: ₹1.5L/year
        - Interest: 8.2%
        - Tenure: Till 21 years or marriage
        - EEE status
        
        5. CREDIT SCORE MANAGEMENT
        
        Credit score ranges:
        - 300-549: Poor
        - 550-649: Average
        - 650-749: Good
        - 750-900: Excellent
        
        How to improve:
        - Pay all bills on time
        - Keep credit utilization < 30%
        - Don't close old credit cards
        - Avoid multiple loan applications
        - Check credit report annually
        
        Get free credit report: CIBIL, Experian, Equifax
        """
        
        documents.append(Document(
            page_content=banking_content,
            metadata={"source": "Banking & Savings Guide"}
        ))
        
        return documents


# Example usage
if __name__ == "__main__":
    loader = FinancialDocumentLoader()
    
    # Load additional documents
    indian_docs = IndianFinancialDocuments()
    tax_docs = indian_docs.get_tax_documents()
    investment_docs = indian_docs.get_investment_documents()
    banking_docs = indian_docs.get_banking_documents()
    
    print(f"Tax docs: {len(tax_docs)}")
    print(f"Investment docs: {len(investment_docs)}")
    print(f"Banking docs: {len(banking_docs)}")
