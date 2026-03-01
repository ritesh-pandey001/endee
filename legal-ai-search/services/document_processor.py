"""
Document processing service for upload and indexing.
"""

import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import PyPDF2
from docx import Document as DocxDocument

from app.core.config import settings
from app.core.logging_config import logger
from services.hybrid_search import search_engine


class DocumentProcessor:
    """
    Process and index documents for the legal research assistant.
    """
    
    def __init__(self):
        """Initialize document processor."""
        self.documents_path = Path(settings.documents_path)
        self.documents_path.mkdir(parents=True, exist_ok=True)
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap
    
    def generate_doc_id(self, filename: str, content: str) -> str:
        """
        Generate unique document ID based on filename and content hash.
        
        Args:
            filename: Document filename
            content: Document content
            
        Returns:
            Unique document ID
        """
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        clean_filename = re.sub(r'[^a-zA-Z0-9_-]', '_', Path(filename).stem)
        return f"{clean_filename}_{timestamp}_{content_hash}"
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """
        Extract text from PDF file.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    text += f"\n[Page {page_num + 1}]\n{page_text}"
                return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    def extract_text_from_docx(self, docx_path: Path) -> str:
        """
        Extract text from DOCX file.
        
        Args:
            docx_path: Path to DOCX file
            
        Returns:
            Extracted text
        """
        try:
            doc = DocxDocument(docx_path)
            paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
            return "\n\n".join(paragraphs)
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {e}")
            raise
    
    def chunk_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks for indexing.
        
        Args:
            text: Input text to chunk
            metadata: Optional metadata to attach to chunks
            
        Returns:
            List of text chunks with metadata
        """
        metadata = metadata or {}
        
        # Split by sentences for better semantic boundaries
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = ""
        current_size = 0
        
        for sentence in sentences:
            sentence_size = len(sentence)
            
            if current_size + sentence_size <= self.chunk_size:
                current_chunk += sentence + " "
                current_size += sentence_size + 1
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # Start new chunk with overlap
                if self.chunk_overlap > 0 and chunks:
                    # Get last part of previous chunk for overlap
                    words = current_chunk.split()
                    overlap_words = words[-min(len(words), self.chunk_overlap // 5):]
                    current_chunk = " ".join(overlap_words) + " " + sentence + " "
                    current_size = len(current_chunk)
                else:
                    current_chunk = sentence + " "
                    current_size = sentence_size + 1
        
        # Add final chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # Format chunks with metadata
        formatted_chunks = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = {
                **metadata,
                "chunk_index": i,
                "total_chunks": len(chunks)
            }
            formatted_chunks.append({
                "text": chunk,
                "metadata": chunk_metadata
            })
        
        logger.info(f"Created {len(formatted_chunks)} chunks from text")
        return formatted_chunks
    
    def process_document(self, filename: str, content: Optional[str] = None, 
                        file_path: Optional[Path] = None,
                        metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a document: extract text, chunk, and index.
        
        Args:
            filename: Document filename
            content: Document text content (if already extracted)
            file_path: Path to document file (for PDF/DOCX)
            metadata: Additional metadata
            
        Returns:
            Document processing result with doc_id and stats
        """
        try:
            # Extract text if not provided
            if content is None:
                if file_path is None:
                    raise ValueError("Either content or file_path must be provided")
                
                file_ext = file_path.suffix.lower()
                if file_ext == '.pdf':
                    content = self.extract_text_from_pdf(file_path)
                elif file_ext == '.docx':
                    content = self.extract_text_from_docx(file_path)
                elif file_ext == '.txt':
                    content = file_path.read_text(encoding='utf-8')
                else:
                    raise ValueError(f"Unsupported file type: {file_ext}")
            
            # Generate document ID
            doc_id = self.generate_doc_id(filename, content)
            
            # Prepare document metadata
            doc_metadata = {
                "filename": filename,
                "doc_id": doc_id,
                "upload_date": datetime.utcnow().isoformat(),
                "size_bytes": len(content),
                **(metadata or {})
            }
            
            # Chunk the document
            chunks = self.chunk_text(content, doc_metadata)
            
            # Prepare for indexing
            chunk_texts = [chunk["text"] for chunk in chunks]
            chunk_metadatas = [chunk["metadata"] for chunk in chunks]
            chunk_ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
            
            # Index in hybrid search engine
            search_engine.add_documents(
                documents=chunk_texts,
                metadatas=chunk_metadatas,
                ids=chunk_ids
            )
            
            # Save original document
            doc_file_path = self.documents_path / f"{doc_id}.txt"
            doc_file_path.write_text(content, encoding='utf-8')
            
            result = {
                "doc_id": doc_id,
                "filename": filename,
                "num_chunks": len(chunks),
                "size_bytes": len(content),
                "upload_date": doc_metadata["upload_date"],
                "metadata": metadata or {}
            }
            
            logger.info(f"Successfully processed document {doc_id}: {len(chunks)} chunks")
            return result
            
        except Exception as e:
            logger.error(f"Error processing document {filename}: {e}")
            raise
    
    def upload_document(self, filename: str, content: str, 
                       metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Upload and process a document from content string.
        Supports text content or base64-encoded binary files (PDF, DOCX).
        
        Args:
            filename: Document filename
            content: Document text content or base64-encoded binary data
            metadata: Additional metadata
            
        Returns:
            Document processing result
        """
        import base64
        import tempfile
        
        file_ext = Path(filename).suffix.lower()
        
        # Check if content is base64-encoded (for PDF/DOCX)
        if file_ext in ['.pdf', '.docx']:
            try:
                # Decode base64 content
                binary_data = base64.b64decode(content)
                
                # Create temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
                    temp_file.write(binary_data)
                    temp_path = Path(temp_file.name)
                
                try:
                    # Extract text from the file
                    if file_ext == '.pdf':
                        text_content = self.extract_text_from_pdf(temp_path)
                    elif file_ext == '.docx':
                        text_content = self.extract_text_from_docx(temp_path)
                    
                    # Validate file size
                    size_mb = len(text_content.encode('utf-8')) / (1024 * 1024)
                    if size_mb > settings.max_upload_size_mb:
                        raise ValueError(
                            f"Document size ({size_mb:.2f}MB) exceeds maximum allowed "
                            f"({settings.max_upload_size_mb}MB)"
                        )
                    
                    # Process the extracted text
                    return self.process_document(filename, content=text_content, metadata=metadata)
                    
                finally:
                    # Clean up temporary file
                    if temp_path.exists():
                        temp_path.unlink()
                        
            except Exception as e:
                logger.error(f"Error processing binary file {filename}: {e}")
                raise ValueError(f"Failed to process {file_ext.upper()} file: {str(e)}")
        
        else:
            # Plain text file - validate and process
            size_mb = len(content.encode('utf-8')) / (1024 * 1024)
            if size_mb > settings.max_upload_size_mb:
                raise ValueError(
                    f"Document size ({size_mb:.2f}MB) exceeds maximum allowed "
                    f"({settings.max_upload_size_mb}MB)"
                )
            
            return self.process_document(filename, content=content, metadata=metadata)
    
    def upload_file(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Upload and process a document from file path.
        
        Args:
            file_path: Path to document file
            metadata: Additional metadata
            
        Returns:
            Document processing result
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Validate file size
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > settings.max_upload_size_mb:
            raise ValueError(
                f"File size ({size_mb:.2f}MB) exceeds maximum allowed "
                f"({settings.max_upload_size_mb}MB)"
            )
        
        return self.process_document(path.name, file_path=path, metadata=metadata)
    
    def get_document(self, doc_id: str) -> Optional[str]:
        """
        Retrieve original document content by ID.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document content or None if not found
        """
        doc_path = self.documents_path / f"{doc_id}.txt"
        if doc_path.exists():
            return doc_path.read_text(encoding='utf-8')
        return None
    
    def list_documents(self) -> List[str]:
        """
        List all indexed documents.
        
        Returns:
            List of document IDs
        """
        return [f.stem for f in self.documents_path.glob("*.txt")]
    
    def clear_all_documents(self) -> Dict[str, Any]:
        """
        Clear all documents from the system.
        Deletes all files in the documents directory.
        
        Returns:
            Dictionary with operation result
        """
        try:
            files_deleted = 0
            
            # Delete all .txt files in documents directory
            for file_path in self.documents_path.glob("*.txt"):
                try:
                    file_path.unlink()
                    files_deleted += 1
                    logger.info(f"Deleted document: {file_path.name}")
                except Exception as e:
                    logger.error(f"Error deleting {file_path.name}: {e}")
            
            logger.info(f"Cleared {files_deleted} documents")
            
            return {
                "success": True,
                "files_deleted": files_deleted
            }
            
        except Exception as e:
            logger.error(f"Error clearing documents: {e}")
            return {
                "success": False,
                "files_deleted": 0,
                "error": str(e)
            }


# Global document processor instance
document_processor = DocumentProcessor()
