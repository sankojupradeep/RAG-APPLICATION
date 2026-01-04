"""
ChatGPT-like Web Interface for Enhanced RAG System
A Streamlit-based chat interface for document Q&A
"""
import streamlit as st
import os
import sys
import time
from pathlib import Path
import json
from datetime import datetime

# Add src to path
sys.path.append('src')

from src.enhanced_search import EnhancedRAGSearch

# Page configuration
st.set_page_config(
    page_title="Smart Document Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for ChatGPT-like styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    .user-message {
        background-color: #f0f2f6;
        border-left-color: #667eea;
    }
    
    .assistant-message {
        background-color: #e8f4fd;
        border-left-color: #1f77b4;
    }
    
    .document-info {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        margin: 1rem 0;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    
    .stTextInput > div > div > input {
        border-radius: 20px;
        border: 2px solid #667eea;
        padding: 0.5rem 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "rag_system" not in st.session_state:
    st.session_state.rag_system = None
if "documents_loaded" not in st.session_state:
    st.session_state.documents_loaded = False
if "system_ready" not in st.session_state:
    st.session_state.system_ready = False

def initialize_rag_system():
    """Initialize the RAG system"""
    try:
        with st.spinner("🔄 Initializing Smart Document Assistant..."):
            rag_system = EnhancedRAGSearch(data_dir="data")
            
            # Check if documents are available
            collection_info = rag_system.analyze_document_collection()
            if "error" in collection_info:
                return None, "No documents found. Please add documents to the 'data' directory."
            
            return rag_system, None
    except Exception as e:
        return None, f"Error initializing system: {str(e)}"

def display_document_info(rag_system):
    """Display information about loaded documents"""
    collection_info = rag_system.analyze_document_collection()
    
    if "error" not in collection_info:
        st.sidebar.markdown("### 📚 Document Collection")
        
        # Metrics
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.metric("Documents", collection_info['total_documents'])
        with col2:
            st.metric("Chunks", collection_info['total_chunks'])
        
        # Document types
        if 'document_types' in collection_info:
            st.sidebar.markdown("**Document Types:**")
            for doc_type, count in collection_info['document_types'].items():
                st.sidebar.write(f"• {doc_type.upper()}: {count} files")
        
        # Document details
        st.sidebar.markdown("**Documents:**")
        for doc in collection_info['documents'][:5]:  # Show first 5
            with st.sidebar.expander(f"📄 {doc['file_name']}", expanded=False):
                st.write(f"**Type:** {doc.get('file_type', 'Unknown').upper()}")
                st.write(f"**Pages:** {doc['pages']}")
                st.write(f"**Topics:** {', '.join(doc['key_topics'][:3])}")
                st.write(f"**Summary:** {doc['summary'][:100]}...")

def display_chat_message(role, content, timestamp=None):
    """Display a chat message with proper styling"""
    if timestamp is None:
        timestamp = datetime.now().strftime("%H:%M")
    
    if role == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>🧑 You</strong> <small>({timestamp})</small><br>
            {content}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message assistant-message">
            <strong>🤖 Assistant</strong> <small>({timestamp})</small><br>
            {content}
        </div>
        """, unsafe_allow_html=True)

def get_response(rag_system, question, analysis_depth="standard"):
    """Get response from RAG system"""
    try:
        with st.spinner("🔍 Analyzing your question..."):
            result = rag_system.comprehensive_search(question, analysis_depth=analysis_depth)
            return result["response"], result["search_results"]
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}", None

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Smart Document Assistant</h1>
        <p>Ask questions about your documents - Get intelligent answers powered by AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("⚙️ Settings")
    
    # Initialize system if not done
    if not st.session_state.system_ready:
        if st.sidebar.button("🚀 Initialize System"):
            rag_system, error = initialize_rag_system()
            if rag_system:
                st.session_state.rag_system = rag_system
                st.session_state.system_ready = True
                st.session_state.documents_loaded = True
                st.success("✅ System initialized successfully!")
                st.rerun()
            else:
                st.error(f"❌ {error}")
    
    # System controls
    if st.session_state.system_ready:
        # Analysis depth setting
        analysis_depth = st.sidebar.selectbox(
            "🔍 Analysis Depth",
            ["quick", "standard", "deep"],
            index=1,
            help="Choose how thoroughly to analyze your question"
        )
        
        # Display document info
        display_document_info(st.session_state.rag_system)
        
        # Clear chat button
        if st.sidebar.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
        
        # Export chat button
        if st.session_state.messages and st.sidebar.button("💾 Export Chat"):
            chat_data = {
                "timestamp": datetime.now().isoformat(),
                "messages": st.session_state.messages
            }
            st.sidebar.download_button(
                "📥 Download Chat History",
                data=json.dumps(chat_data, indent=2),
                file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    # Main chat interface
    if not st.session_state.system_ready:
        st.info("👈 Please initialize the system using the sidebar to start chatting!")
        
        # Show sample questions
        st.markdown("### 💡 Sample Questions You Can Ask:")
        sample_questions = [
            "What are the main topics covered in the documents?",
            "Summarize the key findings and conclusions",
            "What methodologies are discussed?",
            "Are there any practical applications mentioned?",
            "What are the technical requirements?",
            "Explain the system architecture"
        ]
        
        for i, question in enumerate(sample_questions, 1):
            st.markdown(f"{i}. {question}")
        
        return
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            display_chat_message(
                message["role"], 
                message["content"], 
                message.get("timestamp")
            )
    
    # Chat input
    st.markdown("---")
    
    # Create columns for input and button
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_input = st.text_input(
            "Ask a question about your documents:",
            placeholder="Type your question here...",
            key="user_input",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.button("Send 📤", key="send_button")
    
    # Handle user input
    if send_button and user_input:
        # Add user message
        timestamp = datetime.now().strftime("%H:%M")
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": timestamp
        })
        
        # Get AI response
        response, search_results = get_response(
            st.session_state.rag_system, 
            user_input, 
            analysis_depth
        )
        
        # Add assistant message
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().strftime("%H:%M"),
            "search_results": search_results
        })
        
        # Clear input and rerun
        st.rerun()
    
    # Quick action buttons
    if st.session_state.system_ready:
        st.markdown("### 🚀 Quick Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📋 Document Summary"):
                summary_question = "Provide a comprehensive summary of all the documents"
                st.session_state.messages.append({
                    "role": "user",
                    "content": summary_question,
                    "timestamp": datetime.now().strftime("%H:%M")
                })
                response, search_results = get_response(
                    st.session_state.rag_system, 
                    summary_question, 
                    "deep"
                )
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now().strftime("%H:%M"),
                    "search_results": search_results
                })
                st.rerun()
        
        with col2:
            if st.button("🔑 Key Topics"):
                topics_question = "What are the main topics and themes discussed?"
                st.session_state.messages.append({
                    "role": "user",
                    "content": topics_question,
                    "timestamp": datetime.now().strftime("%H:%M")
                })
                response, search_results = get_response(
                    st.session_state.rag_system, 
                    topics_question, 
                    "standard"
                )
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now().strftime("%H:%M"),
                    "search_results": search_results
                })
                st.rerun()
        
        with col3:
            if st.button("⚙️ Technical Details"):
                tech_question = "Explain the technical aspects and implementation details"
                st.session_state.messages.append({
                    "role": "user",
                    "content": tech_question,
                    "timestamp": datetime.now().strftime("%H:%M")
                })
                response, search_results = get_response(
                    st.session_state.rag_system, 
                    tech_question, 
                    "deep"
                )
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now().strftime("%H:%M"),
                    "search_results": search_results
                })
                st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🤖 Smart Document Assistant | Powered by Enhanced RAG System</p>
    <p><small>Upload your documents to the 'data' directory and start asking questions!</small></p>
</div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()