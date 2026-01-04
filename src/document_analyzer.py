"""
Enhanced document analyzer for comprehensive content analysis of all document types
Supports: PDF, TXT, CSV, Excel, Word, JSON
"""
import os
from typing import List, Dict, Any, Tuple
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader, TextLoader, CSVLoader, Docx2txtLoader, JSONLoader
)
from langchain_community.document_loaders.excel import UnstructuredExcelLoader
from sentence_transformers import SentenceTransformer
import numpy as np
from collections import defaultdict
import re

class DocumentAnalyzer:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", " ", ""]
        )
        print(f"[INFO] Document analyzer initialized with model: {model_name}")

    def analyze_document(self, file_path: str) -> Dict[str, Any]:
        """
        Comprehensive document analysis for all supported file types including:
        - Full document summary
        - Section-wise analysis
        - Key topics extraction
        - Structured content mapping
        
        Supports: PDF, TXT, CSV, Excel, Word, JSON
        """
        print(f"[INFO] Analyzing document: {file_path}")
        
        # Determine file type and load accordingly
        file_extension = Path(file_path).suffix.lower()
        pages = self._load_document_by_type(file_path, file_extension)
        
        if not pages:
            print(f"[WARNING] No content loaded from {file_path}")
            return self._create_empty_analysis(file_path)
        
        # Extract full text
        full_text = "\n".join([page.page_content for page in pages])
        
        # Generate document-level summary
        doc_summary = self._generate_document_summary(full_text)
        
        # Extract key topics and themes
        key_topics = self._extract_key_topics(full_text)
        
        # Analyze document structure (adapted for different file types)
        structure = self._analyze_document_structure(pages, file_extension)
        
        # Create semantic chunks with context
        semantic_chunks = self._create_semantic_chunks(pages, file_extension)
        
        # Generate embeddings for different levels
        embeddings = self._generate_multi_level_embeddings(
            full_text, doc_summary, semantic_chunks
        )
        
        return {
            "file_path": file_path,
            "file_type": file_extension,
            "total_pages": len(pages),
            "full_text": full_text,
            "document_summary": doc_summary,
            "key_topics": key_topics,
            "structure": structure,
            "semantic_chunks": semantic_chunks,
            "embeddings": embeddings,
            "metadata": {
                "source": file_path,
                "file_type": file_extension,
                "total_chars": len(full_text),
                "total_pages": len(pages)
            }
        }

    def _load_document_by_type(self, file_path: str, file_extension: str) -> List[Any]:
        """Load document based on file type"""
        try:
            if file_extension == '.pdf':
                loader = PyPDFLoader(file_path)
            elif file_extension == '.txt':
                loader = TextLoader(file_path)
            elif file_extension == '.csv':
                loader = CSVLoader(file_path)
            elif file_extension in ['.xlsx', '.xls']:
                loader = UnstructuredExcelLoader(file_path)
            elif file_extension == '.docx':
                loader = Docx2txtLoader(file_path)
            elif file_extension == '.json':
                loader = JSONLoader(file_path)
            else:
                print(f"[WARNING] Unsupported file type: {file_extension}")
                return []
            
            pages = loader.load()
            print(f"[INFO] Loaded {len(pages)} pages/sections from {file_extension} file")
            return pages
            
        except Exception as e:
            print(f"[ERROR] Failed to load {file_path}: {e}")
            return []

    def _create_empty_analysis(self, file_path: str) -> Dict[str, Any]:
        """Create empty analysis structure for failed loads"""
        return {
            "file_path": file_path,
            "file_type": Path(file_path).suffix.lower(),
            "total_pages": 0,
            "full_text": "",
            "document_summary": "Failed to load document content",
            "key_topics": [],
            "structure": {"sections": [], "headings": [], "page_summaries": []},
            "semantic_chunks": [],
            "embeddings": {"document": np.array([]), "chunks": np.array([])},
            "metadata": {"source": file_path, "total_chars": 0, "total_pages": 0}
        }

    def _generate_document_summary(self, full_text: str, max_length: int = 2000) -> str:
        """Generate a comprehensive summary of the entire document"""
        # For very long documents, create summary from key sections
        if len(full_text) > 10000:
            # Split into sections and summarize key parts
            sections = self._split_into_sections(full_text)
            key_sections = sections[:5]  # Take first 5 sections
            summary_text = "\n".join(key_sections)
        else:
            summary_text = full_text
        
        # Truncate if still too long
        if len(summary_text) > max_length:
            summary_text = summary_text[:max_length] + "..."
        
        return summary_text

    def _extract_key_topics(self, text: str) -> List[str]:
        """Extract key topics and themes from the document"""
        # Simple keyword extraction (can be enhanced with NLP libraries)
        # Remove common words and extract meaningful terms
        words = re.findall(r'\b[A-Za-z]{4,}\b', text.lower())
        word_freq = defaultdict(int)
        
        # Common stop words to exclude
        stop_words = {
            'this', 'that', 'with', 'have', 'will', 'from', 'they', 'been', 
            'were', 'said', 'each', 'which', 'their', 'time', 'would', 'there',
            'could', 'other', 'more', 'very', 'what', 'know', 'just', 'first',
            'into', 'over', 'think', 'also', 'your', 'work', 'life', 'only',
            'can', 'should', 'after', 'being', 'now', 'made', 'before', 'here',
            'through', 'when', 'where', 'how', 'all', 'any', 'may', 'say'
        }
        
        for word in words:
            if word not in stop_words and len(word) > 4:
                word_freq[word] += 1
        
        # Return top 20 most frequent meaningful terms
        top_topics = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]
        return [topic[0] for topic in top_topics]

    def _analyze_document_structure(self, pages: List[Any], file_extension: str) -> Dict[str, Any]:
        """Analyze document structure based on file type"""
        structure = {
            "sections": [],
            "headings": [],
            "page_summaries": [],
            "file_type_specific": {}
        }
        
        for i, page in enumerate(pages):
            content = page.page_content
            
            # File type specific analysis
            if file_extension == '.pdf':
                structure["file_type_specific"] = self._analyze_pdf_structure(content)
            elif file_extension == '.csv':
                structure["file_type_specific"] = self._analyze_csv_structure(content)
            elif file_extension == '.json':
                structure["file_type_specific"] = self._analyze_json_structure(content)
            elif file_extension in ['.xlsx', '.xls']:
                structure["file_type_specific"] = self._analyze_excel_structure(content)
            elif file_extension == '.docx':
                structure["file_type_specific"] = self._analyze_word_structure(content)
            
            # Common analysis for all types
            headings = self._extract_headings(content, file_extension)
            page_summary = content[:300] + "..." if len(content) > 300 else content
            
            structure["headings"].extend(headings)
            structure["page_summaries"].append({
                "page": i + 1,
                "summary": page_summary,
                "headings": headings,
                "content_type": self._identify_content_type(content, file_extension)
            })
        
        return structure

    def _analyze_pdf_structure(self, content: str) -> Dict[str, Any]:
        """PDF-specific structure analysis"""
        return {
            "has_tables": "table" in content.lower() or "|" in content,
            "has_figures": "figure" in content.lower() or "fig." in content.lower(),
            "has_references": "references" in content.lower() or "bibliography" in content.lower(),
            "paragraph_count": len([p for p in content.split('\n\n') if len(p.strip()) > 50])
        }

    def _analyze_csv_structure(self, content: str) -> Dict[str, Any]:
        """CSV-specific structure analysis"""
        lines = content.split('\n')
        return {
            "row_count": len(lines),
            "estimated_columns": len(lines[0].split(',')) if lines else 0,
            "has_header": True,  # Assume first row is header
            "data_types": "mixed"  # Could be enhanced with actual type detection
        }

    def _analyze_json_structure(self, content: str) -> Dict[str, Any]:
        """JSON-specific structure analysis"""
        try:
            import json
            data = json.loads(content)
            return {
                "structure_type": type(data).__name__,
                "key_count": len(data) if isinstance(data, dict) else None,
                "item_count": len(data) if isinstance(data, list) else None,
                "nested_levels": self._count_json_nesting(data)
            }
        except:
            return {"structure_type": "invalid_json", "parsing_error": True}

    def _analyze_excel_structure(self, content: str) -> Dict[str, Any]:
        """Excel-specific structure analysis"""
        lines = content.split('\n')
        return {
            "row_count": len(lines),
            "has_multiple_sheets": "sheet" in content.lower(),
            "has_formulas": any(line.strip().startswith('=') for line in lines),
            "data_density": len([l for l in lines if l.strip()]) / max(len(lines), 1)
        }

    def _analyze_word_structure(self, content: str) -> Dict[str, Any]:
        """Word document-specific structure analysis"""
        return {
            "paragraph_count": len(content.split('\n\n')),
            "has_headings": any(line.isupper() or line.istitle() for line in content.split('\n')[:10]),
            "has_lists": '•' in content or any(line.strip().startswith(('1.', '2.', '-', '*')) for line in content.split('\n')),
            "word_count": len(content.split())
        }

    def _extract_headings(self, content: str, file_extension: str) -> List[str]:
        """Extract headings based on file type"""
        headings = []
        lines = content.split('\n')
        
        if file_extension == '.pdf':
            # PDF heading extraction
            for line in lines:
                line = line.strip()
                if (len(line.split()) <= 8 and len(line) > 5 and 
                    (line.isupper() or line.istitle()) and not line.endswith('.')):
                    headings.append(line)
        
        elif file_extension == '.csv':
            # CSV headers (first row)
            if lines:
                headings = [col.strip() for col in lines[0].split(',')]
        
        elif file_extension in ['.docx', '.txt']:
            # Word/Text heading extraction
            for line in lines:
                line = line.strip()
                if (len(line) > 0 and len(line.split()) <= 10 and 
                    (line.isupper() or line.istitle()) and 
                    not line.endswith('.') and len(line) < 100):
                    headings.append(line)
        
        return headings[:10]  # Limit to top 10 headings

    def _identify_content_type(self, content: str, file_extension: str) -> str:
        """Identify the type of content in the section"""
        content_lower = content.lower()
        
        if file_extension == '.csv':
            return "tabular_data"
        elif file_extension == '.json':
            return "structured_data"
        elif "table" in content_lower or "|" in content:
            return "table"
        elif "figure" in content_lower or "chart" in content_lower:
            return "figure_reference"
        elif len(content.split()) < 50:
            return "short_text"
        elif any(keyword in content_lower for keyword in ["abstract", "summary", "conclusion"]):
            return "summary_section"
        else:
            return "body_text"

    def _count_json_nesting(self, obj, level=0) -> int:
        """Count nesting levels in JSON structure"""
        if isinstance(obj, dict):
            return max([self._count_json_nesting(v, level + 1) for v in obj.values()] + [level])
        elif isinstance(obj, list) and obj:
            return max([self._count_json_nesting(item, level + 1) for item in obj] + [level])
        else:
            return level

    def _create_semantic_chunks(self, pages: List[Any], file_extension: str) -> List[Dict[str, Any]]:
        """Create semantically meaningful chunks with enhanced context for all file types"""
        chunks = []
        
        for page_idx, page in enumerate(pages):
            # Adapt chunking strategy based on file type
            if file_extension == '.csv':
                # For CSV, treat each row as a potential chunk
                page_chunks = self._chunk_csv_content(page.page_content)
            elif file_extension == '.json':
                # For JSON, chunk by logical structure
                page_chunks = self._chunk_json_content(page.page_content)
            else:
                # Standard text chunking for PDF, TXT, Word, Excel
                page_chunks = self.text_splitter.split_text(page.page_content)
            
            for chunk_idx, chunk_text in enumerate(page_chunks):
                # Add context information
                chunk_data = {
                    "text": chunk_text,
                    "page_number": page_idx + 1,
                    "chunk_index": chunk_idx,
                    "source": page.metadata.get("source", ""),
                    "file_type": file_extension,
                    "context": {
                        "previous_chunk": page_chunks[chunk_idx - 1] if chunk_idx > 0 else "",
                        "next_chunk": page_chunks[chunk_idx + 1] if chunk_idx < len(page_chunks) - 1 else "",
                        "page_context": page.page_content[:200] + "..." if len(page.page_content) > 200 else page.page_content,
                        "content_type": self._identify_content_type(chunk_text, file_extension)
                    }
                }
                chunks.append(chunk_data)
        
        return chunks

    def _chunk_csv_content(self, content: str) -> List[str]:
        """Special chunking for CSV content"""
        lines = content.split('\n')
        if len(lines) <= 1:
            return [content]
        
        # Keep header with each chunk
        header = lines[0]
        chunks = []
        
        # Group rows into chunks of reasonable size
        chunk_size = 10  # rows per chunk
        for i in range(1, len(lines), chunk_size):
            chunk_lines = [header] + lines[i:i + chunk_size]
            chunk_content = '\n'.join(chunk_lines)
            if chunk_content.strip():
                chunks.append(chunk_content)
        
        return chunks if chunks else [content]

    def _chunk_json_content(self, content: str) -> List[str]:
        """Special chunking for JSON content"""
        try:
            import json
            data = json.loads(content)
            
            if isinstance(data, list):
                # Chunk list items
                chunks = []
                chunk_size = 5  # items per chunk
                for i in range(0, len(data), chunk_size):
                    chunk_data = data[i:i + chunk_size]
                    chunks.append(json.dumps(chunk_data, indent=2))
                return chunks
            
            elif isinstance(data, dict):
                # Chunk dictionary by keys
                chunks = []
                items = list(data.items())
                chunk_size = 3  # key-value pairs per chunk
                for i in range(0, len(items), chunk_size):
                    chunk_dict = dict(items[i:i + chunk_size])
                    chunks.append(json.dumps(chunk_dict, indent=2))
                return chunks
            
        except json.JSONDecodeError:
            pass
        
        # Fallback to regular text chunking
        return self.text_splitter.split_text(content)

    def _generate_multi_level_embeddings(self, full_text: str, summary: str, chunks: List[Dict]) -> Dict[str, np.ndarray]:
        """Generate embeddings at multiple levels for better retrieval"""
        embeddings = {}
        
        # Document-level embedding
        doc_embedding = self.model.encode([summary])
        embeddings["document"] = doc_embedding[0]
        
        # Chunk-level embeddings
        chunk_texts = [chunk["text"] for chunk in chunks]
        if chunk_texts:
            chunk_embeddings = self.model.encode(chunk_texts, show_progress_bar=True)
            embeddings["chunks"] = chunk_embeddings
        
        print(f"[INFO] Generated embeddings - Document: {doc_embedding.shape}, Chunks: {chunk_embeddings.shape if chunk_texts else 'None'}")
        
        return embeddings

    def _split_into_sections(self, text: str) -> List[str]:
        """Split document into logical sections"""
        # Split by double newlines (paragraph breaks)
        sections = text.split('\n\n')
        # Filter out very short sections
        sections = [s.strip() for s in sections if len(s.strip()) > 100]
        return sections

    def analyze_multiple_documents(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """Analyze multiple documents and return comprehensive analysis"""
        analyses = []
        for file_path in file_paths:
            try:
                analysis = self.analyze_document(file_path)
                analyses.append(analysis)
            except Exception as e:
                print(f"[ERROR] Failed to analyze {file_path}: {e}")
        
        return analyses