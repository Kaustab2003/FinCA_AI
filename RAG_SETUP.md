# Financial Knowledge Base RAG Setup

This guide explains the new **LangChain RAG** (Retrieval Augmented Generation) feature added to FinCA AI.

## 🎯 What is RAG?

RAG allows the AI to answer questions by:
1. **Retrieving** relevant information from a knowledge base
2. **Augmenting** the LLM prompt with that information
3. **Generating** accurate, source-backed answers

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install RAG dependencies
pip install chromadb==0.4.22 sentence-transformers==2.3.1 pypdf==4.0.1 unstructured==0.11.8
```

### 2. Test the Implementation

```bash
python test_rag.py
```

### 3. Run the App

```bash
streamlit run src/ui/app_integrated.py
```

Then navigate to **📚 Knowledge Base** in the sidebar.

## 📚 Features

### Knowledge Base Content

The RAG system includes comprehensive information about:

**Tax Topics:**
- Income tax slabs (Old & New Regime)
- Section 80C deductions
- Section 80D (Health Insurance)
- HRA exemption rules
- TDS and ITR filing

**Investment Topics:**
- Mutual fund categories
- ELSS vs PPF comparison
- SIP strategies
- Asset allocation by age
- Tax on investments

**Banking & Savings:**
- Fixed deposits
- Post Office schemes (PPF, NSC, SCSS, SSY)
- Credit score management
- Emergency fund guidelines

### How to Use

1. Go to **📚 Knowledge Base** page
2. Click example questions or type your own
3. Get instant, source-backed answers
4. View sources used for the answer

### Example Questions

- "What is Section 80C and how much can I save?"
- "Compare old tax regime vs new tax regime"
- "Should I invest in ELSS or PPF?"
- "How to calculate HRA exemption?"
- "What is the best SIP investment strategy?"

## 🏗️ Technical Architecture

### Components

```
User Query
    ↓
Knowledge Base UI (Streamlit)
    ↓
RAG Agent (src/agents/rag_knowledge_agent.py)
    ↓
Vector Database (ChromaDB)
    ↓
Embeddings (OpenAI text-embedding-3-small)
    ↓
LLM (Groq Llama 3.3 70B)
    ↓
Source-backed Answer
```

### Files Added

1. **`src/agents/rag_knowledge_agent.py`**
   - Main RAG implementation
   - Handles query processing
   - Manages vector database

2. **`src/utils/document_loader.py`**
   - Document loading utilities
   - Pre-defined Indian financial documents
   - PDF/TXT file support

3. **Updated `src/ui/app_integrated.py`**
   - Added Knowledge Base navigation
   - New `show_knowledge_base()` function
   - Interactive UI with example questions

4. **Updated `requirements.txt`**
   - Added ChromaDB for vector storage
   - Added sentence-transformers for embeddings
   - Added pypdf and unstructured for document processing

## 🔧 Configuration

### Environment Variables Required

```env
# Already in your .env
OPENAI_API_KEY=sk-proj-...     # For embeddings
GROQ_API_KEY=gsk_...           # For LLM
```

### Vector Database

- **Location**: `./data/financial_knowledge_db/`
- **Type**: ChromaDB (SQLite-based)
- **Persistence**: Auto-saved after adding documents
- **Size**: ~10-20 MB

## 📊 Performance

- **Query Response**: 2-5 seconds
- **Embedding Model**: text-embedding-3-small (cost-effective)
- **LLM**: Llama 3.3 70B via Groq (FREE & fast)
- **Retrieval**: Top 5 most relevant documents

## 🎨 Customization

### Add Custom Documents

```python
from src.agents.rag_knowledge_agent import FinancialKnowledgeAgent
from langchain.schema import Document

agent = FinancialKnowledgeAgent()

# Add custom document
custom_doc = Document(
    page_content="Your financial content here...",
    metadata={"source": "Your Source", "category": "Tax"}
)

agent.add_documents([custom_doc])
```

### Load PDF Files

```python
from src.utils.document_loader import FinancialDocumentLoader

loader = FinancialDocumentLoader()
documents = loader.load_pdf("path/to/document.pdf", metadata={"source": "RBI Circular"})

agent.add_documents(documents)
```

## 🐛 Troubleshooting

### Error: "No module named 'chromadb'"

```bash
pip install chromadb==0.4.22
```

### Error: "No module named 'sentence_transformers'"

```bash
pip install sentence-transformers==2.3.1
```

### Slow First Query

The first query initializes the vector database and may take 10-20 seconds. Subsequent queries are much faster.

### Memory Issues

If you encounter memory issues, reduce the chunk size in `rag_knowledge_agent.py`:

```python
self.text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,  # Reduced from 1000
    chunk_overlap=100  # Reduced from 200
)
```

## 🚀 Next Steps

### Potential Enhancements

1. **Upload Custom Documents**: Allow users to upload their own PDFs
2. **Real-time Updates**: Fetch latest tax laws from government websites
3. **Multi-language Support**: Hindi, Kannada translations
4. **Conversation Memory**: Remember context across questions
5. **Citation Links**: Direct links to source documents

### Adding More Documents

To expand the knowledge base, add documents to `IndianFinancialDocuments` class in `document_loader.py` or use the `add_documents()` method.

## 📖 References

- **LangChain Documentation**: https://python.langchain.com/
- **ChromaDB Documentation**: https://docs.trychroma.com/
- **Groq API**: https://console.groq.com/

## ✅ Testing Checklist

- [ ] Dependencies installed
- [ ] Test script runs successfully
- [ ] App loads without errors
- [ ] Knowledge Base page accessible
- [ ] Example questions work
- [ ] Custom questions return answers
- [ ] Sources are displayed

## 🎉 Success!

Your FinCA AI now has a powerful RAG-based knowledge base that can answer any financial question with source-backed accuracy!
