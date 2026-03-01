"""
LLM Service Module for AI Legal Research Assistant
Handles Gemini API interactions for embeddings and text generation.
"""

from typing import List, Dict, Any, Optional
import google.generativeai as genai

from app.core.config import settings
from app.core.logging_config import logger


class LLMService:
    """
    Service for interacting with Google Gemini API.
    Handles embeddings generation and answer generation.
    """
    
    def __init__(self):
        """Initialize Gemini API."""
        try:
            genai.configure(api_key=settings.gemini_api_key)
            self.embedding_model = settings.embedding_model
            self.generation_model = genai.GenerativeModel(settings.gemini_model)
            logger.info(f"LLM Service initialized with {settings.gemini_model}")
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM Service: {e}")
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector (3072 dimensions for gemini-embedding-001)
        """
        try:
            result = genai.embed_content(
                model=self.embedding_model,
                content=text,
                task_type="retrieval_document"
            )
            
            embedding = result["embedding"]
            logger.debug(f"Generated embedding, dimension: {len(embedding)}")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for search query.
        
        Args:
            query: Search query text
            
        Returns:
            Query embedding vector
        """
        try:
            result = genai.embed_content(
                model=self.embedding_model,
                content=query,
                task_type="retrieval_query"
            )
            
            embedding = result["embedding"]
            logger.debug(f"Generated query embedding, dimension: {len(embedding)}")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            raise
    
    def generate_answer(
        self,
        question: str,
        context_documents: List[Dict[str, Any]],
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate answer using Gemini based on question and retrieved context.
        
        Args:
            question: User's question
            context_documents: List of retrieved documents with text and metadata
            max_tokens: Maximum tokens in response (uses config default if None)
            
        Returns:
            Generated answer text
        """
        try:
            # Build context from retrieved documents
            context_parts = []
            for i, doc in enumerate(context_documents, 1):
                text = doc.get("text", "")
                metadata = doc.get("metadata", {})
                doc_name = metadata.get("filename", f"Document {i}")
                
                context_parts.append(
                    f"[Document {i}: {doc_name}]\n{text}\n"
                )
            
            context = "\n".join(context_parts)
            
            # Build prompt
            prompt = f"""You are an AI legal research assistant. Answer the following question based ONLY on the provided legal documents. Be precise and cite specific document sections when possible.

Question: {question}

Legal Documents:
{context}

Instructions:
- Provide a clear, concise answer based on the documents
- Cite specific documents by number when referencing information
- If the documents don't contain enough information, say so
- Use legal terminology appropriately
- Focus on accuracy over completeness

Answer:"""
            
            # Generate response
            response = self.generation_model.generate_content(
                prompt,
                generation_config={
                    "max_output_tokens": max_tokens or settings.max_tokens,
                    "temperature": settings.temperature
                }
            )
            
            answer = response.text
            logger.info(f"Generated answer, length: {len(answer)}")
            return answer
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise
    
    def summarize_document(
        self,
        text: str,
        max_length: int = 200
    ) -> Dict[str, Any]:
        """
        Summarize a legal document.
        
        Args:
            text: Document text
            max_length: Target summary length in words
            
        Returns:
            Dictionary with summary, key points, and entities
        """
        try:
            prompt = f"""Analyze the following legal document and provide:
1. A concise summary ({max_length} words max)
2. Key legal points (3-5 bullet points)
3. Important entities (parties, dates, amounts, terms)

Document:
{text}

Provide your response in the following format:
SUMMARY:
[Your summary here]

KEY POINTS:
- [Point 1]
- [Point 2]
...

ENTITIES:
- [Entity 1]
- [Entity 2]
..."""
            
            response = self.generation_model.generate_content(prompt)
            result_text = response.text
            
            # Parse response
            summary = ""
            key_points = []
            entities = []
            
            current_section = None
            for line in result_text.split('\n'):
                line = line.strip()
                
                if line.startswith('SUMMARY:'):
                    current_section = 'summary'
                    continue
                elif line.startswith('KEY POINTS:'):
                    current_section = 'key_points'
                    continue
                elif line.startswith('ENTITIES:'):
                    current_section = 'entities'
                    continue
                
                if line:
                    if current_section == 'summary':
                        summary += line + " "
                    elif current_section == 'key_points' and line.startswith('-'):
                        key_points.append(line[1:].strip())
                    elif current_section == 'entities' and line.startswith('-'):
                        entities.append(line[1:].strip())
            
            return {
                "summary": summary.strip(),
                "key_points": key_points,
                "entities": entities
            }
            
        except Exception as e:
            logger.error(f"Error summarizing document: {e}")
            raise


# Global instance
llm_service = LLMService()
