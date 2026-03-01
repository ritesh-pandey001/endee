"""
Endee Vector Database Client for AI Legal Research Assistant.

⚠️ DEPRECATED: This REST API client is deprecated.
Please use services/vector_store.py with the official Endee Python SDK instead.

This module provides integration with Endee Vector Database for:
- Vector storage and retrieval
- Semantic similarity search
- Document indexing and management
"""

import os
from typing import List, Dict, Any, Optional
import requests

from app.core.logging_config import logger


class EndeeVectorDB:
    """
    Client for Endee Vector Database operations.
    
    Endee is a high-performance vector database optimized for semantic search
    and AI applications. It provides fast similarity search with HNSW indexing
    and supports large-scale document collections.
    """
    
    def __init__(self, api_key: str = None, collection_name: str = "legal_documents"):
        """
        Initialize Endee Vector Database client.
        
        Args:
            api_key: Endee API key (defaults to ENDEE_API_KEY environment variable)
            collection_name: Name of the vector collection
        """
        self.api_key = api_key or os.getenv("ENDEE_API_KEY")
        if not self.api_key:
            raise ValueError("Endee API key is required. Set ENDEE_API_KEY environment variable.")
        
        self.base_url = os.getenv("ENDEE_URL", "https://api.endee.io/v1")
        self.collection_name = collection_name
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Initialize collection
        self._ensure_collection_exists()
        logger.info(f"Endee Vector Database initialized with collection: {collection_name}")
    
    def _ensure_collection_exists(self):
        """Create collection if it doesn't exist."""
        try:
            # Check if collection exists
            response = requests.get(
                f"{self.base_url}/collections/{self.collection_name}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 404:
                # Create collection
                create_response = requests.post(
                    f"{self.base_url}/collections",
                    headers=self.headers,
                    json={
                        "name": self.collection_name,
                        "dimension": 768,  # Gemini text-embedding-004 dimension
                        "metric": "cosine",
                        "description": "Legal documents collection for AI research assistant"
                    },
                    timeout=10
                )
                create_response.raise_for_status()
                logger.info(f"Created new Endee collection: {self.collection_name}")
            elif response.status_code == 200:
                logger.info(f"Using existing Endee collection: {self.collection_name}")
            else:
                response.raise_for_status()
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error ensuring collection exists: {e}")
            raise
    
    def add_documents(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ):
        """
        Add documents to Endee vector database.
        
        Args:
            documents: List of document texts
            embeddings: List of embedding vectors
            metadatas: List of metadata dictionaries
            ids: List of document IDs
        """
        try:
            vectors = []
            for i, (doc_id, embedding, metadata, text) in enumerate(zip(ids, embeddings, metadatas, documents)):
                vectors.append({
                    "id": doc_id,
                    "vector": embedding,
                    "metadata": {
                        **metadata,
                        "text": text
                    }
                })
            
            # Batch insert vectors
            response = requests.post(
                f"{self.base_url}/collections/{self.collection_name}/vectors",
                headers=self.headers,
                json={"vectors": vectors},
                timeout=30
            )
            response.raise_for_status()
            
            logger.info(f"Added {len(vectors)} documents to Endee")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error adding documents to Endee: {e}")
            raise
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in Endee database.
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of search results with scores and metadata
        """
        try:
            payload = {
                "vector": query_embedding,
                "top_k": top_k
            }
            
            if filter_metadata:
                payload["filter"] = filter_metadata
            
            response = requests.post(
                f"{self.base_url}/collections/{self.collection_name}/search",
                headers=self.headers,
                json=payload,
                timeout=15
            )
            response.raise_for_status()
            
            results = response.json().get("results", [])
            
            # Format results to match expected structure
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "id": result["id"],
                    "score": result["score"],
                    "metadata": result["metadata"],
                    "text": result["metadata"].get("text", "")
                })
            
            logger.info(f"Endee search returned {len(formatted_results)} results")
            return formatted_results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching Endee: {e}")
            raise
    
    def get_all_documents(self) -> Dict[str, Any]:
        """
        Retrieve all documents from collection.
        
        Returns:
            Dictionary with document IDs, texts, and metadatas
        """
        try:
            response = requests.get(
                f"{self.base_url}/collections/{self.collection_name}/vectors",
                headers=self.headers,
                params={"limit": 10000},
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            vectors = data.get("vectors", [])
            
            # Format to match ChromaDB structure for compatibility
            return {
                "ids": [v["id"] for v in vectors],
                "documents": [v["metadata"].get("text", "") for v in vectors],
                "metadatas": [v["metadata"] for v in vectors]
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting all documents from Endee: {e}")
            return {"ids": [], "documents": [], "metadatas": []}
    
    def delete_documents(self, ids: List[str]):
        """
        Delete documents by IDs.
        
        Args:
            ids: List of document IDs to delete
        """
        try:
            response = requests.delete(
                f"{self.base_url}/collections/{self.collection_name}/vectors",
                headers=self.headers,
                json={"ids": ids},
                timeout=15
            )
            response.raise_for_status()
            logger.info(f"Deleted {len(ids)} documents from Endee")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error deleting documents from Endee: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get collection statistics.
        
        Returns:
            Dictionary with collection stats
        """
        try:
            response = requests.get(
                f"{self.base_url}/collections/{self.collection_name}/stats",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            
            stats = response.json()
            return {
                "total_documents": stats.get("vector_count", 0),
                "dimension": stats.get("dimension", 768),  # Gemini text-embedding-004
                "metric": stats.get("metric", "cosine")
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting Endee stats: {e}")
            return {"total_documents": 0, "dimension": 768, "metric": "cosine"}
    
    def reset_collection(self):
        """Delete all documents in collection."""
        try:
            response = requests.delete(
                f"{self.base_url}/collections/{self.collection_name}",
                headers=self.headers,
                timeout=15
            )
            response.raise_for_status()
            
            # Recreate collection
            self._ensure_collection_exists()
            logger.info(f"Reset Endee collection: {self.collection_name}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error resetting Endee collection: {e}")
            raise
