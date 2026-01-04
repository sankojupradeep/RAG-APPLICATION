# Enhanced RAG System with Multi-Document Support

A comprehensive Retrieval-Augmented Generation (RAG) system that supports multiple document types with ChatGPT-like web interfaces and advanced document analysis capabilities.

## 🚀 Features

### Multi-Document Support
- **PDF Documents**: Advanced parsing with PyMuPDF and PyPDF
- **Text Files**: Plain text document processing
- **CSV Files**: Structured data analysis and querying
- **Excel Files**: Spreadsheet data extraction and analysis
- **Word Documents**: DOCX file processing
- **JSON Files**: Structured JSON data handling

### Advanced Search Capabilities
- **Hybrid Search**: Combines semantic similarity with keyword matching
- **Balanced Retrieval**: Ensures results from all documents, not biased toward one
- **Multi-level Indexing**: Document-level and chunk-level search
- **Cross-Document Synthesis**: Combines information from multiple sources

### Web Interfaces
- **Advanced Streamlit App**: Modern UI with drag-and-drop upload, animations, and mobile responsiveness
- **Basic Streamlit App**: Simple interface for quick testing
- **Flask API**: RESTful API for integration with other applications

### Enhanced Features
- **Real-time Processing**: Live document analysis and indexing
- **Source Citations**: Tracks and displays source documents for each response
- **Performance Metrics**: Response time and accuracy tracking
- **Error Handling**: Robust error management and user feedback

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Virtual environment (recommended)
- GROQ API key (free from [console.groq.com](https://console.groq.com/keys))

### Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <your-repository-url>
   cd RAG-Tutorials
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv env
   
   # On Windows
   env\Scripts\activate
   
   # On macOS/Linux
   source env/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r enhanced_requirements.txt
   ```

4. **Configure Environment Variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env file and add your API keys
   # GROQ_API_KEY=your_actual_groq_api_key_here
   ```

## 🚀 Quick Start

### Option 1: Launch All Interfaces (Recommended)
```bash
python launch_chat.py
```
This will show you all available interfaces and let you choose which one to run.

### Option 2: Run Specific Interface

**Advanced Streamlit App (Recommended)**
```bash
streamlit run advanced_chat_app.py
```

**Basic Streamlit App**
```bash
streamlit run streamlit_app.py
```

**Flask API**
```bash
python flask_chat_app.py
```

## 📁 Project Structure

```
RAG-Tutorials/
├── src/                          # Core system modules
│   ├── document_analyzer.py      # Multi-document analysis engine
│   ├── enhanced_vectorstore.py   # Advanced vector storage with hybrid search
│   ├── enhanced_search.py        # Balanced search algorithms
│   └── embedding.py              # Text embedding utilities
├── advanced_chat_app.py          # Modern Streamlit interface
├── streamlit_app.py              # Basic Streamlit interface
├── flask_chat_app.py             # Flask API interface
├── launch_chat.py                # Interface launcher
├── enhanced_requirements.txt     # Python dependencies
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

## 📖 Documentation

- **[Enhanced RAG README](ENHANCED_RAG_README.md)**: Technical details and architecture
- **[Web Interface Guide](WEB_INTERFACE_README.md)**: Interface usage and features
- **[Project Presentation Guide](PROJECT_PRESENTATION_README.md)**: Academic presentation materials

## 🎯 Usage Examples

### 1. Upload Documents
- Drag and drop files into the web interface
- Supported formats: PDF, TXT, CSV, XLSX, DOCX, JSON
- System automatically analyzes and indexes content

### 2. Ask Questions
- **Single Document**: "What are the main findings in this research paper?"
- **Multi-Document**: "Compare the methodologies across all uploaded papers"
- **Data Analysis**: "What trends do you see in the sales data?"
- **Cross-Reference**: "How do the conclusions in document A relate to document B?"

### 3. Advanced Features
- **Quick Actions**: Pre-defined analysis templates
- **Export Results**: Save conversations and analysis
- **Source Tracking**: See which documents contributed to each answer
- **Performance Metrics**: Monitor response times and accuracy

## 🔧 Configuration

### API Keys
The system supports multiple LLM providers:
- **GROQ** (Recommended): Fast and free tier available
- **OpenAI**: GPT-3.5/GPT-4 models
- **Anthropic**: Claude models

### Model Configuration
Default embedding model: `all-MiniLM-L6-v2`
- Lightweight and efficient
- Good balance of speed and accuracy
- Can be changed in the configuration files

## 🧪 Testing

### Run System Tests
```bash
python -m pytest tests/ -v
```

### Test Individual Components
```bash
# Test document analyzer
python src/document_analyzer.py

# Test vector store
python src/enhanced_vectorstore.py

# Test search engine
python src/enhanced_search.py
```

## 🐛 Troubleshooting

### Common Issues

1. **"GROQ_API_KEY not found"**
   - Ensure you've created `.env` file from `.env.example`
   - Add your actual API key to the `.env` file

2. **"No supported documents found"**
   - Check file formats are supported (PDF, TXT, CSV, XLSX, DOCX, JSON)
   - Ensure files are not corrupted
   - Try uploading through the web interface

3. **"Import Error: No module named..."**
   - Ensure virtual environment is activated
   - Run `pip install -r enhanced_requirements.txt`

4. **Slow Performance**
   - Check internet connection for API calls
   - Consider using local models for embedding
   - Reduce document size or chunk size

### Getting Help
- Check the documentation files in the repository
- Review error messages in the console
- Ensure all dependencies are properly installed

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangChain**: Framework for LLM applications
- **Streamlit**: Web interface framework
- **FAISS**: Vector similarity search
- **GROQ**: Fast LLM inference
- **Sentence Transformers**: Text embedding models

## 📊 Performance Metrics

- **Document Processing**: ~2-5 seconds per document
- **Query Response**: ~1-3 seconds average
- **Supported File Size**: Up to 100MB per document
- **Concurrent Users**: Tested with up to 10 simultaneous users

## 🔮 Future Enhancements

- [ ] Support for more document types (PowerPoint, HTML, Markdown)
- [ ] Advanced analytics dashboard
- [ ] User authentication and document management
- [ ] Integration with cloud storage (Google Drive, Dropbox)
- [ ] Mobile app development
- [ ] Multi-language support
- [ ] Advanced visualization tools

---

**Built with ❤️ for comprehensive document analysis and intelligent question answering**