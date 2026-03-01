"""
Endee Vector Store using Official Python SDK.

This module provides vector database operations using the official Endee SDK:
- Index creation and management
- Document embedding storage and retrieval
- Semantic similarity search
- Metadata management

Replaces the legacy REST API client with the official SDK for better performance
and reliability.
"""

from typing import List, Dict, Any, Optional

try:
    from endee import Endee, Precision
    ENDEE_AVAILABLE = True
except ImportError:
    ENDEE_AVAILABLE = False
    Endee = None
    Precision = None

from app.core.config import settings
from app.core.logging_config import logger


class EndeeVectorStore:
    """
    Vector store implementation using the official Endee Python SDK.
    
    Provides high-performance vector storage and similarity search for legal documents.
    Uses INT8 precision for optimal storage efficiency while maintaining search quality.
    """
    
    def __init__(self, index_name: str = "legal_documents_index", dimension: Optional[int] = None):
        """
        Initialize Endee Vector Store with official SDK.
        
        Args:
            index_name: Name of the vector index
            dimension: Embedding dimension (auto-detected from first embedding if None)
        """
        self.index_name = index_name
        self.dimension = dimension
        self.index = None
        self.use_fallback = False
        
        # In-memory fallback for when Endee server is not available
        self.fallback_vectors = []
        self.fallback_ids = []
        self.fallback_metadatas = []
        
        if not ENDEE_AVAILABLE:
            logger.warning("Endee SDK not installed. Using in-memory fallback mode.")
            self.client = None
            self.use_fallback = True
            return
        
        try:
            self.client = Endee()
            
            # Configure Endee server URL from settings
            if settings.endee_url:
                self.client.set_base_url(settings.endee_url)
                logger.info(f"Configured Endee client with base URL: {settings.endee_url}")
            
            logger.info(f"Initialized Endee Vector Store (SDK) with index: {index_name}")
            
        except Exception as e:
            logger.warning(f"Could not connect to Endee server: {e}. Using in-memory fallback.")
            self.client = None
            self.use_fallback = True
    
    def initialize_index(self, dimension: int):
        """
        Create or connect to an Endee index with the official SDK.
        
        Args:
            dimension: Vector embedding dimension
        """
        if self.use_fallback:
            self.dimension = dimension
            logger.info(f"Using in-memory fallback with dimension {dimension}")
            return
            
        try:
            # Try to get existing index first
            try:
                self.index = self.client.get_index(name=self.index_name)
                logger.info(f"Connected to existing Endee index: {self.index_name}")
                
                # Verify dimension matches
                index_info = self.index.describe()
                if index_info.get("dimension") != dimension:
                    logger.warning(
                        f"Index dimension mismatch: expected {dimension}, "
                        f"got {index_info.get('dimension')}. Using existing index."
                    )
                self.dimension = index_info.get("dimension", dimension)
                
            except Exception:
                # Index doesn't exist, create new one
                logger.info(f"Creating new Endee index: {self.index_name} with dimension {dimension}")
                self.client.create_index(
                    name=self.index_name,
                    dimension=dimension,
                    space_type="cosine",
                    precision=Precision.INT8
                )
                self.index = self.client.get_index(name=self.index_name)
                self.dimension = dimension
                logger.info(f"Successfully created Endee index with {dimension}D vectors")
                
        except Exception as e:
            logger.error(f"Error initializing Endee index: {e}")
            raise
    
    def auto_initialize(self, sample_embedding: List[float]):
        """
        Auto-initialize index by detecting dimension from a sample embedding.
        
        Args:
            sample_embedding: Sample embedding vector to detect dimension
        """
        detected_dimension = len(sample_embedding)
        logger.info(f"Auto-detected embedding dimension: {detected_dimension}")
        self.initialize_index(detected_dimension)
    
    def upsert_documents(
        self,
        doc_ids: List[str],
        vectors: List[List[float]],
        metadatas: List[Dict[str, Any]]
    ):
        """
        Insert or update document embeddings in Endee.
        
        Args:
            doc_ids: List of unique document IDs
            vectors: List of embedding vectors
            metadatas: List of metadata dictionaries (includes text and document info)
        """
        try:
            # Auto-initialize index if not already done
            if self.index is None and not self.use_fallback:
                if vectors:
                    self.auto_initialize(vectors[0])
                else:
                    raise ValueError("Cannot initialize index without embeddings")
            
            if self.use_fallback:
                # Store in memory
                for doc_id, vector, metadata in zip(doc_ids, vectors, metadatas):
                    # Check if ID already exists
                    if doc_id in self.fallback_ids:
                        idx = self.fallback_ids.index(doc_id)
                        self.fallback_vectors[idx] = vector
                        self.fallback_metadatas[idx] = metadata
                    else:
                        self.fallback_ids.append(doc_id)
                        self.fallback_vectors.append(vector)
                        self.fallback_metadatas.append(metadata)
                
                logger.info(f"Upserted {len(doc_ids)} document embeddings to in-memory store")
                return
            
            # Prepare documents for upsert
            documents = []
            for doc_id, vector, metadata in zip(doc_ids, vectors, metadatas):
                documents.append({
                    "id": doc_id,
                    "vector": vector,
                    "meta": metadata
                })
            
            # Batch upsert to Endee
            self.index.upsert(documents)
            
            logger.info(f"Upserted {len(documents)} document embeddings to Endee")
            
        except Exception as e:
            logger.error(f"Error upserting documents to Endee: {e}")
            raise
    
    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filter_meta: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar document vectors in Endee.
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            filter_meta: Optional metadata filters
            
        Returns:
            List of search results with scores and metadata
        """
        try:
            if self.use_fallback:
                # Use in-memory cosine similarity search
                if not self.fallback_vectors:
                    logger.warning("No vectors in fallback store")
                    return []
                
                import numpy as np
                
                # Calculate cosine similarity
                query_norm = np.linalg.norm(query_vector)
                similarities = []
                
                for i, vec in enumerate(self.fallback_vectors):
                    vec_norm = np.linalg.norm(vec)
                    if query_norm > 0 and vec_norm > 0:
                        similarity = np.dot(query_vector, vec) / (query_norm * vec_norm)
                    else:
                        similarity = 0.0
                    
                    # Apply metadata filter if provided
                    if filter_meta:
                        metadata = self.fallback_metadatas[i]
                        matches = all(metadata.get(k) == v for k, v in filter_meta.items())
                        if not matches:
                            continue
                    
                    similarities.append((i, similarity))
                
                # Sort by similarity and get top_k
                similarities.sort(key=lambda x: x[1], reverse=True)
                top_results = similarities[:top_k]
                
                # Format results
                formatted_results = []
                for idx, score in top_results:
                    formatted_results.append({
                        "id": self.fallback_ids[idx],
                        "score": float(score),
                        "metadata": self.fallback_metadatas[idx],
                        "text": self.fallback_metadatas[idx].get("text", "")
                    })
                
                logger.info(f"Fallback search returned {len(formatted_results)} results")
                return formatted_results
            
            if self.index is None:
                logger.warning("Index not initialized, cannot perform search")
                return []
            
            # Perform similarity search
            query_params = {
                "vector": query_vector,
                "top_k": top_k
            }
            
            if filter_meta:
                query_params["filter"] = filter_meta
            
            results = self.index.query(**query_params)
            
            # Format results to match expected structure
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "id": result.get("id"),
                    "score": result.get("score", 0.0),
                    "metadata": result.get("meta", {}),
                    "text": result.get("meta", {}).get("text", "")
                })
            
            logger.info(f"Endee search returned {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching Endee: {e}")
            return []
    
    def get_all_documents(self) -> Dict[str, Any]:
        """
        Retrieve all documents from the index.
        
        Note: This is a convenience method for rebuilding BM25 index.
        For production with large datasets, implement pagination.
        
        Returns:
            Dictionary with document IDs, texts, and metadatas
        """
        try:
            if self.use_fallback:
                # Return all documents from in-memory store
                documents = [meta.get("text", "") for meta in self.fallback_metadatas]
                return {
                    "ids": self.fallback_ids.copy(),
                    "documents": documents,
                    "metadatas": self.fallback_metadatas.copy()
                }
            
            if self.index is None:
                logger.warning("Index not initialized")
                return {"ids": [], "documents": [], "metadatas": []}
            
            # Get index stats to check document count
            stats = self.index.describe()
            doc_count = stats.get("vector_count", 0)
            
            if doc_count == 0:
                return {"ids": [], "documents": [], "metadatas": []}
            
            # Fetch all vectors (with pagination for large collections)
            # Note: Endee SDK may have a fetch/list method - adjust based on actual SDK API
            # For now, we'll use a large dummy query to get documents
            # This is a workaround - check SDK docs for proper list_all method
            
            logger.info(f"Retrieved metadata for {doc_count} documents")
            
            # Placeholder: SDK may not support fetching all vectors without query
            # This might require a different approach or SDK method
            logger.warning(
                "get_all_documents is a placeholder. "
                "Endee SDK may require query-based retrieval. "
                "BM25 index building may need refactoring."
            )
            
            return {"ids": [], "documents": [], "metadatas": []}
            
        except Exception as e:
            logger.error(f"Error getting all documents: {e}")
            return {"ids": [], "documents": [], "metadatas": []}
    
    def delete_documents(self, doc_ids: List[str]):
        """
        Delete documents by IDs.
        
        Args:
            doc_ids: List of document IDs to delete
        """
        try:
            if self.use_fallback:
                # Delete from in-memory store
                for doc_id in doc_ids:
                    if doc_id in self.fallback_ids:
                        idx = self.fallback_ids.index(doc_id)
                        del self.fallback_ids[idx]
                        del self.fallback_vectors[idx]
                        del self.fallback_metadatas[idx]
                logger.info(f"Deleted {len(doc_ids)} documents from in-memory store")
                return
            
            if self.index is None:
                logger.warning("Index not initialized, cannot delete documents")
                return
            
            self.index.delete(ids=doc_ids)
            logger.info(f"Deleted {len(doc_ids)} documents from Endee")
            
        except Exception as e:
            logger.error(f"Error deleting documents from Endee: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get index statistics.
        
        Returns:
            Dictionary with index stats
        """
        try:
            if self.use_fallback:
                return {
                    "total_documents": len(self.fallback_ids),
                    "dimension": self.dimension or 0,
                    "metric": "cosine",
                    "mode": "in-memory-fallback"
                }
            
            if self.index is None:
                return {
                    "total_documents": 0,
                    "dimension": self.dimension or 0,
                    "metric": "cosine"
                }
            
            stats = self.index.describe()
            
            return {
                "total_documents": stats.get("vector_count", 0),
                "dimension": stats.get("dimension", self.dimension),
                "metric": stats.get("space_type", "cosine")
            }
            
        except Exception as e:
            logger.error(f"Error getting Endee stats: {e}")
            return {"total_documents": 0, "dimension": 0, "metric": "cosine"}
    
    def reset_index(self):
        """
        Delete and recreate the index.
        
        Warning: This will delete all stored vectors!
        """
        try:
            if self.index is None:
                logger.warning("Index not initialized, nothing to reset")
                return
            
            # Delete the index
            self.client.delete_index(name=self.index_name)
            logger.info(f"Deleted Endee index: {self.index_name}")
            
            # Reset state
            self.index = None
            
            logger.info("Index reset complete. Will be recreated on next upsert.")
            
        except Exception as e:
            logger.error(f"Error resetting Endee index: {e}")
            raise


# Global vector store instance (initialized on first use)
vector_store = EndeeVectorStore(
    index_name="legal_documents_index",
    dimension=None  # Auto-detect from first embedding
)
