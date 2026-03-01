"""
Hybrid Search System combining vector and keyword search with Endee Vector Database.

This module provides intelligent document retrieval by combining:
- Semantic search using Endee Vector Database (Official SDK)
- Keyword search using BM25 algorithm
- Weighted fusion of results for optimal relevance
"""

import time
from typing import List, Dict, Any, Tuple
import numpy as np
from rank_bm25 import BM25Okapi
import google.generativeai as genai

from services.vector_store import vector_store
from app.core.config import settings
from app.core.logging_config import logger


class HybridSearchEngine:
    """
    Hybrid search engine combining vector (semantic) and keyword (BM25) search.
    
    Uses Endee Vector Database (Official SDK) for high-performance semantic similarity search
    and BM25 for traditional keyword-based retrieval.
    """
    
    def __init__(self):
        """Initialize hybrid search engine with Endee vector store and BM25."""
        # Configure Google Gemini API
        genai.configure(api_key=settings.gemini_api_key)
        
        # Use official Endee SDK vector store
        self.vector_store = vector_store
        logger.info("Initialized Endee Vector Store (Official SDK) for semantic search")
        
        # BM25 index (will be built from documents)
        self.bm25_index = None
        self.bm25_documents = []
        self.bm25_ids = []
        self.bm25_metadatas = []
        
        # Note: BM25 index building is deferred until documents are added
        # since SDK doesn't support listing all vectors easily
        logger.info("BM25 index will be built incrementally as documents are added")
    
    def _build_bm25_index(self):
        """Build BM25 index from stored documents in memory."""
        try:
            if self.bm25_documents:
                # Tokenize documents for BM25
                tokenized_docs = [doc.lower().split() for doc in self.bm25_documents]
                self.bm25_index = BM25Okapi(tokenized_docs)
                
                logger.info(f"Built BM25 index with {len(self.bm25_documents)} documents")
            else:
                logger.info("No documents available for BM25 index")
                self.bm25_index = None
        except Exception as e:
            logger.error(f"Error building BM25 index: {e}")
            self.bm25_index = None
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using Google Gemini.
        
        Args:
            text: Input text to embed
            
        Returns:
            Embedding vector
        """
        try:
            result = genai.embed_content(
                model=settings.embedding_model,
                content=text
            )
            return result["embedding"]
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ):
        """
        Add documents to both vector and keyword indexes.
        
        Args:
            documents: List of document texts
            metadatas: List of metadata dictionaries
            ids: List of document IDs
        """
        try:
            # Generate embeddings for all documents
            embeddings = []
            for doc in documents:
                embedding = self.get_embedding(doc)
                embeddings.append(embedding)
            
            # Prepare metadata with text for vector store
            enhanced_metadatas = []
            for doc, meta in zip(documents, metadatas):
                enhanced_meta = meta.copy()
                enhanced_meta["text"] = doc
                enhanced_metadatas.append(enhanced_meta)
            
            # Add to Endee Vector Store (Official SDK)
            self.vector_store.upsert_documents(
                doc_ids=ids,
                vectors=embeddings,
                metadatas=enhanced_metadatas
            )
            
            # Add to BM25 index (in-memory)
            self.bm25_documents.extend(documents)
            self.bm25_ids.extend(ids)
            self.bm25_metadatas.extend(metadatas)
            self._build_bm25_index()
            
            logger.info(f"Added {len(documents)} documents to hybrid search engine")
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    def vector_search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Perform semantic vector search using Endee Official SDK.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of search results with scores
        """
        try:
            # Generate query embedding
            query_embedding = self.get_embedding(query)
            
            # Search in Endee Vector Store (Official SDK)
            results = self.vector_store.search(
                query_vector=query_embedding,
                top_k=top_k
            )
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "id": result["id"],
                    "text": result["text"],
                    "score": result["score"],
                    "metadata": result["metadata"],
                    "search_type": "vector"
                })
            
            logger.info(f"Vector search returned {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error in vector search: {e}")
            return []
    
    def keyword_search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Perform keyword-based BM25 search.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of search results with BM25 scores
        """
        if not self.bm25_index or not self.bm25_documents:
            logger.warning("BM25 index not available")
            return []
        
        try:
            # Tokenize query
            tokenized_query = query.lower().split()
            
            # Get BM25 scores
            scores = self.bm25_index.get_scores(tokenized_query)
            
            # Get top-k results
            top_indices = np.argsort(scores)[-top_k:][::-1]
            
            results = []
            for idx in top_indices:
                if scores[idx] > 0:  # Only include documents with non-zero scores
                    results.append({
                        "id": self.bm25_ids[idx],
                        "text": self.bm25_documents[idx],
                        "score": float(scores[idx]),
                        "metadata": {},
                        "search_type": "keyword"
                    })
            
            logger.info(f"Keyword search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error in keyword search: {e}")
            return []
    
    def hybrid_search(
        self,
        query: str,
        top_k: int = 5,
        vector_weight: float = None,
        keyword_weight: float = None
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining vector and keyword results.
        
        Args:
            query: Search query
            top_k: Number of final results to return
            vector_weight: Weight for vector search (default from settings)
            keyword_weight: Weight for keyword search (default from settings)
            
        Returns:
            List of ranked search results
        """
        start_time = time.time()
        
        # Use configured weights if not provided
        vector_weight = vector_weight or settings.vector_weight
        keyword_weight = keyword_weight or settings.keyword_weight
        
        try:
            # Perform both searches
            vector_results = self.vector_search(query, top_k=top_k * 2)
            keyword_results = self.keyword_search(query, top_k=top_k * 2)
            
            # Combine results
            combined_scores = {}
            
            # Add vector search scores
            for result in vector_results:
                doc_id = result["id"]
                combined_scores[doc_id] = {
                    "text": result["text"],
                    "metadata": result.get("metadata", {}),
                    "vector_score": result["score"] * vector_weight,
                    "keyword_score": 0.0
                }
            
            # Add keyword search scores
            for result in keyword_results:
                doc_id = result["id"]
                if doc_id in combined_scores:
                    combined_scores[doc_id]["keyword_score"] = result["score"] * keyword_weight
                else:
                    combined_scores[doc_id] = {
                        "text": result["text"],
                        "metadata": result.get("metadata", {}),
                        "vector_score": 0.0,
                        "keyword_score": result["score"] * keyword_weight
                    }
            
            # Calculate final scores and rank
            final_results = []
            for doc_id, data in combined_scores.items():
                final_score = data["vector_score"] + data["keyword_score"]
                final_results.append({
                    "id": doc_id,
                    "text": data["text"],
                    "score": final_score,
                    "metadata": data["metadata"],
                    "vector_score": data["vector_score"],
                    "keyword_score": data["keyword_score"]
                })
            
            # Sort by final score and get top-k
            final_results.sort(key=lambda x: x["score"], reverse=True)
            final_results = final_results[:top_k]
            
            search_time = time.time() - start_time
            logger.info(
                f"Hybrid search completed in {search_time:.3f}s, "
                f"returned {len(final_results)} results"
            )
            
            return final_results
            
        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the indexed collection.
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            stats = self.vector_store.get_stats()
            
            # Count unique documents instead of total chunks
            unique_docs = set()
            if self.bm25_metadatas:
                for metadata in self.bm25_metadatas:
                    if metadata and 'doc_id' in metadata:
                        unique_docs.add(metadata['doc_id'])
            
            return {
                "total_documents": len(unique_docs) if unique_docs else stats.get("total_documents", 0),
                "total_chunks": stats.get("total_documents", 0),
                "vector_dimension": stats.get("dimension", 768),
                "similarity_metric": stats.get("metric", "cosine"),
                "bm25_index_size": len(self.bm25_documents) if self.bm25_documents else 0
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {"total_documents": 0}
    
    def delete_document(self, doc_id: str):
        """
        Delete a document from the search indexes.
        
        Args:
            doc_id: Document ID to delete
        """
        try:
            # Delete from vector store
            self.vector_store.delete_documents([doc_id])
            
            # Delete from BM25 index
            if doc_id in self.bm25_ids:
                idx = self.bm25_ids.index(doc_id)
                self.bm25_ids.pop(idx)
                self.bm25_documents.pop(idx)
                self.bm25_metadatas.pop(idx)
                self._build_bm25_index()
            
            logger.info(f"Deleted document: {doc_id}")
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            raise
    
    def reset(self):
        """Clear all documents from the search engine."""
        try:
            # Reset vector store
            self.vector_store.reset_index()
            
            # Reset BM25 index
            self.bm25_documents = []
            self.bm25_ids = []
            self.bm25_metadatas = []
            self.bm25_index = None
            
            logger.info("Reset search engine")
        except Exception as e:
            logger.error(f"Error resetting search engine: {e}")
            raise


# Global search engine instance
search_engine = HybridSearchEngine()
