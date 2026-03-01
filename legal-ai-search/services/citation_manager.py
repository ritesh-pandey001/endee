"""
Citation management for tracking and formatting source citations.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.logging_config import logger
from app.models.schemas import Citation


class CitationManager:
    """
    Manage source citations for legal research answers.
    """
    
    def __init__(self):
        """Initialize citation manager."""
        pass
    
    def create_citation(self, doc_id: str, doc_name: str, chunk_id: str, 
                       text: str, score: float, 
                       metadata: Optional[Dict[str, Any]] = None) -> Citation:
        """
        Create a citation object from search result.
        
        Args:
            doc_id: Document ID
            doc_name: Document name
            chunk_id: Chunk ID
            text: Cited text
            score: Relevance score
            metadata: Additional metadata
            
        Returns:
            Citation object
        """
        metadata = metadata or {}
        
        # Extract page number if available
        page_number = metadata.get("page_number")
        if not page_number and "[Page " in text:
            import re
            match = re.search(r'\[Page (\d+)\]', text)
            if match:
                page_number = int(match.group(1))
        
        return Citation(
            doc_id=doc_id,
            doc_name=doc_name,
            chunk_id=chunk_id,
            text=self._clean_citation_text(text),
            score=score,
            page_number=page_number,
            metadata=metadata
        )
    
    def _clean_citation_text(self, text: str, max_length: int = 500) -> str:
        """
        Clean and truncate citation text.
        
        Args:
            text: Raw citation text
            max_length: Maximum length
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Truncate if needed
        if len(text) > max_length:
            text = text[:max_length].rsplit(' ', 1)[0] + "..."
        
        return text
    
    def format_citations(self, citations: List[Citation], style: str = "numbered") -> str:
        """
        Format citations for display.
        
        Args:
            citations: List of citations
            style: Citation style (numbered, apa, bluebook)
            
        Returns:
            Formatted citation string
        """
        if not citations:
            return "No citations available."
        
        if style == "numbered":
            return self._format_numbered(citations)
        elif style == "apa":
            return self._format_apa(citations)
        elif style == "bluebook":
            return self._format_bluebook(citations)
        else:
            return self._format_numbered(citations)
    
    def _format_numbered(self, citations: List[Citation]) -> str:
        """Format as numbered list."""
        lines = []
        for i, citation in enumerate(citations, 1):
            page_info = f", p. {citation.page_number}" if citation.page_number else ""
            lines.append(
                f"[{i}] {citation.doc_name}{page_info}\n"
                f"    {citation.text[:200]}..."
            )
        return "\n\n".join(lines)
    
    def _format_apa(self, citations: List[Citation]) -> str:
        """Format in APA style (simplified)."""
        lines = []
        for citation in citations:
            page_info = f", p. {citation.page_number}" if citation.page_number else ""
            lines.append(f"{citation.doc_name}{page_info}.")
        return "\n".join(lines)
    
    def _format_bluebook(self, citations: List[Citation]) -> str:
        """Format in Bluebook style (simplified)."""
        lines = []
        for citation in citations:
            page_info = f" at {citation.page_number}" if citation.page_number else ""
            lines.append(f"{citation.doc_name}{page_info}.")
        return "\n".join(lines)
    
    def rank_citations(self, citations: List[Citation], 
                      threshold: float = 0.7) -> List[Citation]:
        """
        Filter and rank citations by relevance.
        
        Args:
            citations: List of citations
            threshold: Minimum score threshold
            
        Returns:
            Filtered and ranked citations
        """
        # Filter by threshold
        filtered = [c for c in citations if c.score >= threshold]
        
        # Sort by score
        filtered.sort(key=lambda c: c.score, reverse=True)
        
        logger.info(f"Ranked {len(filtered)} citations above threshold {threshold}")
        return filtered
    
    def deduplicate_citations(self, citations: List[Citation]) -> List[Citation]:
        """
        Remove duplicate citations from the same document.
        
        Args:
            citations: List of citations
            
        Returns:
            Deduplicated citations
        """
        seen_docs = set()
        unique_citations = []
        
        for citation in citations:
            if citation.doc_id not in seen_docs:
                seen_docs.add(citation.doc_id)
                unique_citations.append(citation)
        
        logger.info(f"Deduplicated {len(citations)} to {len(unique_citations)} citations")
        return unique_citations
    
    def create_citations_from_results(self, search_results: List[Dict[str, Any]], 
                                     top_k: int = 5) -> List[Citation]:
        """
        Create citation objects from search results.
        
        Args:
            search_results: List of search results
            top_k: Number of citations to return
            
        Returns:
            List of citations
        """
        citations = []
        
        for result in search_results[:top_k]:
            metadata = result.get("metadata", {})
            citation = self.create_citation(
                doc_id=metadata.get("doc_id", "unknown"),
                doc_name=metadata.get("filename", "Unknown Document"),
                chunk_id=result.get("id", "unknown"),
                text=result.get("text", ""),
                score=result.get("score", 0.0),
                metadata=metadata
            )
            citations.append(citation)
        
        return citations
    
    def get_inline_citations(self, citations: List[Citation]) -> str:
        """
        Generate inline citation markers (e.g., [1], [2]).
        
        Args:
            citations: List of citations
            
        Returns:
            Inline citation text
        """
        if not citations:
            return ""
        
        citation_numbers = [str(i) for i in range(1, len(citations) + 1)]
        return f"[{', '.join(citation_numbers)}]"


# Global citation manager instance
citation_manager = CitationManager()
