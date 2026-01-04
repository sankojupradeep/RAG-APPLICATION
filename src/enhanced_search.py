"""
Enhanced RAG search with comprehensive document analysis and intelligent question answering
Supports all document types: PDF, TXT, CSV, Excel, Word, JSON
"""
import os
from dotenv import load_dotenv
from src.enhanced_vectorstore import EnhancedVectorStore
from src.data_loader import load_all_documents  # Use original loader for all types
from langchain_groq import ChatGroq
from typing import List, Dict, Any
import glob
from pathlib import Path

load_dotenv()

class EnhancedRAGSearch:
    def __init__(self, 
                 persist_dir: str = "enhanced_faiss_store", 
                 embedding_model: str = "all-MiniLM-L6-v2", 
                 llm_model: str = "llama-3.1-8b-instant",  # Updated to current model
                 data_dir: str = "data"):
        
        self.vectorstore = EnhancedVectorStore(persist_dir, embedding_model)
        self.data_dir = data_dir
        
        # Initialize LLM
        groq_api_key = os.getenv("GROQ_API_KEY", "")
        if not groq_api_key:
            print("[WARNING] GROQ_API_KEY not found in environment variables")
        
        self.llm = ChatGroq(groq_api_key=groq_api_key, model_name=llm_model)
        print(f"[INFO] Enhanced RAG initialized with LLM: {llm_model}")
        
        # Load or build vector store
        self._initialize_vectorstore()

    def _initialize_vectorstore(self):
        """Initialize vector store by loading existing or building new"""
        # Check if enhanced vector store exists
        doc_index_path = os.path.join(self.vectorstore.persist_dir, "document.index")
        chunk_index_path = os.path.join(self.vectorstore.persist_dir, "chunk.index")
        
        # Check for new documents in data directory
        documents = load_all_documents(self.data_dir)
        current_files = set([doc.metadata.get("source", "") for doc in documents if doc.metadata.get("source")])
        
        # Check if we need to rebuild
        need_rebuild = False
        
        if os.path.exists(doc_index_path) and os.path.exists(chunk_index_path):
            print("[INFO] Loading existing enhanced vector store...")
            self.vectorstore.load()
            
            # Check if all current files are indexed
            indexed_files = set([doc["file_path"] for doc in self.vectorstore.document_metadata])
            
            if current_files != indexed_files:
                print(f"[INFO] Document changes detected:")
                new_files = current_files - indexed_files
                removed_files = indexed_files - current_files
                
                if new_files:
                    print(f"  New files: {[os.path.basename(f) for f in new_files]}")
                if removed_files:
                    print(f"  Removed files: {[os.path.basename(f) for f in removed_files]}")
                
                need_rebuild = True
        else:
            need_rebuild = True
        
        if need_rebuild:
            print("[INFO] Rebuilding vector store with current documents...")
            self.vectorstore.rebuild_vectorstore()

    def _build_vectorstore(self):
        """Build vector store from all supported document types in data directory"""
        # Use the original data loader to get all supported document types
        documents = load_all_documents(self.data_dir)
        
        if not documents:
            print(f"[WARNING] No supported documents found in {self.data_dir}")
            print("Supported formats: PDF, TXT, CSV, Excel (.xlsx), Word (.docx), JSON")
            return
        
        # Extract unique file paths from loaded documents
        file_paths = list(set([doc.metadata.get("source", "") for doc in documents if doc.metadata.get("source")]))
        
        print(f"[INFO] Found {len(file_paths)} document files with {len(documents)} total pages/sections")
        for file_path in file_paths:
            file_type = Path(file_path).suffix.lower()
            print(f"  - {Path(file_path).name} ({file_type})")
        
        # Build enhanced vector store from all document types
        self.vectorstore.build_from_documents(file_paths)

    def comprehensive_search(self, query: str, analysis_depth: str = "deep") -> Dict[str, Any]:
        """
        Perform comprehensive search and analysis
        
        Args:
            query: User question
            analysis_depth: "quick", "standard", or "deep"
        """
        print(f"[INFO] Performing {analysis_depth} analysis for: '{query}'")
        
        # Configure search parameters based on depth
        if analysis_depth == "quick":
            doc_top_k, chunk_top_k = 2, 5
        elif analysis_depth == "standard":
            doc_top_k, chunk_top_k = 3, 8
        else:  # deep
            doc_top_k, chunk_top_k = 5, 15
        
        # Perform hybrid search
        search_results = self.vectorstore.hybrid_search(query, doc_top_k, chunk_top_k)
        
        # Get comprehensive context
        context = self.vectorstore.get_comprehensive_context(query, max_context_length=6000)
        
        # Generate intelligent response
        response = self._generate_intelligent_response(query, context, search_results)
        
        return {
            "query": query,
            "response": response,
            "search_results": search_results,
            "context_used": context,
            "analysis_depth": analysis_depth
        }

    def _generate_intelligent_response(self, query: str, context: str, search_results: Dict) -> str:
        """Generate intelligent response using LLM with comprehensive context"""
        
        # Create enhanced prompt with analysis instructions
        prompt = f"""You are an expert document analyst. Answer the user's question using the provided comprehensive context from multiple documents.

CONTEXT INFORMATION:
{context}

USER QUESTION: {query}

INSTRUCTIONS:
1. Provide a comprehensive answer based on ALL relevant information from the context
2. If the question requires analysis across multiple documents, synthesize information from all sources
3. Include specific details, examples, and explanations when available
4. If information is incomplete, clearly state what aspects need more information
5. Cite specific documents or pages when referencing information
6. Structure your response clearly with main points and supporting details

ANSWER:"""

        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            print(f"[ERROR] LLM generation failed: {e}")
            return self._fallback_response(query, search_results)

    def _fallback_response(self, query: str, search_results: Dict) -> str:
        """Fallback response when LLM fails"""
        response_parts = [f"Based on the analysis of the documents, here's what I found regarding: '{query}'\n"]
        
        # Add document summaries
        if search_results["relevant_documents"]:
            response_parts.append("RELEVANT DOCUMENTS:")
            for i, doc in enumerate(search_results["relevant_documents"][:3], 1):
                doc_name = os.path.basename(doc["document"]["file_path"])
                summary = doc["document"]["document_summary"][:300]
                response_parts.append(f"{i}. {doc_name}: {summary}...")
        
        # Add relevant content
        if search_results["relevant_chunks"]:
            response_parts.append("\nRELEVANT CONTENT:")
            for i, chunk in enumerate(search_results["relevant_chunks"][:5], 1):
                content = chunk["chunk"]["chunk_text"][:200]
                page = chunk["chunk"]["page_number"]
                response_parts.append(f"{i}. [Page {page}] {content}...")
        
        return "\n\n".join(response_parts)

    def analyze_document_collection(self) -> Dict[str, Any]:
        """Analyze the entire document collection of all supported types"""
        if not self.vectorstore.document_metadata:
            return {"error": "No documents loaded"}
        
        # Group documents by type
        type_counts = {}
        for doc_meta in self.vectorstore.document_metadata:
            file_type = doc_meta.get("file_type", "unknown")
            type_counts[file_type] = type_counts.get(file_type, 0) + 1
        
        analysis = {
            "total_documents": len(self.vectorstore.document_metadata),
            "total_chunks": len(self.vectorstore.chunk_metadata),
            "document_types": type_counts,
            "documents": []
        }
        
        for doc_meta in self.vectorstore.document_metadata:
            doc_analysis = {
                "file_name": os.path.basename(doc_meta["file_path"]),
                "file_type": doc_meta.get("file_type", "unknown"),
                "pages": doc_meta["metadata"]["total_pages"],
                "key_topics": doc_meta["key_topics"][:10],
                "summary": doc_meta["document_summary"][:200] + "...",
                "structure_info": doc_meta["structure"].get("file_type_specific", {})
            }
            analysis["documents"].append(doc_analysis)
        
        return analysis

    def ask_question(self, question: str, depth: str = "standard") -> str:
        """Simple interface for asking questions"""
        result = self.comprehensive_search(question, depth)
        return result["response"]

    def get_document_summary(self, file_name: str) -> str:
        """Get summary of a specific document"""
        for doc_meta in self.vectorstore.document_metadata:
            if file_name in doc_meta["file_path"]:
                return doc_meta["document_summary"]
        return f"Document '{file_name}' not found in the collection."

    def list_available_documents(self) -> List[str]:
        """List all available documents"""
        return [os.path.basename(doc["file_path"]) for doc in self.vectorstore.document_metadata]

# Example usage and testing
if __name__ == "__main__":
    # Initialize enhanced RAG
    enhanced_rag = EnhancedRAGSearch(data_dir="data")
    
    # Example questions
    test_questions = [
        "What are the main topics covered in the documents?",
        "Explain the key concepts and methodologies discussed.",
        "What are the practical applications mentioned?",
        "Summarize the conclusions and recommendations."
    ]
    
    print("=== ENHANCED RAG DEMO ===")
    print(f"Available documents: {enhanced_rag.list_available_documents()}")
    print(f"Collection analysis: {enhanced_rag.analyze_document_collection()}")
    
    for question in test_questions:
        print(f"\n--- Question: {question} ---")
        answer = enhanced_rag.ask_question(question, depth="standard")
        print(f"Answer: {answer[:500]}...")