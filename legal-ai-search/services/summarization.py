"""
Case summarization service using LLM.
"""

import time
import re
from typing import List, Dict, Any, Optional
import google.generativeai as genai

from app.core.config import settings
from app.core.logging_config import logger
from services.document_processor import document_processor


class SummarizationService:
    """
    Legal case and document summarization service.
    """
    
    def __init__(self):
        """Initialize summarization service."""
        # Configure Google Gemini API
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)
        
        self.summary_prompts = {
            "brief": """Provide a brief summary of this legal document in 2-3 sentences. 
                       Focus on the most critical information.""",
            
            "comprehensive": """Provide a comprehensive summary of this legal document including:
                               1. Main subject matter and parties involved
                               2. Key legal issues and arguments
                               3. Important findings or rulings
                               4. Significant implications or outcomes
                               
                               Be thorough but concise.""",
            
            "key_points": """Extract and list the key points from this legal document.
                            Present them as a bulleted list with clear, concise statements.
                            Focus on actionable insights and critical information."""
        }
    
    def extract_entities(self, text: str) -> List[str]:
        """
        Extract legal entities from text (parties, courts, judges, etc.).
        
        Args:
            text: Legal document text
            
        Returns:
            List of extracted entities
        """
        prompt = """Extract all important legal entities from this text, including:
        - Party names (plaintiffs, defendants, appellants, etc.)
        - Court names
        - Judge names
        - Case numbers
        - Legal statutes or regulations mentioned
        
        Return only a JSON array of strings, one entity per string.
        
        Text:
        {text}
        """
        
        try:
            response = self.model.generate_content(
                f"You are a legal entity extraction assistant. Return only a JSON array.\n\n{prompt.format(text=text[:4000])}"
            )
            
            # Parse JSON response
            import json
            entities_text = response.text.strip()
            entities = json.loads(entities_text)
            
            return entities if isinstance(entities, list) else []
            
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            # Fallback: basic pattern matching
            return self._extract_entities_fallback(text)
    
    def _extract_entities_fallback(self, text: str) -> List[str]:
        """Fallback entity extraction using regex patterns."""
        entities = []
        
        # Extract case numbers (e.g., "No. 21-1234")
        case_numbers = re.findall(r'No\.\s*\d{2,4}-\d+', text)
        entities.extend(case_numbers)
        
        # Extract court names (basic patterns)
        courts = re.findall(r'(Supreme Court|Court of Appeals|District Court|Circuit Court)[^.]*', text)
        entities.extend([c.strip() for c in courts[:5]])
        
        # Extract capitalized names (likely parties or judges)
        names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}\b', text)
        # Filter common words
        common_words = {'Court', 'State', 'United', 'States', 'Judge', 'Justice', 'The'}
        entities.extend([n for n in names[:10] if n not in common_words])
        
        return list(set(entities))[:15]  # Return unique, limited list
    
    def extract_key_points(self, text: str) -> List[str]:
        """
        Extract key points from legal text.
        
        Args:
            text: Legal document text
            
        Returns:
            List of key points
        """
        prompt = self.summary_prompts["key_points"] + f"\n\nDocument:\n{text}"
        
        try:
            response = self.model.generate_content(
                f"You are a legal document analysis assistant.\n\n{prompt}"
            )
            
            content = response.text.strip()
            
            # Parse bullet points
            lines = content.split('\n')
            key_points = []
            for line in lines:
                line = line.strip()
                # Remove bullet markers
                line = re.sub(r'^[-•*]\s*', '', line)
                line = re.sub(r'^\d+\.\s*', '', line)
                if line:
                    key_points.append(line)
            
            return key_points
            
        except Exception as e:
            logger.error(f"Error extracting key points: {e}")
            return []
    
    def summarize_text(self, text: str, summary_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Summarize legal text.
        
        Args:
            text: Text to summarize
            summary_type: Type of summary (brief, comprehensive, key_points)
            
        Returns:
            Summary result with metadata
        """
        start_time = time.time()
        
        if summary_type not in self.summary_prompts:
            summary_type = "comprehensive"
        
        prompt = self.summary_prompts[summary_type] + f"\n\nDocument:\n{text}"
        
        try:
            # Generate summary
            response = self.model.generate_content(
                f"You are an expert legal document summarization assistant.\n\n{prompt}"
            )
            
            summary = response.text.strip()
            
            # Extract key points and entities in parallel
            key_points = self.extract_key_points(text) if summary_type != "key_points" else []
            entities = self.extract_entities(text)
            
            processing_time = (time.time() - start_time) * 1000
            
            result = {
                "summary": summary,
                "key_points": key_points,
                "entities": entities,
                "processing_time_ms": processing_time,
                "word_count": len(summary.split())
            }
            
            logger.info(f"Summarization completed in {processing_time:.2f}ms")
            return result
            
        except Exception as e:
            logger.error(f"Error in summarization: {e}")
            raise
    
    def summarize_document(self, doc_id: str, summary_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Summarize a document by ID.
        
        Args:
            doc_id: Document ID
            summary_type: Type of summary
            
        Returns:
            Summary result
        """
        # Retrieve document
        content = document_processor.get_document(doc_id)
        
        if not content:
            raise ValueError(f"Document not found: {doc_id}")
        
        return self.summarize_text(content, summary_type)
    
    def summarize_search_results(self, results: List[Dict[str, Any]]) -> str:
        """
        Create a summary from multiple search results.
        
        Args:
            results: List of search results
            
        Returns:
            Combined summary
        """
        if not results:
            return "No results to summarize."
        
        # Combine text from results
        combined_text = "\n\n---\n\n".join([
            f"[Source {i+1}]\n{r.get('text', '')}"
            for i, r in enumerate(results[:5])  # Limit to top 5
        ])
        
        prompt = f"""Synthesize the following legal sources into a coherent summary:

{combined_text}

Provide a comprehensive answer that integrates information from all sources.
Mention when sources agree or disagree on key points."""
        
        try:
            response = self.model.generate_content(
                f"You are a legal research synthesis assistant.\n\n{prompt}"
            )
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error summarizing search results: {e}")
            return "Error generating summary."


# Global summarization service instance
summarization_service = SummarizationService()
