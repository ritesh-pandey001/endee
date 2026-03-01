"""
Query history service for tracking user queries and results.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from contextlib import contextmanager

from app.core.config import settings
from app.core.logging_config import logger
from app.models.schemas import QueryHistoryEntry


class QueryHistoryService:
    """
    Service for storing and retrieving query history.
    """
    
    def __init__(self):
        """Initialize query history service with SQLite database."""
        self.db_path = Path(settings.query_history_db)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS query_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    response_time_ms REAL NOT NULL,
                    num_citations INTEGER DEFAULT 0,
                    user_id TEXT,
                    session_id TEXT,
                    metadata TEXT
                )
            """)
            
            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON query_history(timestamp DESC)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_id 
                ON query_history(user_id)
            """)
            
            conn.commit()
            logger.info("Query history database initialized")
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def add_query(self, query: str, answer: str, response_time_ms: float,
                  num_citations: int = 0, user_id: Optional[str] = None,
                  session_id: Optional[str] = None,
                  metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        Add a query to history.
        
        Args:
            query: User query
            answer: System answer
            response_time_ms: Response time in milliseconds
            num_citations: Number of citations provided
            user_id: Optional user ID
            session_id: Optional session ID
            metadata: Optional metadata dictionary
            
        Returns:
            Query ID
        """
        import json
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO query_history 
                (query, answer, timestamp, response_time_ms, num_citations, 
                 user_id, session_id, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                query,
                answer,
                datetime.utcnow(),
                response_time_ms,
                num_citations,
                user_id,
                session_id,
                json.dumps(metadata) if metadata else None
            ))
            conn.commit()
            query_id = cursor.lastrowid
            
        logger.info(f"Added query to history: ID {query_id}")
        return query_id
    
    def get_query(self, query_id: int) -> Optional[QueryHistoryEntry]:
        """
        Get a specific query by ID.
        
        Args:
            query_id: Query ID
            
        Returns:
            Query history entry or None
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, query, answer, timestamp, response_time_ms, num_citations
                FROM query_history
                WHERE id = ?
            """, (query_id,))
            
            row = cursor.fetchone()
            if row:
                return QueryHistoryEntry(
                    id=row["id"],
                    query=row["query"],
                    answer=row["answer"],
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    response_time_ms=row["response_time_ms"],
                    num_citations=row["num_citations"]
                )
        return None
    
    def get_recent_queries(self, limit: int = 10, 
                          user_id: Optional[str] = None) -> List[QueryHistoryEntry]:
        """
        Get recent queries.
        
        Args:
            limit: Maximum number of queries to return
            user_id: Optional filter by user ID
            
        Returns:
            List of query history entries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if user_id:
                cursor.execute("""
                    SELECT id, query, answer, timestamp, response_time_ms, num_citations
                    FROM query_history
                    WHERE user_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (user_id, limit))
            else:
                cursor.execute("""
                    SELECT id, query, answer, timestamp, response_time_ms, num_citations
                    FROM query_history
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (limit,))
            
            entries = []
            for row in cursor.fetchall():
                entries.append(QueryHistoryEntry(
                    id=row["id"],
                    query=row["query"],
                    answer=row["answer"],
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    response_time_ms=row["response_time_ms"],
                    num_citations=row["num_citations"]
                ))
            
            return entries
    
    def search_queries(self, search_term: str, limit: int = 10) -> List[QueryHistoryEntry]:
        """
        Search queries by text.
        
        Args:
            search_term: Search term
            limit: Maximum number of results
            
        Returns:
            List of matching query entries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, query, answer, timestamp, response_time_ms, num_citations
                FROM query_history
                WHERE query LIKE ? OR answer LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (f"%{search_term}%", f"%{search_term}%", limit))
            
            entries = []
            for row in cursor.fetchall():
                entries.append(QueryHistoryEntry(
                    id=row["id"],
                    query=row["query"],
                    answer=row["answer"],
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    response_time_ms=row["response_time_ms"],
                    num_citations=row["num_citations"]
                ))
            
            return entries
    
    def get_paginated_history(self, page: int = 1, page_size: int = 20,
                             user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get paginated query history.
        
        Args:
            page: Page number (1-indexed)
            page_size: Number of entries per page
            user_id: Optional filter by user ID
            
        Returns:
            Dictionary with entries and pagination info
        """
        offset = (page - 1) * page_size
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get total count
            if user_id:
                cursor.execute("SELECT COUNT(*) as count FROM query_history WHERE user_id = ?", (user_id,))
            else:
                cursor.execute("SELECT COUNT(*) as count FROM query_history")
            total_count = cursor.fetchone()["count"]
            
            # Get page of entries
            if user_id:
                cursor.execute("""
                    SELECT id, query, answer, timestamp, response_time_ms, num_citations
                    FROM query_history
                    WHERE user_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ? OFFSET ?
                """, (user_id, page_size, offset))
            else:
                cursor.execute("""
                    SELECT id, query, answer, timestamp, response_time_ms, num_citations
                    FROM query_history
                    ORDER BY timestamp DESC
                    LIMIT ? OFFSET ?
                """, (page_size, offset))
            
            entries = []
            for row in cursor.fetchall():
                entries.append(QueryHistoryEntry(
                    id=row["id"],
                    query=row["query"],
                    answer=row["answer"],
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    response_time_ms=row["response_time_ms"],
                    num_citations=row["num_citations"]
                ))
            
            return {
                "entries": entries,
                "total_count": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": (total_count + page_size - 1) // page_size
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get query history statistics.
        
        Returns:
            Dictionary with statistics
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_queries,
                    AVG(response_time_ms) as avg_response_time,
                    MIN(response_time_ms) as min_response_time,
                    MAX(response_time_ms) as max_response_time,
                    AVG(num_citations) as avg_citations
                FROM query_history
            """)
            
            row = cursor.fetchone()
            
            return {
                "total_queries": row["total_queries"] or 0,
                "avg_response_time_ms": row["avg_response_time"] or 0,
                "min_response_time_ms": row["min_response_time"] or 0,
                "max_response_time_ms": row["max_response_time"] or 0,
                "avg_citations": row["avg_citations"] or 0
            }
    
    def clear_history(self, user_id: Optional[str] = None):
        """
        Clear query history.
        
        Args:
            user_id: Optional - clear only for specific user
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if user_id:
                cursor.execute("DELETE FROM query_history WHERE user_id = ?", (user_id,))
            else:
                cursor.execute("DELETE FROM query_history")
            conn.commit()
            
        logger.info(f"Cleared query history{f' for user {user_id}' if user_id else ''}")


# Global query history service instance
query_history_service = QueryHistoryService()
