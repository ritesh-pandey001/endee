"""
API routes for the AI Legal Research Assistant.
"""

import time
from typing import List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from fastapi.responses import JSONResponse
import google.generativeai as genai

from app.models.schemas import (
    DocumentUploadRequest, DocumentMetadata, SearchQuery, SearchResult,
    SummarizationRequest, SummaryResult, QueryHistoryResponse,
    PerformanceMetrics, HealthCheckResponse, ErrorResponse, Citation
)
from services.hybrid_search import search_engine
from services.document_processor import document_processor
from services.summarization import summarization_service
from services.citation_manager import citation_manager
from services.query_history import query_history_service
from services.llm_service import llm_service
from utils.performance import performance_tracker, RequestTimer
from app.core.config import settings
from app.core.logging_config import logger


router = APIRouter()


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint.
    """
    try:
        stats = search_engine.get_collection_stats()
        history_stats = query_history_service.get_statistics()
        
        return HealthCheckResponse(
            status="healthy",
            version=settings.api_version,
            vector_db_status="connected",
            documents_indexed=stats.get("total_documents", 0),
            total_queries=history_stats.get("total_queries", 0)
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@router.post("/documents/upload", response_model=DocumentMetadata)
async def upload_document(request: DocumentUploadRequest):
    """
    Upload and index a document.
    """
    with RequestTimer("document_upload"):
        try:
            result = document_processor.upload_document(
                filename=request.filename,
                content=request.content,
                metadata=request.metadata
            )
            
            return DocumentMetadata(
                doc_id=result["doc_id"],
                filename=result["filename"],
                upload_date=result["upload_date"],
                num_chunks=result["num_chunks"],
                size_bytes=result["size_bytes"],
                metadata=result["metadata"]
            )
        except Exception as e:
            logger.error(f"Error uploading document: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents", response_model=List[str])
async def list_documents():
    """
    List all indexed documents.
    """
    try:
        return document_processor.list_documents()
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{doc_id}")
async def get_document(doc_id: str):
    """
    Retrieve a document by ID.
    """
    try:
        content = document_processor.get_document(doc_id)
        if not content:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {"doc_id": doc_id, "content": content}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=SearchResult)
async def search(request: SearchQuery):
    """
    Search legal documents with hybrid search and get AI-generated answer with citations.
    """
    start_time = time.time()
    
    with RequestTimer("search"):
        try:
            # Perform hybrid search
            search_results = search_engine.hybrid_search(
                query=request.query,
                top_k=request.top_k or settings.top_k_results
            )
            
            if not search_results:
                return SearchResult(
                    query=request.query,
                    answer="No relevant documents found for your query.",
                    citations=[],
                    search_time_ms=(time.time() - start_time) * 1000,
                    model_used=settings.gemini_model
                )
            
            # Create citations
            citations = []
            if request.include_citations:
                citations = citation_manager.create_citations_from_results(
                    search_results,
                    top_k=request.top_k or settings.top_k_results
                )
            
            # Generate AI answer using Google Gemini
            genai.configure(api_key=settings.gemini_api_key)
            model = genai.GenerativeModel(settings.gemini_model)
            
            # Prepare context from search results
            context = "\n\n".join([
                f"[Source {i+1}]\n{result['text']}"
                for i, result in enumerate(search_results[:5])
            ])
            
            prompt = f"""You are a legal research assistant. Based on the following sources, provide a comprehensive answer to the query.

Query: {request.query}

Sources:
{context}

Provide a well-structured answer that:
1. Directly addresses the query
2. Synthesizes information from multiple sources
3. Maintains legal accuracy
4. References sources using [1], [2], etc. markers

