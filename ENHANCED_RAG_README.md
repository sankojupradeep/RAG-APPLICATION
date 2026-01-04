# Enhanced RAG System

An advanced Retrieval-Augmented Generation (RAG) system that performs comprehensive document analysis for **all supported document types** instead of simple keyword-based indexing.

## 📁 Supported Document Types

✅ **PDF** - Academic papers, reports, books  
✅ **TXT** - Plain text documents  
✅ **CSV** - Tabular data, datasets  
✅ **Excel** (.xlsx, .xls) - Spreadsheets, data tables  
✅ **Word** (.docx) - Documents, reports  
✅ **JSON** - Structured data, API responses, configurations  

## 🚀 Key Features

### Original RAG vs Enhanced RAG

| Feature | Original RAG | Enhanced RAG |
|---------|-------------|--------------|
| **Document Types** | PDF, TXT, CSV, Excel, Word, JSON | **Same + Enhanced Analysis** |
| **Document Processing** | Page-by-page loading, fixed chunking | **Comprehensive analysis with file-type specific handling** |
| **Indexing** | Single FAISS index | **Multi-level indexing (document + chunk)** |
| **Search Strategy** | Direct chunk similarity | **Hybrid search (document → chunk filtering)** |
| **Context Building** | Simple chunk concatenation | **Rich context with summaries + relevant content** |
| **Metadata** | Basic (source, page) | **Rich (topics, structure, file-type specific info)** |
| **Question Answering** | Simple prompt | **Structured analysis with comprehensive context** |

### Enhanced Capabilities

✅ **Multi-Format Support**: PDF, TXT, CSV, Excel, Word, JSON documents  
✅ **Document-Level Understanding**: Analyzes entire document structure and content  
✅ **File-Type Specific Analysis**: Tailored processing for each document type  
✅ **Multi-Level Search**: Document-level + chunk-level retrieval  
✅ **Comprehensive Context**: Document summaries + relevant chunks  
✅ **Rich Metadata**: Topics, structure, file-type specific information  
✅ **Semantic Chunking**: Context-aware text segmentation adapted per file type  
✅ **Hybrid Retrieval**: Combines multiple search strategies  
✅ **Cross-Document Analysis**: Better handling of multi-document questions  

## 📊 File-Type Specific Features

### PDF Documents
- Page-by-page analysis
- Figure and table detection
- Reference extraction
- Academic paper structure recognition

### CSV/Excel Files  
- Column header extraction
- Row-based chunking with headers
- Data type analysis
- Statistical overview

### JSON Files
- Nested structure analysis
- Key-value relationship mapping
- Hierarchical chunking
- Schema detection

### Word Documents
- Heading extraction
- List and bullet point detection
- Paragraph structure analysis
- Style-based content categorization

### Text Files
- Section detection
- Topic extraction
- Paragraph-based chunking
- Content type identification  

## 📁 Project Structure

```
RAG-Tutorials/
├── src/
│   ├── document_analyzer.py      # Comprehensive PDF analysis
│   ├── enhanced_vectorstore.py   # Multi-level vector storage
│   ├── enhanced_search.py        # Advanced RAG search system
│   ├── search.py                 # Original RAG system
│   ├── vectorstore.py           # Original vector store
│   ├── embedding.py             # Original embedding pipeline
│   └── data_loader.py           # Document loading utilities
├── enhanced_rag_demo.py         # Interactive demo script
├── compare_rag_systems.py       # Comparison between systems
├── enhanced_requirements.txt    # Dependencies for enhanced system
└── data/                        # Place your PDF files here
```

## 🛠️ Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd RAG-Tutorials
```

2. **Install dependencies**:
```bash
pip install -r enhanced_requirements.txt
```

3. **Set up environment variables**:
Create a `.env` file with your API keys:
```env
GROQ_API_KEY=your_groq_api_key_here
```

4. **Add your documents**:
```bash
mkdir data
# Copy your documents to the data/ directory
# Supported: PDF, TXT, CSV, Excel (.xlsx), Word (.docx), JSON
```

## 🧪 Testing All Document Types

Run the comprehensive test suite:
```bash
python test_all_document_types.py
```

This will create sample documents of all types and verify the system works correctly.

## 🚀 Quick Start

### Basic Usage

```python
from src.enhanced_search import EnhancedRAGSearch

# Initialize the enhanced RAG system
enhanced_rag = EnhancedRAGSearch(data_dir="data")

