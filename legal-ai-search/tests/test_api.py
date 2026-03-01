"""
Example test suite for AI Legal Research Assistant.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data


def test_upload_document(client):
    """Test document upload."""
    response = client.post(
        "/api/v1/documents/upload",
        json={
            "filename": "test_case.txt",
            "content": "This is a test legal document about contract law.",
            "metadata": {"category": "contract_law"}
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "doc_id" in data
    assert data["filename"] == "test_case.txt"


def test_list_documents(client):
    """Test listing documents."""
    response = client.get("/api/v1/documents")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_search_query(client):
    """Test search endpoint."""
    # First upload a document
    client.post(
        "/api/v1/documents/upload",
        json={
            "filename": "test_search.txt",
            "content": "Contract breach occurs when one party fails to perform their obligations.",
            "metadata": {}
        }
    )
    
    # Then search
    response = client.post(
        "/api/v1/search",
        json={
            "query": "What is contract breach?",
            "top_k": 3,
            "include_citations": True
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "citations" in data
    assert "search_time_ms" in data


def test_summarization(client):
    """Test summarization endpoint."""
    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "This is a legal case about property rights. The plaintiff claims ownership based on adverse possession. The court ruled in favor of the defendant.",
            "summary_type": "brief"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "processing_time_ms" in data


def test_query_history(client):
    """Test query history endpoint."""
    response = client.get("/api/v1/history?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert "entries" in data
    assert "total_count" in data
    assert "page" in data


def test_metrics(client):
    """Test metrics endpoint."""
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data


def test_stats(client):
    """Test statistics endpoint."""
    response = client.get("/api/v1/stats")
    assert response.status_code == 200
    data = response.json()
    assert "documents" in data
    assert "query_history" in data
    assert "system" in data


def test_invalid_search_query(client):
    """Test search with invalid query."""
    response = client.post(
        "/api/v1/search",
        json={
            "query": "",  # Empty query
            "top_k": 3
        }
    )
    assert response.status_code == 422  # Validation error


def test_invalid_summary_request(client):
    """Test summarization with no input."""
    response = client.post(
        "/api/v1/summarize",
        json={
            "summary_type": "brief"
            # No doc_id or text provided
        }
    )
    assert response.status_code == 400


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
