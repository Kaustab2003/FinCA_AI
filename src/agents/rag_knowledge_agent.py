"""
Financial Knowledge Base Agent using LangChain RAG
Provides answers from Indian tax laws, RBI circulars, SEBI regulations, and personal finance guides
"""

import os
from typing import List, Dict, Optional
from langchain_groq import ChatGroq
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from src.config.settings import settings


class FinancialKnowledgeAgent:
    """
    RAG-based agent for financial knowledge queries
    Uses vector database to retrieve relevant information
    """
    
    def __init__(self):
        """Initialize RAG components"""
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.3,  # Lower temperature for factual answers
            groq_api_key=settings.GROQ_API_KEY
        )
        
        # Embeddings for vector database
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY,
            model="text-embedding-3-small"  # Cost-effective embedding model
        )
        
        # Vector store path
        self.persist_directory = "./data/financial_knowledge_db"
        
        # Initialize or load vector store
        self.vectorstore = self._initialize_vectorstore()
        
        # Custom prompt for financial queries
        self.prompt_template = PromptTemplate(
            template="""You are a financial expert specializing in Indian finance, taxation, and investments.
Use the following context to answer the question. If you don't know the answer based on the context, say so clearly.
Always cite which document or regulation you're referring to.

Context: {context}

Question: {question}

Answer in a clear, structured format with:
1. Direct answer
2. Relevant section/regulation reference
3. Practical example (if applicable)
4. Additional tips

Answer:""",
            input_variables=["context", "question"]
        )
        
        # Create QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}  # Retrieve top 5 relevant documents
            ),
            return_source_documents=True,
            chain_type_kwargs={"prompt": self.prompt_template}
        )
    
    def _initialize_vectorstore(self) -> Chroma:
        """Initialize or load existing vector store"""
        # Create directory if it doesn't exist
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Check if vector store already exists
        if os.path.exists(os.path.join(self.persist_directory, "chroma.sqlite3")):
            # Load existing vector store
            vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            print("✅ Loaded existing knowledge base")
        else:
            # Create new vector store with default documents
            documents = self._load_default_documents()
            vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )
            print(f"✅ Created new knowledge base with {len(documents)} documents")
        
        return vectorstore
    
    def _load_default_documents(self) -> List[Document]:
        """Load default financial knowledge documents"""
        documents = []
        
        # Indian Income Tax Information
        tax_docs = [
            Document(
                page_content="""
                Section 80C Deductions (FY 2024-25):
                Maximum deduction limit: ₹1,50,000
                
                Eligible investments:
                1. Employee Provident Fund (EPF)
                2. Public Provident Fund (PPF)
                3. Equity Linked Savings Scheme (ELSS)
                4. National Savings Certificate (NSC)
                5. Tax-saving Fixed Deposits (5-year lock-in)
                6. Life Insurance Premium
                7. Sukanya Samriddhi Yojana
                8. Principal repayment on home loan
                9. Tuition fees for children (max 2 children)
                
                Lock-in periods vary by instrument.
                """,
                metadata={"source": "Income Tax Act 1961", "section": "80C", "year": "2024-25"}
            ),
            Document(
                page_content="""
                Income Tax Slabs - Old Regime (FY 2024-25):
                
                For individuals below 60 years:
                - Up to ₹2,50,000: Nil
                - ₹2,50,001 to ₹5,00,000: 5%
                - ₹5,00,001 to ₹10,00,000: 20%
                - Above ₹10,00,000: 30%
                
                Additional:
                - Health & Education Cess: 4% on total tax
                - Surcharge: 10% if income > ₹50L, 15% if > ₹1Cr
                
                Deductions allowed: 80C, 80D, HRA, etc.
                Standard Deduction: ₹50,000 for salaried
                """,
                metadata={"source": "Income Tax Act 1961", "regime": "old", "year": "2024-25"}
            ),
            Document(
                page_content="""
                Income Tax Slabs - New Regime (FY 2024-25):
                
                - Up to ₹3,00,000: Nil
                - ₹3,00,001 to ₹7,00,000: 5%
                - ₹7,00,001 to ₹10,00,000: 10%
                - ₹10,00,001 to ₹12,00,000: 15%
                - ₹12,00,001 to ₹15,00,000: 20%
                - Above ₹15,00,000: 30%
                
                Standard Deduction: ₹50,000 (from FY 2023-24)
                No other deductions allowed (80C, HRA, etc.)
                Lower tax rates but fewer exemptions
                """,
                metadata={"source": "Income Tax Act 1961", "regime": "new", "year": "2024-25"}
            ),
            Document(
                page_content="""
                Section 80D - Health Insurance Premium:
                
                Deduction limits:
                - Self, spouse, children: Up to ₹25,000
                - Parents (below 60 years): Up to ₹25,000
                - Parents (60+ years): Up to ₹50,000
                
                Maximum total deduction: ₹1,00,000
                (₹25,000 for self + ₹50,000 for senior citizen parents + ₹5,000 preventive health checkup)
                
                Eligible: Health insurance premiums, preventive health checkups
                Payment mode: Any mode except cash
                """,
                metadata={"source": "Income Tax Act 1961", "section": "80D"}
            ),
            Document(
                page_content="""
                House Rent Allowance (HRA) Exemption:
                
                HRA exemption is the minimum of:
                1. Actual HRA received
                2. 50% of salary (metro cities) or 40% (non-metro)
                3. Rent paid minus 10% of salary
                
                Metro cities: Mumbai, Delhi, Kolkata, Chennai
                
                Requirements:
                - Must be living in rented accommodation
                - Rent receipts for annual rent > ₹1,00,000
                - Landlord PAN for annual rent > ₹1,00,000
                
                Not available in new tax regime.
                """,
                metadata={"source": "Income Tax Rules", "section": "HRA"}
            )
        ]
        documents.extend(tax_docs)
        
        # Investment & Mutual Fund Information
        investment_docs = [
            Document(
                page_content="""
                Mutual Fund Categories in India:
                
                1. Equity Funds:
                   - Large Cap: Top 100 companies by market cap
                   - Mid Cap: 101-250 companies
                   - Small Cap: 251st company onwards
                   - Multi Cap: Mix of all market caps
                   - Sectoral/Thematic: Specific sectors
                
                2. Debt Funds:
                   - Liquid Funds: Very short duration
                   - Short Duration: 1-3 years maturity
                   - Corporate Bond: High-rated corporate debt
                   - Gilt Funds: Government securities
                
                3. Hybrid Funds:
                   - Aggressive: 65-80% equity
                   - Balanced: 40-60% equity
                   - Conservative: 10-25% equity
                """,
                metadata={"source": "SEBI Categorization", "type": "Mutual Funds"}
            ),
            Document(
                page_content="""
                Equity Linked Savings Scheme (ELSS):
                
                Features:
                - Tax-saving mutual fund under Section 80C
                - Minimum 65% investment in equity
                - 3-year lock-in period (shortest among 80C options)
                - Maximum deduction: ₹1,50,000
                
                Taxation:
                - LTCG > ₹1 lakh: 10% tax (after 1 year holding)
                - STCG: 15% (before 1 year)
                
                Benefits:
                - Potential for higher returns vs traditional options
                - Wealth creation with tax benefits
                - Professional fund management
                """,
                metadata={"source": "SEBI", "type": "ELSS", "section": "80C"}
            ),
            Document(
                page_content="""
                Systematic Investment Plan (SIP):
                
                How it works:
                - Fixed amount invested at regular intervals (monthly/quarterly)
                - Rupee cost averaging benefit
                - Power of compounding over long term
                
                Benefits:
                1. Disciplined investing habit
                2. Reduces market timing risk
                3. Lower initial investment (can start from ₹500)
                4. Flexibility to pause/stop
                
                Returns calculation:
                - Use XIRR for SIP returns (accounts for multiple cash flows)
                - Long-term equity SIPs historically: 12-15% CAGR
                
                Recommended: Continue for 5+ years for equity SIPs
                """,
                metadata={"source": "Investment Guide", "type": "SIP"}
            ),
            Document(
                page_content="""
                Fixed Deposit (FD) vs Debt Mutual Funds:
                
                Fixed Deposits:
                - Guaranteed returns (bank declared rate)
                - Interest taxed as per income slab
                - Lock-in for tax-saving FDs: 5 years
                - Premature withdrawal: Penalty (usually 0.5-1%)
                - Suitable for: Capital protection, short-term goals
                
                Debt Mutual Funds:
                - Returns depend on market (not guaranteed)
                - LTCG after 3 years: 20% with indexation benefit
                - No lock-in (except ELSS)
                - Better tax efficiency for long-term
                - Suitable for: Tax-efficient parking, 3+ year goals
                
                Indexation benefit can reduce effective tax significantly.
                """,
                metadata={"source": "Comparison Guide", "type": "FD vs Debt Funds"}
            )
        ]
        documents.extend(investment_docs)
        
        # Personal Finance Tips
        finance_docs = [
            Document(
                page_content="""
                Emergency Fund Guidelines:
                
                Purpose: Cover unexpected expenses (job loss, medical emergency, repairs)
                
                Recommended amount:
                - 3-6 months of essential expenses
                - Salaried: 3-4 months
                - Self-employed/single income: 6-12 months
                
                Where to keep:
                1. Savings account (immediate access)
                2. Liquid mutual funds (1-2 days withdrawal)
                3. Short-term FDs with sweep facility
                
                Don't invest emergency fund in:
                - Equity/stocks (volatile)
                - Locked-in investments (PPF, ELSS)
                - Real estate (illiquid)
                """,
                metadata={"source": "Personal Finance Best Practices", "topic": "Emergency Fund"}
            ),
            Document(
                page_content="""
                Credit Card Best Practices:
                
                1. Pay full bill before due date (avoid interest)
                2. Keep credit utilization below 30%
                3. Never withdraw cash (high interest + fees)
                4. Track all transactions
                5. Use reward points wisely
                
                Credit card interest: 36-42% per annum (very high!)
                
                Benefits of good credit score (750+):
                - Lower loan interest rates
                - Higher credit limits
                - Pre-approved offers
                - Better negotiating power
                
                Improve score: Pay on time, low utilization, don't close old cards
                """,
                metadata={"source": "Credit Management Guide", "topic": "Credit Cards"}
            ),
            Document(
                page_content="""
                Retirement Planning in India:
                
                Retirement corpus formula:
                Required corpus = (Annual expenses × 25) / (1 - inflation adjustment)
                
                Retirement savings options:
                1. EPF (Employee Provident Fund):
                   - Mandatory for salaried (12% employee + 12% employer)
                   - Tax-free returns (approx 8-8.5%)
                   - EEE status (Exempt-Exempt-Exempt)
                
                2. PPF (Public Provident Fund):
                   - 15-year lock-in, extendable
                   - Current rate: 7.1% (Q4 FY24)
                   - Max: ₹1.5L/year, Min: ₹500/year
                   - EEE status
                
                3. NPS (National Pension System):
                   - Market-linked returns
                   - Additional ₹50,000 deduction under 80CCD(1B)
                   - 40% lump sum at maturity, 60% annuity
                   - Low cost (0.01% fund management charge)
                
                4. Retirement mutual funds:
                   - 5-year lock-in
                   - Equity exposure for growth
                   - No tax benefit
                
                Start early: Rule of 72 - Money doubles in 72/rate years
                """,
                metadata={"source": "Retirement Planning Guide", "topic": "Retirement"}
            )
        ]
        documents.extend(finance_docs)
        
        return documents
    
    def ask(self, query: str) -> Dict:
        """
        Query the financial knowledge base
        
        Args:
            query: User's question
        
        Returns:
            Dict with answer and source documents
        """
        try:
            result = self.qa_chain({"query": query})
            
            return {
                "answer": result["result"],
                "sources": [
                    {
                        "content": doc.page_content[:200] + "...",
                        "metadata": doc.metadata
                    }
                    for doc in result.get("source_documents", [])
                ],
                "status": "success"
            }
        except Exception as e:
            return {
                "answer": f"Error processing query: {str(e)}",
                "sources": [],
                "status": "error"
            }
    
    def add_documents(self, documents: List[Document]) -> bool:
        """
        Add new documents to knowledge base
        
        Args:
            documents: List of LangChain Document objects
        
        Returns:
            True if successful
        """
        try:
            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            splits = text_splitter.split_documents(documents)
            
            # Add to vector store
            self.vectorstore.add_documents(splits)
            self.vectorstore.persist()
            
            print(f"✅ Added {len(splits)} document chunks to knowledge base")
            return True
        except Exception as e:
            print(f"❌ Error adding documents: {str(e)}")
            return False
    
    def search_similar(self, query: str, k: int = 5) -> List[Document]:
        """
        Search for similar documents without generating answer
        
        Args:
            query: Search query
            k: Number of results to return
        
        Returns:
            List of similar documents
        """
        return self.vectorstore.similarity_search(query, k=k)


# Example usage
if __name__ == "__main__":
    # Initialize agent
    agent = FinancialKnowledgeAgent()
    
    # Test queries
    test_queries = [
        "What is Section 80C and how much can I save?",
        "Explain old vs new tax regime",
        "Should I invest in ELSS or PPF?",
        "How to calculate HRA exemption?"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Q: {query}")
        print(f"{'='*60}")
        result = agent.ask(query)
        print(result["answer"])
        print(f"\nSources: {len(result['sources'])} documents")