Answer:"""
            
            response = model.generate_content(prompt)
            
            answer = response.text.strip()
            
            search_time_ms = (time.time() - start_time) * 1000
            
            # Save to query history
            query_history_service.add_query(
                query=request.query,
                answer=answer,
                response_time_ms=search_time_ms,
                num_citations=len(citations)
            )
            
            return SearchResult(
                query=request.query,
                answer=answer,
                citations=citations,
                search_time_ms=search_time_ms,
                model_used=settings.gemini_model
            )
            
        except Exception as e:
            logger.error(f"Error in search: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.post("/summarize", response_model=SummaryResult)
async def summarize(request: SummarizationRequest):
    """
    Summarize a legal document or text.
    """
    with RequestTimer("summarization"):
        try:
            if request.doc_id:
                result = summarization_service.summarize_document(
                    doc_id=request.doc_id,
                    summary_type=request.summary_type
                )
            elif request.text:
                result = summarization_service.summarize_text(
                    text=request.text,
                    summary_type=request.summary_type
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Either doc_id or text must be provided"
                )
            
            return SummaryResult(**result)
            
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            logger.error(f"Error in summarization: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=QueryHistoryResponse)
async def get_query_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: Optional[str] = None
):
    """
    Get query history with pagination.
    """
    try:
        history = query_history_service.get_paginated_history(
            page=page,
            page_size=page_size,
            user_id=user_id
        )
        
        return QueryHistoryResponse(
            entries=history["entries"],
            total_count=history["total_count"],
            page=history["page"],
            page_size=history["page_size"]
        )
    except Exception as e:
        logger.error(f"Error retrieving history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/search")
async def search_history(query: str = Query(..., min_length=1)):
    """
    Search query history.
    """
    try:
        results = query_history_service.search_queries(query, limit=20)
        return {"results": results}
    except Exception as e:
        logger.error(f"Error searching history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_metrics(operation: Optional[str] = None):
    """
    Get performance metrics.
    """
    try:
        metrics = performance_tracker.get_metrics(operation)
        return {"metrics": metrics}
    except Exception as e:
        logger.error(f"Error retrieving metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_statistics():
    """
    Get system statistics.
    """
    try:
        collection_stats = search_engine.get_collection_stats()
        history_stats = query_history_service.get_statistics()
        
        return {
            "documents": collection_stats,
            "query_history": history_stats,
            "system": {
                "gemini_model": settings.gemini_model,
                "embedding_model": settings.embedding_model,
                "vector_weight": settings.vector_weight,
                "keyword_weight": settings.keyword_weight
            }
        }
    except Exception as e:
        logger.error(f"Error retrieving statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/history/clear")
async def clear_history(user_id: Optional[str] = None):
    """
    Clear query history.
    """
    try:
        query_history_service.clear_history(user_id)
        return {"message": "History cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Simplified endpoints for frontend integration

@router.post("/upload")
async def upload(request: DocumentUploadRequest):
    """
    Simplified document upload endpoint for frontend.
    Upload a legal document and index it for search.
    Returns document metadata.
    """
    with RequestTimer("upload"):
        try:
            result = document_processor.upload_document(
                filename=request.filename,
                content=request.content,
                metadata=request.metadata
            )
            
            return {
                "success": True,
                "doc_id": result["doc_id"],
                "filename": result["filename"],
                "num_chunks": result["num_chunks"],
                "message": f"Successfully uploaded {result['filename']} ({result['num_chunks']} chunks)"
            }
            
        except Exception as e:
            logger.error(f"Error in /upload: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.post("/ask")
async def ask(request: SearchQuery):
    """
    Simplified question-answering endpoint for frontend.
    Ask a question about uploaded documents and get an AI-generated answer with sources.
    """
    start_time = time.time()
    
    with RequestTimer("ask"):
        try:
            # Search for relevant documents
            search_results = search_engine.hybrid_search(
                query=request.query,
                top_k=request.top_k or 5
            )
            
            if not search_results:
                return {
                    "success": True,
                    "question": request.query,
                    "answer": "I couldn't find any relevant documents to answer your question. Please upload some legal documents first.",
                    "sources": [],
                    "search_time_ms": (time.time() - start_time) * 1000
                }
            
            # Format documents for LLM
            context_documents = []
            for result in search_results:
                context_documents.append({
                    "text": result.get("text", ""),
                    "metadata": result.get("metadata", {})
                })
            
            # Generate answer using LLM service
            answer = llm_service.generate_answer(
                question=request.query,
                context_documents=context_documents
            )
            
            # Format sources for frontend
            sources = []
            for i, result in enumerate(search_results, 1):
                metadata = result.get("metadata", {})
                sources.append({
                    "number": i,
                    "filename": metadata.get("filename", f"Document {i}"),
                    "score": result.get("score", 0.0),
                    "text": result.get("text", "")[:300] + "..."  # First 300 chars
                })
            
            search_time_ms = (time.time() - start_time) * 1000
            
            # Save to query history
            query_history_service.add_query(
                query=request.query,
                answer=answer,
                response_time_ms=search_time_ms,
                num_citations=len(sources)
            )
            
            return {
                "success": True,
                "question": request.query,
                "answer": answer,
                "sources": sources,
                "search_time_ms": round(search_time_ms, 2)
            }
            
        except Exception as e:
            logger.error(f"Error in /ask: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/clear")
async def clear_all_documents():
    """
    Clear all documents from the system.
    Removes all uploaded files, clears vector database, and resets search engine.
    """
    try:
        # Clear documents from processor
        result = document_processor.clear_all_documents()
        
        # Reset search engine
        search_engine.reset()
        
        logger.info("All documents cleared successfully")
        
        return {
            "success": True,
            "message": "All documents cleared successfully",
            "files_deleted": result.get("files_deleted", 0)
        }
        
    except Exception as e:
        logger.error(f"Error clearing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))
