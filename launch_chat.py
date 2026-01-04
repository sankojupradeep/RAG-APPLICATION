"""
Launcher script for the Smart Document Chat interface
"""
import subprocess
import sys
import os
from pathlib import Path

def check_streamlit():
    """Check if streamlit is installed"""
    try:
        import streamlit
        return True
    except ImportError:
        return False

def install_streamlit():
    """Install streamlit if not present"""
    print("Installing Streamlit...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit>=1.28.0"])
    print("✅ Streamlit installed successfully!")

def launch_basic_chat():
    """Launch the basic chat interface"""
    print("🚀 Launching Smart Document Assistant...")
    print("📱 Opening in your default browser...")
    print("🔗 URL: http://localhost:8501")
    print("\n💡 Tips:")
    print("   - Make sure your documents are in the 'data' directory")
    print("   - Use Ctrl+C to stop the server")
    print("   - Refresh the page if you encounter any issues")
    print("\n" + "="*50)
    
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
        "--server.port", "8501",
        "--server.address", "localhost",
        "--browser.gatherUsageStats", "false"
    ])

def launch_advanced_chat():
    """Launch the advanced chat interface with file upload"""
    print("🚀 Launching Advanced Smart Document Chat...")
    print("📱 Opening in your default browser...")
    print("🔗 URL: http://localhost:8502")
    print("\n💡 Features:")
    print("   - Drag & drop file upload")
    print("   - Enhanced chat interface")
    print("   - Real-time document processing")
    print("   - Export chat history")
    print("\n💡 Tips:")
    print("   - Upload documents directly through the web interface")
    print("   - Use Ctrl+C to stop the server")
    print("   - Supported formats: PDF, TXT, CSV, Excel, Word, JSON")
    print("\n" + "="*50)
    
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", "advanced_chat_app.py",
        "--server.port", "8502",
        "--server.address", "localhost",
        "--browser.gatherUsageStats", "false"
    ])

def main():
    print("=" * 60)
    print("🤖 Smart Document Chat Launcher")
    print("=" * 60)
    
    # Check if streamlit is installed
    if not check_streamlit():
        print("❌ Streamlit not found. Installing...")
        try:
            install_streamlit()
        except Exception as e:
            print(f"❌ Failed to install Streamlit: {e}")
            print("Please install manually: pip install streamlit")
            return
    
    # Check if data directory exists
    data_dir = Path("data")
    if not data_dir.exists():
        print("📁 Creating data directory...")
        data_dir.mkdir(exist_ok=True)
    
    # Check for documents
    doc_files = list(data_dir.glob("*.*"))
    supported_extensions = {'.pdf', '.txt', '.csv', '.xlsx', '.docx', '.json'}
    valid_docs = [f for f in doc_files if f.suffix.lower() in supported_extensions]
    
    if valid_docs:
        print(f"📚 Found {len(valid_docs)} documents in data directory:")
        for doc in valid_docs[:5]:  # Show first 5
            print(f"   - {doc.name}")
        if len(valid_docs) > 5:
            print(f"   ... and {len(valid_docs) - 5} more")
    else:
        print("📁 No documents found in data directory")
        print("   You can either:")
        print("   1. Add documents to the 'data' directory manually")
        print("   2. Use the advanced interface to upload files")
    
    print("\n🎯 Choose your interface:")
    print("1. 📱 Basic Chat Interface (documents from 'data' directory)")
    print("2. 🚀 Advanced Chat Interface (with file upload)")
    print("3. ❌ Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == "1":
                if not valid_docs:
                    print("⚠️  No documents found in 'data' directory.")
                    print("   Please add documents first or use option 2.")
                    continue
                launch_basic_chat()
                break
            elif choice == "2":
                launch_advanced_chat()
                break
            elif choice == "3":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()