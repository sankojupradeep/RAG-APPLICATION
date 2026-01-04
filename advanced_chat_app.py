"""
Advanced ChatGPT-like Interface with File Upload
Enhanced web interface for document Q&A with drag-and-drop file upload
"""
import streamlit as st
import os
import sys
import time
import shutil
from pathlib import Path
import json
from datetime import datetime
import tempfile

# Add src to path
sys.path.append('src')

from src.enhanced_search import EnhancedRAGSearch

# Page configuration
st.set_page_config(
    page_title="Smart Document Chat",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .chat-container {
        max-height: 600px;
        overflow-y: auto;
        padding: 1rem;
        border: 1px solid #e0e0e0;
        border-radius: 15px;
        background: #fafafa;
        margin-bottom: 1rem;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 5px 20px;
        margin: 0.5rem 0 0.5rem auto;
        max-width: 80%;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .assistant-message {
        background: white;
        color: #333;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 20px 5px;
        margin: 0.5rem auto 0.5rem 0;
        max-width: 80%;
        border: 1px solid #e0e0e0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    .message-time {
        font-size: 0.8rem;
        opacity: 0.7;
        margin-top: 0.5rem;
    }
    
    .document-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease;
    }
    
    .document-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(240, 147, 251, 0.3);
    }
    
    .upload-area {
        border: 2px dashed #667eea;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        background: #f8f9ff;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        border-color: #764ba2;
        background: #f0f2ff;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.7rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 2px solid #e0e0e0;
        padding: 0.7rem 1.5rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .quick-action-btn {
        background: white;
        border: 2px solid #667eea;
        color: #667eea;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.25rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .quick-action-btn:hover {
        background: #667eea;
        color: white;
        transform: translateY(-1px);
    }
    
    .typing-indicator {
        display: flex;
        align-items: center;
        padding: 1rem;
        color: #666;
    }
    
    .typing-dots {
        display: inline-flex;
        margin-left: 0.5rem;
    }
    
    .typing-dots span {
        height: 8px;
        width: 8px;
        background: #667eea;
        border-radius: 50%;
        margin: 0 2px;
        animation: typing 1.4s infinite ease-in-out;
    }
    
    .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
    .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
    
    @keyframes typing {
        0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
        40% { transform: scale(1); opacity: 1; }
    }
    
    .source-info {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 0.5rem 1rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "rag_system" not in st.session_state:
    st.session_state.rag_system = None
if "system_ready" not in st.session_state:
    st.session_state.system_ready = False
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
if "processing" not in st.session_state:
    st.session_state.processing = False

def save_uploaded_files(uploaded_files):
    """Save uploaded files to data directory"""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    saved_files = []
    for uploaded_file in uploaded_files:
        file_path = data_dir / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        saved_files.append(str(file_path))
    
    return saved_files

def initialize_rag_system():
    """Initialize the RAG system"""
    try:
        rag_system = EnhancedRAGSearch(data_dir="data")
        collection_info = rag_system.analyze_document_collection()
        
        if "error" in collection_info:
            return None, "No documents found. Please upload documents first."
        
        return rag_system, None
    except Exception as e:
        return None, f"Error initializing system: {str(e)}"

def display_typing_indicator():
    """Display typing indicator"""
    st.markdown("""
    <div class="typing-indicator">
        🤖 Assistant is thinking
        <div class="typing-dots">
            <span></span>
            <span></span>
            <span></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_message(role, content, timestamp, search_results=None):
    """Display a chat message with enhanced styling"""
    if role == "user":
        st.markdown(f"""
        <div class="user-message">
            <div>{content}</div>
            <div class="message-time">You • {timestamp}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="assistant-message">
            <div><strong>🤖 Assistant</strong></div>
            <div style="margin-top: 0.5rem;">{content}</div>
            <div class="message-time">{timestamp}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show sources if available
        if search_results and search_results.get("relevant_documents"):
            with st.expander("📚 Sources", expanded=False):
                for i, doc in enumerate(search_results["relevant_documents"][:3], 1):
                    doc_name = os.path.basename(doc["document"]["file_path"])
                    relevance = doc["relevance_score"]
                    st.markdown(f"""
                    <div class="source-info">
                        <strong>{i}. {doc_name}</strong><br>
                        <small>Relevance: {relevance:.3f}</small>
                    </div>
                    """, unsafe_allow_html=True)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>💬 Smart Document Chat</h1>
        <p>Upload documents and chat with your AI assistant</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.title("📁 Document Manager")
        
        # File upload section
        st.markdown("### Upload Documents")
        uploaded_files = st.file_uploader(
            "Choose files",
            type=['pdf', 'txt', 'csv', 'xlsx', 'docx', 'json'],
            accept_multiple_files=True,
            help="Supported formats: PDF, TXT, CSV, Excel, Word, JSON"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} files selected")
            
            if st.button("📤 Process Files"):
                with st.spinner("Processing files..."):
                    saved_files = save_uploaded_files(uploaded_files)
                    st.session_state.uploaded_files.extend(saved_files)
                    
                    # Reinitialize system
                    rag_system, error = initialize_rag_system()
                    if rag_system:
                        st.session_state.rag_system = rag_system
                        st.session_state.system_ready = True
                        st.success("✅ Files processed successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ {error}")
        
        # System status
        if st.session_state.system_ready:
            st.markdown("### 📊 System Status")
            collection_info = st.session_state.rag_system.analyze_document_collection()
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{collection_info['total_documents']}</h3>
                    <p>Documents</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{collection_info['total_chunks']}</h3>
                    <p>Chunks</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Document list
            st.markdown("### 📚 Loaded Documents")
            for doc in collection_info['documents']:
                with st.expander(f"📄 {doc['file_name']}", expanded=False):
                    st.write(f"**Type:** {doc.get('file_type', 'Unknown').upper()}")
                    st.write(f"**Pages:** {doc['pages']}")
                    st.write(f"**Topics:** {', '.join(doc['key_topics'][:3])}")
        
        # Settings
        st.markdown("### ⚙️ Settings")
        analysis_depth = st.selectbox(
            "Analysis Depth",
            ["quick", "standard", "deep"],
            index=1,
            help="Choose analysis thoroughness"
        )
        
        # Clear chat
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
        
        # Rebuild index button
        if st.button("🔄 Rebuild Index"):
            with st.spinner("Rebuilding document index..."):
                try:
                    st.session_state.rag_system.vectorstore.rebuild_vectorstore()
                    st.success("✅ Index rebuilt successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error rebuilding index: {e}")
    
    # Main chat area
    if not st.session_state.system_ready:
        st.markdown("""
        <div class="upload-area">
            <h3>👋 Welcome to Smart Document Chat!</h3>
            <p>Upload your documents using the sidebar to get started</p>
            <p><strong>Supported formats:</strong> PDF, TXT, CSV, Excel, Word, JSON</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sample questions
        st.markdown("### 💡 What you can ask once documents are loaded:")
        sample_questions = [
            "📋 Summarize the main points from all documents",
            "🔍 What are the key findings and conclusions?",
            "⚙️ Explain the technical implementation details",
            "📊 What data or statistics are presented?",
            "🎯 What are the practical applications mentioned?",
            "🔗 How do the different documents relate to each other?"
        ]
        
        for question in sample_questions:
            st.markdown(f"• {question}")
        
        return
    
    # Chat interface
    st.markdown("### 💬 Chat with your documents")
    
    # Chat container
    chat_container = st.container()
    with chat_container:
        # Display messages
        for message in st.session_state.messages:
            display_message(
                message["role"],
                message["content"],
                message.get("timestamp", ""),
                message.get("search_results")
            )
        
        # Show typing indicator if processing
        if st.session_state.processing:
            display_typing_indicator()
    
    # Input area
    st.markdown("---")
    
    # Quick action buttons
    st.markdown("**Quick Actions:**")
    col1, col2, col3, col4 = st.columns(4)
    
    quick_actions = [
        ("📋 Summary", "Provide a comprehensive summary of all documents"),
        ("🔑 Key Topics", "What are the main topics and themes?"),
        ("⚙️ Technical", "Explain technical details and implementation"),
        ("📊 Data", "What data, statistics, or metrics are mentioned?")
    ]
    
    for i, (button_text, question) in enumerate(quick_actions):
        with [col1, col2, col3, col4][i]:
            if st.button(button_text, key=f"quick_{i}"):
                # Add user message
                timestamp = datetime.now().strftime("%H:%M")
                st.session_state.messages.append({
                    "role": "user",
                    "content": question,
                    "timestamp": timestamp
                })
                
                # Process question
                st.session_state.processing = True
                st.rerun()
    
    # Text input
    user_input = st.text_input(
        "Type your message:",
        placeholder="Ask anything about your documents...",
        key="chat_input"
    )
    
    # Send button
    col1, col2 = st.columns([5, 1])
    with col2:
        send_clicked = st.button("Send 🚀", key="send_btn")
    
    # Process input
    if (send_clicked and user_input) or st.session_state.processing:
        if user_input and not st.session_state.processing:
            # Add user message
            timestamp = datetime.now().strftime("%H:%M")
            st.session_state.messages.append({
                "role": "user",
                "content": user_input,
                "timestamp": timestamp
            })
            st.session_state.processing = True
            st.rerun()
        
        elif st.session_state.processing:
            # Get the last user message
            last_message = st.session_state.messages[-1]
            if last_message["role"] == "user":
                question = last_message["content"]
                
                # Get AI response
                try:
                    result = st.session_state.rag_system.comprehensive_search(
                        question, 
                        analysis_depth=analysis_depth
                    )
                    response = result["response"]
                    search_results = result["search_results"]
                    
                    # Add assistant message
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response,
                        "timestamp": datetime.now().strftime("%H:%M"),
                        "search_results": search_results
                    })
                    
                except Exception as e:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"Sorry, I encountered an error: {str(e)}",
                        "timestamp": datetime.now().strftime("%H:%M")
                    })
                
                st.session_state.processing = False
                st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🤖 Smart Document Chat | Powered by Enhanced RAG System</p>
    <p><small>Upload documents and start chatting with your AI assistant!</small></p>
</div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()