# Ask a question
answer = enhanced_rag.ask_question("What are the main topics in these documents?")
print(answer)
```

### Interactive Demo

Run the interactive demo:
```bash
python enhanced_rag_demo.py
```

### Compare Systems

Compare original vs enhanced RAG:
```bash
python compare_rag_systems.py
```

## 📊 Advanced Usage

### Comprehensive Search with Different Depths

```python
# Quick analysis (2 docs, 5 chunks)
result = enhanced_rag.comprehensive_search("your question", analysis_depth="quick")

# Standard analysis (3 docs, 8 chunks) 
result = enhanced_rag.comprehensive_search("your question", analysis_depth="standard")

# Deep analysis (5 docs, 15 chunks)
result = enhanced_rag.comprehensive_search("your question", analysis_depth="deep")
```

### Document Collection Analysis

```python
# Analyze your document collection
collection_info = enhanced_rag.analyze_document_collection()
print(f"Total documents: {collection_info['total_documents']}")
print(f"Total chunks: {collection_info['total_chunks']}")

# List available documents
documents = enhanced_rag.list_available_documents()
print("Available documents:", documents)

# Get specific document summary
summary = enhanced_rag.get_document_summary("document_name.pdf")
print(summary)
```

### Multi-Level Search

```python
# Document-level search
docs = enhanced_rag.vectorstore.search_documents("machine learning", top_k=3)

# Chunk-level search
chunks = enhanced_rag.vectorstore.search_chunks("neural networks", top_k=10)

# Hybrid search (recommended)
results = enhanced_rag.vectorstore.hybrid_search("deep learning applications")
```

## 🔧 Configuration

### Customizing the Enhanced RAG System

```python
enhanced_rag = EnhancedRAGSearch(
    persist_dir="custom_store",           # Vector store directory
    embedding_model="all-MiniLM-L6-v2",  # Embedding model
    llm_model="gemma2-9b-it",            # LLM model
    data_dir="custom_data"               # PDF files directory
)
```

### Document Analyzer Settings

```python
from src.document_analyzer import DocumentAnalyzer

analyzer = DocumentAnalyzer(
    model_name="all-MiniLM-L6-v2"  # Embedding model for analysis
)

# Analyze a single document
analysis = analyzer.analyze_document("path/to/document.pdf")
```

## 📈 Performance Comparison

### Speed vs Quality Trade-offs

- **Original RAG**: Faster setup, good for simple queries
- **Enhanced RAG**: More comprehensive analysis, better for complex questions

### Memory Usage

- **Original RAG**: Lower memory footprint
- **Enhanced RAG**: Higher memory usage due to multi-level indexing

### Accuracy

- **Original RAG**: Good for keyword-based queries
- **Enhanced RAG**: Superior for analytical and cross-document questions

## 🎯 Use Cases

### When to Use Enhanced RAG

✅ **Research Analysis**: Analyzing academic papers, reports  
✅ **Document Synthesis**: Combining information from multiple sources  
✅ **Complex Queries**: Questions requiring deep understanding  
✅ **Cross-Document Analysis**: Finding connections between documents  
✅ **Comprehensive Summaries**: Detailed document overviews  

### When to Use Original RAG

✅ **Simple Queries**: Direct fact-finding questions  
✅ **Resource Constraints**: Limited memory/compute  
✅ **Quick Setup**: Rapid prototyping  
✅ **Keyword Search**: Simple term-based retrieval  

## 🔍 Example Questions

The enhanced system excels at:

- "What are the main methodologies discussed across all documents?"
- "Compare and contrast the approaches mentioned in different papers"
- "Summarize the key findings and their implications"
- "What are the practical applications of the concepts discussed?"
- "How do the different documents relate to each other?"

## 🛠️ Troubleshooting

### Common Issues

1. **No PDF files found**: Ensure PDF files are in the `data/` directory
2. **GROQ API key missing**: Set `GROQ_API_KEY` in your `.env` file
3. **Memory issues**: Reduce `analysis_depth` or process fewer documents
4. **Slow performance**: Use smaller embedding models or reduce chunk sizes

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.INFO)
```

## 📚 API Reference

### EnhancedRAGSearch Class

#### Methods

- `ask_question(question, depth="standard")`: Simple Q&A interface
- `comprehensive_search(query, analysis_depth)`: Full search with metadata
- `analyze_document_collection()`: Collection statistics
- `list_available_documents()`: Available document list
- `get_document_summary(file_name)`: Specific document summary

#### Parameters

- `analysis_depth`: "quick", "standard", or "deep"
- `persist_dir`: Vector store directory
- `embedding_model`: SentenceTransformer model name
- `llm_model`: Groq LLM model name
- `data_dir`: PDF files directory

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built on top of LangChain, FAISS, and SentenceTransformers
- Uses Groq API for LLM inference
- Inspired by advanced RAG research and best practices