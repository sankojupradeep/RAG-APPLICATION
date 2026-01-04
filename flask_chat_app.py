"""
Flask-based ChatGPT-like interface for Enhanced RAG System
Alternative web interface using Flask
"""
from flask import Flask, render_template, request, jsonify, session
import os
import sys
import json
from datetime import datetime
import uuid

# Add src to path
sys.path.append('src')

from src.enhanced_search import EnhancedRAGSearch

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Global RAG system instance
rag_system = None
system_ready = False

def initialize_rag():
    """Initialize the RAG system"""
    global rag_system, system_ready
    try:
        rag_system = EnhancedRAGSearch(data_dir="data")
        collection_info = rag_system.analyze_document_collection()
        
        if "error" not in collection_info:
            system_ready = True
            return True, collection_info
        else:
            return False, "No documents found in data directory"
    except Exception as e:
        return False, str(e)

@app.route('/')
def index():
    """Main chat interface"""
    return render_template('chat.html')

@app.route('/api/init', methods=['POST'])
def init_system():
    """Initialize the RAG system"""
    success, info = initialize_rag()
    return jsonify({
        'success': success,
        'message': info if isinstance(info, str) else 'System initialized successfully',
        'collection_info': info if isinstance(info, dict) else None
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    if not system_ready:
        return jsonify({
            'success': False,
            'message': 'System not initialized. Please initialize first.'
        })
    
    data = request.json
    message = data.get('message', '')
    analysis_depth = data.get('analysis_depth', 'standard')
    
    if not message:
        return jsonify({
            'success': False,
            'message': 'No message provided'
        })
    
    try:
        # Get response from RAG system
        result = rag_system.comprehensive_search(message, analysis_depth=analysis_depth)
        
        # Store conversation in session
        if 'conversation' not in session:
            session['conversation'] = []
        
        conversation_entry = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'user_message': message,
            'assistant_response': result["response"],
            'search_results': result["search_results"]
        }
        
        session['conversation'].append(conversation_entry)
        
        return jsonify({
            'success': True,
            'response': result["response"],
            'search_results': result["search_results"],
            'conversation_id': conversation_entry['id']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error processing message: {str(e)}'
        })

@app.route('/api/status')
def status():
    """Get system status"""
    if not system_ready:
        return jsonify({
            'ready': False,
            'message': 'System not initialized'
        })
    
    try:
        collection_info = rag_system.analyze_document_collection()
        return jsonify({
            'ready': True,
            'collection_info': collection_info
        })
    except Exception as e:
        return jsonify({
            'ready': False,
            'message': str(e)
        })

@app.route('/api/conversation')
def get_conversation():
    """Get conversation history"""
    return jsonify({
        'conversation': session.get('conversation', [])
    })

@app.route('/api/clear', methods=['POST'])
def clear_conversation():
    """Clear conversation history"""
    session['conversation'] = []
    return jsonify({'success': True})

# Create templates directory and HTML template
def create_templates():
    """Create the HTML template"""
    templates_dir = "templates"
    os.makedirs(templates_dir, exist_ok=True)
    
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Document Chat</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 1rem 2rem;
            color: white;
            text-align: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .container {
            flex: 1;
            display: flex;
            max-width: 1200px;
            margin: 0 auto;
            width: 100%;
            gap: 1rem;
            padding: 1rem;
        }
        
        .sidebar {
            width: 300px;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 1.5rem;
            height: fit-content;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .chat-container {
            flex: 1;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            display: flex;
            flex-direction: column;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .chat-messages {
            flex: 1;
            padding: 1.5rem;
            overflow-y: auto;
            max-height: 600px;
        }
        
        .message {
            margin-bottom: 1rem;
            padding: 1rem 1.5rem;
            border-radius: 20px;
            max-width: 80%;
            word-wrap: break-word;
        }
        
        .user-message {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin-left: auto;
            border-radius: 20px 20px 5px 20px;
        }
        
        .assistant-message {
            background: #f8f9fa;
            color: #333;
            border: 1px solid #e9ecef;
            border-radius: 20px 20px 20px 5px;
        }
        
        .chat-input-container {
            padding: 1.5rem;
            border-top: 1px solid #e9ecef;
            background: white;
            border-radius: 0 0 15px 15px;
        }
        
        .chat-input {
            display: flex;
            gap: 1rem;
            align-items: center;
        }
        
        .chat-input input {
            flex: 1;
            padding: 1rem 1.5rem;
            border: 2px solid #e9ecef;
            border-radius: 25px;
            font-size: 1rem;
            outline: none;
            transition: border-color 0.3s;
        }
        
        .chat-input input:focus {
            border-color: #667eea;
        }
        
        .send-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
            transition: transform 0.2s;
        }
        
        .send-btn:hover {
            transform: translateY(-2px);
        }
        
        .send-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .init-btn {
            background: #28a745;
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            cursor: pointer;
            width: 100%;
            margin-bottom: 1rem;
            font-weight: 600;
        }
        
        .clear-btn {
            background: #dc3545;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            cursor: pointer;
            width: 100%;
            margin-top: 1rem;
        }
        
        .status {
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            text-align: center;
        }
        
        .status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .status.info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        
        .quick-actions {
            margin-top: 1rem;
        }
        
        .quick-action-btn {
            background: #f8f9fa;
            border: 2px solid #667eea;
            color: #667eea;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            cursor: pointer;
            margin: 0.25rem;
            font-size: 0.9rem;
            transition: all 0.3s;
        }
        
        .quick-action-btn:hover {
            background: #667eea;
            color: white;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 1rem;
            color: #666;
        }
        
        .typing-indicator {
            display: none;
            padding: 1rem 1.5rem;
            color: #666;
            font-style: italic;
        }
        
        @media (max-width: 768px) {
            .container {
                flex-direction: column;
            }
            
            .sidebar {
                width: 100%;
                order: 2;
            }
            
            .chat-container {
                order: 1;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 Smart Document Chat</h1>
        <p>AI-powered document analysis and Q&A</p>
    </div>
    
    <div class="container">
        <div class="sidebar">
            <h3>📊 System Control</h3>
            <button class="init-btn" onclick="initializeSystem()">🚀 Initialize System</button>
            
            <div id="status" class="status info">
                System not initialized
            </div>
            
            <div id="collection-info" style="display: none;">
                <h4>📚 Document Collection</h4>
                <div id="doc-stats"></div>
            </div>
            
            <h4>⚙️ Settings</h4>
            <label for="analysis-depth">Analysis Depth:</label>
            <select id="analysis-depth" style="width: 100%; padding: 0.5rem; margin: 0.5rem 0; border-radius: 5px; border: 1px solid #ddd;">
                <option value="quick">Quick</option>
                <option value="standard" selected>Standard</option>
                <option value="deep">Deep</option>
            </select>
            
            <button class="clear-btn" onclick="clearChat()">🗑️ Clear Chat</button>
            
            <div class="quick-actions">
                <h4>🚀 Quick Actions</h4>
                <button class="quick-action-btn" onclick="askQuestion('Summarize all documents')">📋 Summary</button>
                <button class="quick-action-btn" onclick="askQuestion('What are the main topics?')">🔑 Topics</button>
                <button class="quick-action-btn" onclick="askQuestion('Explain technical details')">⚙️ Technical</button>
                <button class="quick-action-btn" onclick="askQuestion('What data is presented?')">📊 Data</button>
            </div>
        </div>
        
        <div class="chat-container">
            <div class="chat-messages" id="chat-messages">
                <div class="message assistant-message">
                    <strong>🤖 Assistant</strong><br><br>
                    Welcome! I'm your Smart Document Assistant. Please initialize the system using the sidebar to start chatting about your documents.
                </div>
            </div>
            
            <div class="loading" id="loading">
                <div>🤖 Assistant is thinking...</div>
            </div>
            
            <div class="chat-input-container">
                <div class="chat-input">
                    <input type="text" id="message-input" placeholder="Ask anything about your documents..." disabled>
                    <button class="send-btn" id="send-btn" onclick="sendMessage()" disabled>Send 🚀</button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let systemReady = false;
        
        function initializeSystem() {
            const statusDiv = document.getElementById('status');
            statusDiv.className = 'status info';
            statusDiv.textContent = 'Initializing system...';
            
            fetch('/api/init', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    systemReady = true;
                    statusDiv.className = 'status success';
                    statusDiv.textContent = 'System ready!';
                    
                    // Enable input
                    document.getElementById('message-input').disabled = false;
                    document.getElementById('send-btn').disabled = false;
                    
                    // Show collection info
                    if (data.collection_info) {
                        const collectionDiv = document.getElementById('collection-info');
                        const statsDiv = document.getElementById('doc-stats');
                        
                        statsDiv.innerHTML = `
                            <p><strong>Documents:</strong> ${data.collection_info.total_documents}</p>
                            <p><strong>Chunks:</strong> ${data.collection_info.total_chunks}</p>
                        `;
                        
                        collectionDiv.style.display = 'block';
                    }
                } else {
                    statusDiv.className = 'status error';
                    statusDiv.textContent = data.message;
                }
            })
            .catch(error => {
                statusDiv.className = 'status error';
                statusDiv.textContent = 'Error initializing system';
                console.error('Error:', error);
            });
        }
        
        function sendMessage() {
            const input = document.getElementById('message-input');
            const message = input.value.trim();
            
            if (!message || !systemReady) return;
            
            // Add user message to chat
            addMessage('user', message);
            input.value = '';
            
            // Show loading
            document.getElementById('loading').style.display = 'block';
            document.getElementById('send-btn').disabled = true;
            
            // Send to API
            const analysisDepth = document.getElementById('analysis-depth').value;
            
            fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    analysis_depth: analysisDepth
                })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('send-btn').disabled = false;
                
                if (data.success) {
                    addMessage('assistant', data.response);
                } else {
                    addMessage('assistant', 'Sorry, I encountered an error: ' + data.message);
                }
            })
            .catch(error => {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('send-btn').disabled = false;
                addMessage('assistant', 'Sorry, I encountered an error processing your request.');
                console.error('Error:', error);
            });
        }
        
        function addMessage(role, content) {
            const messagesDiv = document.getElementById('chat-messages');
            const messageDiv = document.createElement('div');
            
            const timestamp = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
            
            if (role === 'user') {
                messageDiv.className = 'message user-message';
                messageDiv.innerHTML = `<div>${content}</div><small style="opacity: 0.8; margin-top: 0.5rem; display: block;">You • ${timestamp}</small>`;
            } else {
                messageDiv.className = 'message assistant-message';
                messageDiv.innerHTML = `<strong>🤖 Assistant</strong><br><br>${content}<br><small style="opacity: 0.6; margin-top: 0.5rem; display: block;">${timestamp}</small>`;
            }
            
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        function askQuestion(question) {
            if (!systemReady) return;
            
            document.getElementById('message-input').value = question;
            sendMessage();
        }
        
        function clearChat() {
            fetch('/api/clear', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(() => {
                const messagesDiv = document.getElementById('chat-messages');
                messagesDiv.innerHTML = `
                    <div class="message assistant-message">
                        <strong>🤖 Assistant</strong><br><br>
                        Chat cleared! How can I help you with your documents?
                    </div>
                `;
            });
        }
        
        // Enter key to send message
        document.getElementById('message-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>'''
    
    with open(os.path.join(templates_dir, 'chat.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)

if __name__ == '__main__':
    # Create templates
    create_templates()
    
    print("🚀 Starting Flask Chat Server...")
    print("🔗 Open your browser and go to: http://localhost:5000")
    print("💡 Make sure your documents are in the 'data' directory")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)