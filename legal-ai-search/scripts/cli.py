"""
Command-line interface for AI Legal Research Assistant.
"""

import sys
import argparse
import json
from pathlib import Path
from typing import Optional

import requests


class LegalAssistantCLI:
    """CLI client for the Legal Research Assistant."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize CLI client."""
        self.base_url = base_url.rstrip("/")
        self.api_url = f"{self.base_url}/api/v1"
    
    def health_check(self) -> dict:
        """Check system health."""
        response = requests.get(f"{self.api_url}/health")
        response.raise_for_status()
        return response.json()
    
    def upload_document(self, file_path: str, metadata: Optional[dict] = None) -> dict:
        """Upload a document."""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        content = path.read_text(encoding='utf-8')
        
        data = {
            "filename": path.name,
            "content": content,
            "metadata": metadata or {}
        }
        
        response = requests.post(f"{self.api_url}/documents/upload", json=data)
        response.raise_for_status()
        return response.json()
    
    def search(self, query: str, top_k: int = 5, include_citations: bool = True) -> dict:
        """Search legal documents."""
        data = {
            "query": query,
            "top_k": top_k,
            "include_citations": include_citations
        }
        
        response = requests.post(f"{self.api_url}/search", json=data)
        response.raise_for_status()
        return response.json()
    
    def summarize(self, text: Optional[str] = None, doc_id: Optional[str] = None,
                 summary_type: str = "comprehensive") -> dict:
        """Summarize text or document."""
        data = {
            "summary_type": summary_type
        }
        
        if text:
            data["text"] = text
        elif doc_id:
            data["doc_id"] = doc_id
        else:
            raise ValueError("Either text or doc_id must be provided")
        
        response = requests.post(f"{self.api_url}/summarize", json=data)
        response.raise_for_status()
        return response.json()
    
    def get_history(self, page: int = 1, page_size: int = 10) -> dict:
        """Get query history."""
        response = requests.get(
            f"{self.api_url}/history",
            params={"page": page, "page_size": page_size}
        )
        response.raise_for_status()
        return response.json()
    
    def get_stats(self) -> dict:
        """Get system statistics."""
        response = requests.get(f"{self.api_url}/stats")
        response.raise_for_status()
        return response.json()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AI Legal Research Assistant CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Base URL of the API server"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Health check command
    subparsers.add_parser("health", help="Check system health")
    
    # Upload command
    upload_parser = subparsers.add_parser("upload", help="Upload a document")
    upload_parser.add_argument("file", help="Path to document file")
    upload_parser.add_argument("--metadata", help="JSON metadata")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search legal documents")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--top-k", type=int, default=5, help="Number of results")
    search_parser.add_argument("--no-citations", action="store_true", help="Exclude citations")
    
    # Summarize command
    summarize_parser = subparsers.add_parser("summarize", help="Summarize text or document")
    summarize_parser.add_argument("--text", help="Text to summarize")
    summarize_parser.add_argument("--doc-id", help="Document ID to summarize")
    summarize_parser.add_argument(
        "--type",
        choices=["brief", "comprehensive", "key_points"],
        default="comprehensive",
        help="Summary type"
    )
    
    # History command
    history_parser = subparsers.add_parser("history", help="View query history")
    history_parser.add_argument("--page", type=int, default=1, help="Page number")
    history_parser.add_argument("--page-size", type=int, default=10, help="Page size")
    
    # Stats command
    subparsers.add_parser("stats", help="View system statistics")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize client
    client = LegalAssistantCLI(base_url=args.url)
    
    try:
        # Execute command
        if args.command == "health":
            result = client.health_check()
            print(f"Status: {result['status']}")
            print(f"Version: {result['version']}")
            print(f"Documents Indexed: {result['documents_indexed']}")
            print(f"Total Queries: {result['total_queries']}")
        
        elif args.command == "upload":
            metadata = json.loads(args.metadata) if args.metadata else None
            result = client.upload_document(args.file, metadata)
            print(f"✓ Document uploaded successfully")
            print(f"  Document ID: {result['doc_id']}")
            print(f"  Filename: {result['filename']}")
            print(f"  Chunks: {result['num_chunks']}")
            print(f"  Size: {result['size_bytes']} bytes")
        
        elif args.command == "search":
            result = client.search(
                args.query,
                top_k=args.top_k,
                include_citations=not args.no_citations
            )
            print(f"\n📋 Query: {result['query']}")
            print(f"\n💡 Answer:\n{result['answer']}\n")
            print(f"⏱️  Search Time: {result['search_time_ms']:.2f}ms")
            
            if result['citations']:
                print(f"\n📚 Citations ({len(result['citations'])}):")
                for i, citation in enumerate(result['citations'], 1):
                    print(f"\n[{i}] {citation['doc_name']} (score: {citation['score']:.3f})")
                    print(f"    {citation['text'][:150]}...")
        
        elif args.command == "summarize":
            result = client.summarize(
                text=args.text,
                doc_id=args.doc_id,
                summary_type=args.type
            )
            print(f"\n📝 Summary:\n{result['summary']}\n")
            
            if result['key_points']:
                print("🔑 Key Points:")
                for point in result['key_points']:
                    print(f"  • {point}")
            
            if result['entities']:
                print(f"\n👥 Entities: {', '.join(result['entities'][:10])}")
            
            print(f"\n⏱️  Processing Time: {result['processing_time_ms']:.2f}ms")
        
        elif args.command == "history":
            result = client.get_history(page=args.page, page_size=args.page_size)
            print(f"\n📊 Query History (Page {result['page']}, Total: {result['total_count']})\n")
            
            for entry in result['entries']:
                print(f"[{entry['id']}] {entry['timestamp']}")
                print(f"    Q: {entry['query'][:80]}...")
                print(f"    A: {entry['answer'][:80]}...")
                print(f"    Time: {entry['response_time_ms']:.2f}ms, Citations: {entry['num_citations']}\n")
        
        elif args.command == "stats":
            result = client.get_stats()
            print("\n📊 System Statistics\n")
            print("Documents:")
            print(f"  Total: {result['documents']['total_documents']}")
            print(f"  Vector Index: {result['documents']['vector_index_size']}")
            print(f"  BM25 Index: {result['documents']['bm25_index_size']}")
            
            print("\nQuery History:")
            print(f"  Total Queries: {result['query_history']['total_queries']}")
            print(f"  Avg Response Time: {result['query_history']['avg_response_time_ms']:.2f}ms")
            print(f"  Avg Citations: {result['query_history']['avg_citations']:.2f}")
            
            print("\nSystem:")
            print(f"  Model: {result['system'].get('gemini_model', 'N/A')}")
            print(f"  Embedding: {result['system']['embedding_model']}")
            print(f"  Vector Weight: {result['system']['vector_weight']}")
            print(f"  Keyword Weight: {result['system']['keyword_weight']}")
    
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Cannot connect to server at {args.url}")
        print("   Make sure the server is running.")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"   Response: {e.response.text}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
