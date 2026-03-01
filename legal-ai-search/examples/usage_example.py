"""
Example usage script for AI Legal Research Assistant.
Demonstrates how to interact with the API programmatically.
"""

import requests
import json
from pathlib import Path


# Configuration
BASE_URL = "http://localhost:8000/api/v1"

# Sample legal text
SAMPLE_LEGAL_TEXT = """
SUPREME COURT OF THE UNITED STATES

Smith v. Jones, 123 U.S. 456 (2023)

FACTS:
The plaintiff, John Smith, entered into a contract with defendant Jane Jones for the sale of property located at 123 Main Street. The contract specified that the defendant would purchase the property for $500,000, with closing scheduled for January 15, 2023. The defendant failed to perform their obligations under the contract and did not appear at the scheduled closing.

ISSUE:
Whether the defendant's failure to appear at closing constitutes a material breach of contract, entitling the plaintiff to damages.

HOLDING:
The Court holds that the defendant's failure to appear at the scheduled closing constitutes a material breach of contract. The defendant's obligations were clearly specified in the written agreement, and the failure to perform these obligations caused substantial harm to the plaintiff.

REASONING:
Under established contract law principles, a material breach occurs when one party fails to perform a substantial part of their contractual obligations. In this case, the defendant's complete failure to appear at closing and consummate the purchase constitutes such a material breach. The plaintiff is entitled to consequential and incidental damages resulting from this breach.

The Court applies the four-part test for material breach: (1) the breach defeated the benefit of the contract to the non-breaching party; (2) the breach was substantial; (3) the breaching party acted without good faith; and (4) the non-breaching party did not receive substantial benefit from the partial performance. All four elements are satisfied in this case.

JUDGMENT:
Judgment for the plaintiff. Defendant is liable for damages including lost profits, costs of maintaining the property during the delay, and reasonable attorney fees.
"""


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def upload_document_example():
    """Example: Upload a document."""
    print_section("1. UPLOADING A DOCUMENT")
    
    response = requests.post(
        f"{BASE_URL}/documents/upload",
        json={
            "filename": "smith_v_jones.txt",
            "content": SAMPLE_LEGAL_TEXT,
            "metadata": {
                "case_name": "Smith v. Jones",
                "citation": "123 U.S. 456",
                "year": 2023,
                "court": "Supreme Court",
                "subject": "Contract Law"
            }
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Document uploaded successfully!")
        print(f"  Document ID: {result['doc_id']}")
        print(f"  Filename: {result['filename']}")
        print(f"  Chunks Created: {result['num_chunks']}")
        print(f"  Size: {result['size_bytes']} bytes")
        return result['doc_id']
    else:
        print(f"✗ Upload failed: {response.text}")
        return None


def search_example():
    """Example: Search with citations."""
    print_section("2. SEARCHING WITH CITATIONS")
    
    query = "What constitutes a material breach of contract?"
    print(f"Query: {query}\n")
    
    response = requests.post(
        f"{BASE_URL}/search",
        json={
            "query": query,
            "top_k": 3,
            "include_citations": True
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"Answer:\n{result['answer']}\n")
        
        print(f"Search Time: {result['search_time_ms']:.2f}ms")
        print(f"Model Used: {result['model_used']}\n")
        
        if result['citations']:
            print(f"Citations ({len(result['citations'])}):")
            for i, citation in enumerate(result['citations'], 1):
                print(f"\n  [{i}] {citation['doc_name']}")
                print(f"      Relevance: {citation['score']:.3f}")
                print(f"      Text: {citation['text'][:150]}...")
    else:
        print(f"✗ Search failed: {response.text}")


def summarize_example():
    """Example: Summarize legal text."""
    print_section("3. SUMMARIZING A CASE")
    
    response = requests.post(
        f"{BASE_URL}/summarize",
        json={
            "text": SAMPLE_LEGAL_TEXT,
            "summary_type": "comprehensive"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"Summary:\n{result['summary']}\n")
        
        if result['key_points']:
            print("Key Points:")
            for i, point in enumerate(result['key_points'], 1):
                print(f"  {i}. {point}")
        
        if result['entities']:
            print(f"\nEntities Identified: {', '.join(result['entities'][:10])}")
        
        print(f"\nProcessing Time: {result['processing_time_ms']:.2f}ms")
        print(f"Word Count: {result['word_count']}")
    else:
        print(f"✗ Summarization failed: {response.text}")


def query_history_example():
    """Example: View query history."""
    print_section("4. QUERY HISTORY")
    
    response = requests.get(
        f"{BASE_URL}/history",
        params={"page": 1, "page_size": 5}
    )
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"Total Queries in History: {result['total_count']}")
        print(f"Showing Page {result['page']} of {result['total_count'] // result['page_size'] + 1}\n")
        
        for entry in result['entries']:
            print(f"[{entry['id']}] {entry['timestamp']}")
            print(f"  Query: {entry['query'][:70]}...")
            print(f"  Response Time: {entry['response_time_ms']:.2f}ms")
            print(f"  Citations: {entry['num_citations']}\n")
    else:
        print(f"✗ Failed to retrieve history: {response.text}")


def statistics_example():
    """Example: View system statistics."""
    print_section("5. SYSTEM STATISTICS")
    
    response = requests.get(f"{BASE_URL}/stats")
    
    if response.status_code == 200:
        result = response.json()
        
        print("Document Statistics:")
        docs = result['documents']
        print(f"  Total Documents: {docs['total_documents']}")
        print(f"  Vector Index Size: {docs['vector_index_size']}")
        print(f"  BM25 Index Size: {docs['bm25_index_size']}")
        
        print("\nQuery History Statistics:")
        history = result['query_history']
        print(f"  Total Queries: {history['total_queries']}")
        print(f"  Average Response Time: {history['avg_response_time_ms']:.2f}ms")
        print(f"  Min Response Time: {history['min_response_time_ms']:.2f}ms")
        print(f"  Max Response Time: {history['max_response_time_ms']:.2f}ms")
        print(f"  Average Citations per Query: {history['avg_citations']:.2f}")
        
        print("\nSystem Configuration:")
        system = result['system']
        print(f"  Gemini Model: {system.get('gemini_model', 'N/A')}")
        print(f"  Embedding Model: {system['embedding_model']}")
        print(f"  Vector Weight: {system['vector_weight']}")
        print(f"  Keyword Weight: {system['keyword_weight']}")
    else:
        print(f"✗ Failed to retrieve statistics: {response.text}")


def performance_metrics_example():
    """Example: View performance metrics."""
    print_section("6. PERFORMANCE METRICS")
    
    response = requests.get(f"{BASE_URL}/metrics")
    
    if response.status_code == 200:
        result = response.json()
        metrics = result['metrics']
        
        if metrics:
            print("Operation Performance Metrics:\n")
            for operation, stats in metrics.items():
                print(f"{operation}:")
                print(f"  Total Requests: {stats['total_requests']}")
                print(f"  Average Time: {stats['avg_response_time_ms']:.2f}ms")
                print(f"  Min Time: {stats['min_response_time_ms']:.2f}ms")
                print(f"  Max Time: {stats['max_response_time_ms']:.2f}ms")
                print(f"  Success Rate: {stats['success_rate']*100:.1f}%\n")
        else:
            print("No metrics available yet. Perform some operations first.")
    else:
        print(f"✗ Failed to retrieve metrics: {response.text}")


def health_check_example():
    """Example: Health check."""
    print_section("HEALTH CHECK")
    
    response = requests.get(f"{BASE_URL}/health")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Status: {result['status']}")
        print(f"Version: {result['version']}")
        print(f"Vector DB Status: {result['vector_db_status']}")
        print(f"Documents Indexed: {result['documents_indexed']}")
        print(f"Total Queries: {result['total_queries']}")
    else:
        print(f"✗ Health check failed: {response.text}")


def main():
    """Run all examples."""
    print("\n" + "="*80)
    print("  AI LEGAL RESEARCH ASSISTANT - USAGE EXAMPLES")
    print("="*80)
    print("\nMake sure the server is running at http://localhost:8000")
    input("\nPress Enter to continue...")
    
    try:
        # Check health first
        health_check_example()
        
        # Upload a document
        doc_id = upload_document_example()
        
        # Search with citations
        search_example()
        
        # Summarize case
        summarize_example()
        
        # View query history
        query_history_example()
        
        # View statistics
        statistics_example()
        
        # View performance metrics
        performance_metrics_example()
        
        print_section("EXAMPLES COMPLETED")
        print("✓ All examples executed successfully!")
        print("\nYou can now:")
        print("  • Access the API documentation at http://localhost:8000/docs")
        print("  • Use the CLI tool: python cli.py --help")
        print("  • Integrate the API into your own applications")
        
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Cannot connect to the server.")
        print("  Please make sure the server is running:")
        print("  python -m app.main")
    except Exception as e:
        print(f"\n✗ ERROR: {e}")


if __name__ == "__main__":
    main()
