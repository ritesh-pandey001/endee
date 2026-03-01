"""
Pydantic models for request/response schemas.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class DocumentUploadRequest(BaseModel):
    """Schema for document upload request."""
    filename: str
    content: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class DocumentMetadata(BaseModel):
    """Schema for document metadata."""
    doc_id: str
    filename: str
    upload_date: datetime
    num_chunks: int
    size_bytes: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SearchQuery(BaseModel):
    """Schema for search query request."""
    query: str = Field(..., min_length=1, max_length=1000)
    top_k: Optional[int] = Field(default=5, ge=1, le=20)
    use_hybrid: Optional[bool] = True
    include_citations: Optional[bool] = True


class Citation(BaseModel):
    """Schema for source citation."""
    doc_id: str
    doc_name: str
    chunk_id: str
    text: str
    score: float
    page_number: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SearchResult(BaseModel):
    """Schema for search result."""
    query: str
    answer: str
    citations: List[Citation]
    search_time_ms: float
    model_used: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SummarizationRequest(BaseModel):
    """Schema for case summarization request."""
    doc_id: Optional[str] = None
    text: Optional[str] = None
    summary_type: str = Field(default="comprehensive", pattern="^(brief|comprehensive|key_points)$")


class SummaryResult(BaseModel):
    """Schema for summarization result."""
    summary: str
    key_points: List[str]
    entities: List[str]
    processing_time_ms: float
    word_count: int


class QueryHistoryEntry(BaseModel):
    """Schema for query history entry."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    query: str
    answer: str
    timestamp: datetime
    response_time_ms: float
    num_citations: int


class QueryHistoryResponse(BaseModel):
    """Schema for query history response."""
    entries: List[QueryHistoryEntry]
    total_count: int
    page: int
    page_size: int


class PerformanceMetrics(BaseModel):
    """Schema for performance metrics."""
    endpoint: str
    avg_response_time_ms: float
    min_response_time_ms: float
    max_response_time_ms: float
    total_requests: int
    success_rate: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthCheckResponse(BaseModel):
    """Schema for health check response."""
    status: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    vector_db_status: str
    documents_indexed: int
    total_queries: int


class ErrorResponse(BaseModel):
    """Schema for error response."""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
