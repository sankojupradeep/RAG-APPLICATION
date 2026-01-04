"""
Enhanced vector store with multi-level indexing and comprehensive document analysis
"""
import os
import faiss
import numpy as np
import pickle
from typing import List, Dict, Any, Tuple
from sentence_transformers import SentenceTransformer
from src.document_analyzer import DocumentAnalyzer
import json

class EnhancedVectorStore:
    def __init__(self, persist_dir: str = "enhanced_faiss_store", embedding_model: str = "all-MiniLM-L6-v2"):
        self.persist_dir = persist_dir
        os.makedirs(self.persist_dir, exist_ok=True)
        
        # Multiple indices for different levels
        self.document_index = None  # Document-level embeddings
        self.chunk_index = None     # Chunk-level embeddings
        
        # Metadata storage
        self.document_metadata = []
        self.chunk_metadata = []
        
        # Models
        self.embedding_model = embedding_model
        self.model = SentenceTransformer(embedding_model)
        self.analyzer = DocumentAnalyzer(embedding_model)
        
        print(f"[INFO] Enhanced vector store initialized with model: {embedding_model}")

    def build_from_documents(self, document_files: List[str]):
        """Build enhanced vector store from all supported document types with comprehensive analysis"""
        print(f"[INFO] Building enhanced vector store from {len(document_files)} document files...")
        
        all_doc_embeddings = []
        all_chunk_embeddings = []
        
        for doc_file in document_files:
            print(f"[INFO] Processing: {doc_file}")
            
            # Comprehensive document analysis for all file types
            analysis = self.analyzer.analyze_document(doc_file)
            
            # Skip if analysis failed
            if not analysis["embeddings"]["document"].size:
                print(f"[WARNING] Skipping {doc_file} - analysis failed")
                continue
            
            # Store document-level data
            doc_embedding = analysis["embeddings"]["document"]
            all_doc_embeddings.append(doc_embedding)
            
            doc_metadata = {
                "file_path": analysis["file_path"],
                "file_type": analysis["file_type"],
                "document_summary": analysis["document_summary"],
                "key_topics": analysis["key_topics"],
                "structure": analysis["structure"],
                "metadata": analysis["metadata"],
                "full_text": analysis["full_text"]  # Store for context
            }
            self.document_metadata.append(doc_metadata)
            
            # Store chunk-level data
            chunk_embeddings = analysis["embeddings"]["chunks"]
            if chunk_embeddings.size > 0:
                all_chunk_embeddings.extend(chunk_embeddings)
                
                for i, chunk in enumerate(analysis["semantic_chunks"]):
                    chunk_meta = {
                        "document_index": len(self.document_metadata) - 1,  # Reference to document
                        "chunk_text": chunk["text"],
                        "page_number": chunk["page_number"],
                        "chunk_index": chunk["chunk_index"],
                        "source": chunk["source"],
                        "file_type": chunk["file_type"],
                        "context": chunk["context"]
                    }
                    self.chunk_metadata.append(chunk_meta)
        
        # Build FAISS indices
        if all_doc_embeddings:
            doc_embeddings_array = np.array(all_doc_embeddings).astype('float32')
            self._build_document_index(doc_embeddings_array)
        
        if all_chunk_embeddings:
            chunk_embeddings_array = np.array(all_chunk_embeddings).astype('float32')
            self._build_chunk_index(chunk_embeddings_array)
        
        # Save everything
        self.save()
        print(f"[INFO] Enhanced vector store built with {len(self.document_metadata)} documents and {len(self.chunk_metadata)} chunks")

    def build_from_pdf_files(self, pdf_files: List[str]):
        """Backward compatibility method - now supports all document types"""
        print("[INFO] build_from_pdf_files is deprecated. Use build_from_documents for all file types.")
        self.build_from_documents(pdf_files)

    def _build_document_index(self, embeddings: np.ndarray):
        """Build document-level FAISS index"""
        dim = embeddings.shape[1]
        self.document_index = faiss.IndexFlatL2(dim)
        self.document_index.add(embeddings)
        print(f"[INFO] Built document index with {embeddings.shape[0]} documents")

    def _build_chunk_index(self, embeddings: np.ndarray):
        """Build chunk-level FAISS index"""
        dim = embeddings.shape[1]
        self.chunk_index = faiss.IndexFlatL2(dim)
        self.chunk_index.add(embeddings)
        print(f"[INFO] Built chunk index with {embeddings.shape[0]} chunks")

    def search_documents(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search at document level for relevant documents"""
        if self.document_index is None:
            return []
        
        # Encode query
        query_embedding = self.model.encode([query]).astype('float32')
        
        # Search document index
        distances, indices = self.document_index.search(query_embedding, top_k)
        
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.document_metadata):
                result = {
                    "rank": i + 1,
                    "distance": float(distance),
                    "document": self.document_metadata[idx],
                    "relevance_score": 1.0 / (1.0 + distance)  # Convert distance to relevance
                }
                results.append(result)
        
        return results

    def search_chunks(self, query: str, top_k: int = 10, document_filter: List[int] = None) -> List[Dict[str, Any]]:
        """Search at chunk level, optionally filtered by document indices"""
        if self.chunk_index is None:
            return []
        
        # Encode query
        query_embedding = self.model.encode([query]).astype('float32')
        
        # Search chunk index
        distances, indices = self.chunk_index.search(query_embedding, top_k * 2)  # Get more for filtering
        
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.chunk_metadata):
                chunk_meta = self.chunk_metadata[idx]
                
                # Apply document filter if specified
                if document_filter and chunk_meta["document_index"] not in document_filter:
                    continue
                
                result = {
                    "rank": len(results) + 1,
                    "distance": float(distance),
                    "chunk": chunk_meta,
                    "document_info": self.document_metadata[chunk_meta["document_index"]],
                    "relevance_score": 1.0 / (1.0 + distance)
                }
                results.append(result)
                
                if len(results) >= top_k:
                    break
        
        return results

    def hybrid_search(self, query: str, doc_top_k: int = 3, chunk_top_k: int = 10) -> Dict[str, Any]:
        """Perform hybrid search: first find relevant documents, then relevant chunks"""
        print(f"[INFO] Performing hybrid search for: '{query}'")
        
        # Step 1: Find relevant documents
        relevant_docs = self.search_documents(query, doc_top_k)
        
        # Step 2: Get chunks from all documents, not just "relevant" ones
        # This ensures we don't miss relevant content from other documents
        all_chunks = self.search_chunks(query, chunk_top_k * 2)  # Get more chunks initially
        
        # Step 3: Balance chunks across documents
        balanced_chunks = []
        doc_chunk_count = {}
        max_chunks_per_doc = max(2, chunk_top_k // len(self.document_metadata)) if self.document_metadata else chunk_top_k
        
        for chunk in all_chunks:
            doc_idx = chunk["chunk"]["document_index"]
            doc_count = doc_chunk_count.get(doc_idx, 0)
            
            # Allow more chunks from highly relevant documents, but ensure diversity
            if doc_count < max_chunks_per_doc or len(balanced_chunks) < chunk_top_k // 2:
                balanced_chunks.append(chunk)
                doc_chunk_count[doc_idx] = doc_count + 1
                
                if len(balanced_chunks) >= chunk_top_k:
                    break
        
        # If we still don't have enough chunks, add the remaining best ones
        if len(balanced_chunks) < chunk_top_k:
            for chunk in all_chunks:
                if chunk not in balanced_chunks:
                    balanced_chunks.append(chunk)
                    if len(balanced_chunks) >= chunk_top_k:
                        break
        
        return {
            "query": query,
            "relevant_documents": relevant_docs,
            "relevant_chunks": balanced_chunks,
            "search_strategy": "balanced_hybrid"
        }

    def get_comprehensive_context(self, query: str, max_context_length: int = 4000) -> str:
        """Get comprehensive context for a query using hybrid search"""
        search_results = self.hybrid_search(query)
        
        context_parts = []
        current_length = 0
        
        # Add document summaries first
        context_parts.append("=== DOCUMENT SUMMARIES ===")
        for doc in search_results["relevant_documents"]:
            summary = doc["document"]["document_summary"][:500]  # Limit summary length
            doc_context = f"\nDocument: {os.path.basename(doc['document']['file_path'])}\nSummary: {summary}\nKey Topics: {', '.join(doc['document']['key_topics'][:5])}\n"
            
            if current_length + len(doc_context) < max_context_length:
                context_parts.append(doc_context)
                current_length += len(doc_context)
        
        # Add relevant chunks
        context_parts.append("\n=== RELEVANT CONTENT ===")
        for chunk in search_results["relevant_chunks"]:
            chunk_text = chunk["chunk"]["chunk_text"]
            chunk_context = f"\n[Page {chunk['chunk']['page_number']}] {chunk_text}\n"
            
            if current_length + len(chunk_context) < max_context_length:
                context_parts.append(chunk_context)
                current_length += len(chunk_context)
            else:
                break
        
        return "\n".join(context_parts)

    def save(self):
        """Save all indices and metadata"""
        # Save FAISS indices
        if self.document_index:
            faiss.write_index(self.document_index, os.path.join(self.persist_dir, "document.index"))
        if self.chunk_index:
            faiss.write_index(self.chunk_index, os.path.join(self.persist_dir, "chunk.index"))
        
        # Save metadata
        with open(os.path.join(self.persist_dir, "document_metadata.pkl"), "wb") as f:
            pickle.dump(self.document_metadata, f)
        with open(os.path.join(self.persist_dir, "chunk_metadata.pkl"), "wb") as f:
            pickle.dump(self.chunk_metadata, f)
        
        print(f"[INFO] Saved enhanced vector store to {self.persist_dir}")

    def load(self):
        """Load indices and metadata"""
        try:
            # Load FAISS indices
            doc_index_path = os.path.join(self.persist_dir, "document.index")
            chunk_index_path = os.path.join(self.persist_dir, "chunk.index")
            
            if os.path.exists(doc_index_path):
                self.document_index = faiss.read_index(doc_index_path)
            if os.path.exists(chunk_index_path):
                self.chunk_index = faiss.read_index(chunk_index_path)
            
            # Load metadata
            with open(os.path.join(self.persist_dir, "document_metadata.pkl"), "rb") as f:
                self.document_metadata = pickle.load(f)
            with open(os.path.join(self.persist_dir, "chunk_metadata.pkl"), "rb") as f:
                self.chunk_metadata = pickle.load(f)
            
            print(f"[INFO] Loaded enhanced vector store from {self.persist_dir}")
            print(f"[INFO] Documents: {len(self.document_metadata)}, Chunks: {len(self.chunk_metadata)}")
            
        except Exception as e:
            print(f"[ERROR] Failed to load enhanced vector store: {e}")

    def rebuild_vectorstore(self):
        """Force rebuild the vector store from all documents in data directory"""
        from src.data_loader import load_all_documents
        
        print("[INFO] Rebuilding vector store from all documents...")
        
        # Clear existing data
        self.document_metadata = []
        self.chunk_metadata = []
        self.document_index = None
        self.chunk_index = None
        
        # Load all documents
        documents = load_all_documents("data")
        
        if not documents:
            print("[WARNING] No documents found to rebuild vector store")
            return False
        
        # Extract unique file paths
        file_paths = list(set([doc.metadata.get("source", "") for doc in documents if doc.metadata.get("source")]))
        
        print(f"[INFO] Rebuilding with {len(file_paths)} document files")
        for file_path in file_paths:
            print(f"  - {os.path.basename(file_path)}")
        
        # Build from documents
        self.build_from_documents(file_paths)
        
        return True

    def get_document_info(self, file_path: str) -> Dict[str, Any]:
        """Get comprehensive information about a specific document"""
        for doc_meta in self.document_metadata:
            if doc_meta["file_path"] == file_path:
                return doc_meta
        return None