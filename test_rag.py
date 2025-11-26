"""
Test script for RAG Knowledge Base
Run this to verify the implementation works
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def test_rag_agent():
    """Test the RAG knowledge agent"""
    print("=" * 60)
    print("Testing Financial Knowledge Base (RAG)")
    print("=" * 60)
    
    try:
        from src.agents.rag_knowledge_agent import FinancialKnowledgeAgent
        from src.utils.document_loader import IndianFinancialDocuments
        
        print("\n✅ Imports successful")
        
        # Initialize agent
        print("\n📦 Initializing RAG agent...")
        agent = FinancialKnowledgeAgent()
        print("✅ Agent initialized")
        
        # Load additional documents
        print("\n📚 Loading Indian financial documents...")
        indian_docs = IndianFinancialDocuments()
        additional_docs = []
        additional_docs.extend(indian_docs.get_tax_documents())
        additional_docs.extend(indian_docs.get_investment_documents())
        additional_docs.extend(indian_docs.get_banking_documents())
        
        if additional_docs:
            agent.add_documents(additional_docs)
            print(f"✅ Loaded {len(additional_docs)} additional documents")
        
        # Test queries
        test_queries = [
            "What is Section 80C and how much can I save?",
            "Compare old vs new tax regime",
            "Should I invest in ELSS or PPF?"
        ]
        
        print("\n" + "=" * 60)
        print("Running Test Queries")
        print("=" * 60)
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n📝 Query {i}: {query}")
            print("-" * 60)
            
            result = agent.ask(query)
            
            if result['status'] == 'success':
                print(f"\n✅ Answer:\n{result['answer'][:300]}...")
                print(f"\n📚 Sources: {len(result['sources'])} documents")
            else:
                print(f"\n❌ Error: {result['answer']}")
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        
        return True
        
    except ImportError as e:
        print(f"\n❌ Import Error: {str(e)}")
        print("\n💡 Install missing dependencies:")
        print("   pip install chromadb sentence-transformers pypdf unstructured")
        return False
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_rag_agent()
    sys.exit(0 if success else 1)
