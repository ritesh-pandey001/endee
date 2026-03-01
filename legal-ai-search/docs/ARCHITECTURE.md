# AI Legal Research Assistant - System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │  Web UI  │  │   CLI    │  │  Python  │  │   REST   │      │
│  │ (Swagger)│  │   Tool   │  │  Client  │  │   API    │      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API LAYER (FastAPI)                         │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    API Routes                             │  │
│  │  /health  /search  /upload  /summarize  /history  /stats │  │
│  └───────────────────────┬──────────────────────────────────┘  │
│                          │                                       │
│  ┌───────────────────────┴──────────────────────────────────┐  │
│  │              Middleware & Authentication                  │  │
│  │      CORS | Logging | Performance Tracking | Validation  │  │
│  └───────────────────────┬──────────────────────────────────┘  │
└────────────────────────────┼────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SERVICE LAYER                               │
│                                                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │ Hybrid Search    │  │ Document         │  │ Summarization│ │
│  │ Engine           │  │ Processor        │  │ Service      │ │
│  │                  │  │                  │  │              │ │
│  │ • Vector Search  │  │ • PDF Extract    │  │ • GPT-4      │ │
│  │ • Keyword Search │  │ • DOCX Extract   │  │ • Entity     │ │
│  │ • Result Fusion  │  │ • Chunking       │  │ • Key Points │ │
│  └──────────────────┘  └──────────────────┘  └──────────────┘ │
│                                                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │ Citation         │  │ Query History    │  │ Performance  │ │
│  │ Manager          │  │ Service          │  │ Tracker      │ │
│  │                  │  │                  │  │              │ │
│  │ • Format         │  │ • SQLite Store   │  │ • Metrics    │ │
│  │ • Rank           │  │ • Pagination     │  │ • Logging    │ │
│  │ • Deduplicate    │  │ • Search History │  │ • Monitoring │ │
│  └──────────────────┘  └──────────────────┘  └──────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                  │
│                                                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │   Endee          │  │   SQLite         │  │ File Storage │ │
│  │   Vector DB      │  │   (History DB)   │  │ (Documents)  │ │
│  │   (Official SDK) │  │                  │  │              │ │
│  │ • Embeddings     │  │ • Query Log      │  │ • PDFs       │ │
│  │ • Similarity     │  │ • Metrics        │  │ • Text Files │ │
│  │ • HNSW Index     │  │ • User Data      │  │ • Metadata   │ │
│  │ • INT8 Precision │  │                  │  │              │ │
│  └──────────────────┘  └──────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   EXTERNAL SERVICES                              │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Gemini API                             │  │
│  │   • GPT-4 (Text Generation)                              │  │
│  │   • text-embedding-3-large (Vector Embeddings)           │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Hybrid Search Engine
**Purpose**: Combines vector and keyword search for optimal retrieval

**Components**:
- **Vector Search**: Uses Google Gemini embeddings + Endee Vector Database (Official SDK) for semantic search
- **Keyword Search**: BM25 algorithm for exact keyword matching
- **Result Fusion**: Weighted combination of both search methods

**Flow**:
```
Query → Generate Embedding → Vector Search (Endee)
     → Tokenize → Keyword Search (BM25)
     → Combine & Rank Results → Return Top K
```

### 2. Document Processor
**Purpose**: Handle document upload, extraction, and indexing

**Supported Formats**: PDF, DOCX, TXT

**Processing Pipeline**:
```
Upload → Extract Text → Chunk Text (with overlap)
      → Generate Embeddings → Index in Endee & BM25
      → Store Original → Return Metadata
```

**Chunking Strategy**:
- Sentence-based splitting for semantic boundaries
- Configurable size (default: 1000 chars)
- Overlap (default: 200 chars) to maintain context

### 3. Summarization Service
**Purpose**: Generate case summaries and extract key information

**Features**:
- Multiple summary types (brief, comprehensive, key points)
- Entity extraction (parties, courts, judges, case numbers)
- Key point identification

**Process**:
```
Document → GPT-4 Prompt → Generate Summary
        → Extract Entities → Extract Key Points
        → Format & Return
```

### 4. Citation Manager
**Purpose**: Track and format source citations

**Features**:
- Automatic citation generation
- Multiple formats (numbered, APA, Bluebook)
- Relevance scoring
- Deduplication

### 5. Query History Service
**Purpose**: Store and retrieve query history

**Storage**: SQLite database

**Schema**:
```sql
query_history (
    id INTEGER PRIMARY KEY,
    query TEXT,
    answer TEXT,
    timestamp DATETIME,
    response_time_ms REAL,
    num_citations INTEGER,
    user_id TEXT,
    session_id TEXT,
    metadata TEXT
)
```

### 6. Performance Tracker
**Purpose**: Monitor system performance

**Metrics Tracked**:
- Response times (min, max, avg)
- Request counts
- Success/failure rates
- Operation-level metrics

## Data Flow

### Search Request Flow
```
1. Client sends search query
2. API validates request
3. Hybrid Search Engine:
   a. Generates query embedding (Google Gemini)
   b. Performs vector search (Endee)
   c. Performs keyword search (BM25)
   d. Combines and ranks results
4. Citation Manager creates citations
5. Generate AI answer:
   a. Format context from results
   b. Call GPT-4 with context
   c. Parse and format response
6. Query History saves query
7. Performance Tracker logs metrics
8. Return structured response
```

### Document Upload Flow
```
1. Client uploads document
2. API validates file size/format
3. Document Processor:
   a. Extracts text (PDF/DOCX/TXT)
   b. Generates document ID
   c. Chunks text with overlap
   d. Generates embeddings for each chunk
4. Hybrid Search Engine:
   a. Adds to Endee (vector index)
   b. Rebuilds BM25 index
5. Store original document
6. Return metadata
```

## Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework
- **Pydantic**: Data validation and settings
- **Uvicorn**: ASGI server

### AI/ML
- **Google Gemini API**: gemini-1.5-flash for generation, text-embedding-004 for vectors
- **Endee Vector Database**: High-performance vector search with HNSW index
- **Rank-BM25**: Keyword search algorithm

### Storage
- **SQLite**: Query history and metadata
- **File System**: Document storage
- **Endee**: Vector embeddings

### Document Processing
- **PyPDF2**: PDF text extraction
- **python-docx**: DOCX processing

### Utilities
- **NumPy**: Numerical operations
- **Python-dotenv**: Environment management

## Configuration

### Key Settings
```python
# Search Weights
VECTOR_WEIGHT = 0.7    # 70% semantic
KEYWORD_WEIGHT = 0.3   # 30% keyword

# Document Processing
CHUNK_SIZE = 1000      # Characters per chunk
CHUNK_OVERLAP = 200    # Overlap for context

# Search
TOP_K_RESULTS = 5      # Results to return
SIMILARITY_THRESHOLD = 0.7  # Min score

# Google Gemini
GEMINI_MODEL = "gemini-1.5-flash"
EMBEDDING_MODEL = "text-embedding-3-large"
TEMPERATURE = 0.3      # Low for consistency
MAX_TOKENS = 2000
```

## Scalability Considerations

### Current Design
- **Single-server deployment**
- **Local file storage**
- **Embedded databases**

### Scaling Options

1. **Horizontal Scaling**:
   - Deploy multiple API servers behind load balancer
   - Share vector DB and documents via network storage
   - Use Endee's clustering capabilities for distributed search

2. **Database Scaling**:
   - Replace SQLite with PostgreSQL
   - Use Redis for caching
   - Implement connection pooling

3. **Storage Scaling**:
   - Use S3/Azure Blob for documents
   - Implement CDN for static content
   - Add document compression

4. **Performance Optimization**:
   - Add result caching (Redis)
   - Implement request batching
   - Use async processing for uploads
   - Add rate limiting

## Security Considerations

### Current Implementation
- Environment variable configuration
- Input validation via Pydantic
- CORS middleware

### Production Recommendations
1. **Authentication**: Add JWT or OAuth2
2. **Authorization**: Role-based access control
3. **Encryption**: HTTPS/TLS in production
4. **API Keys**: Rate limiting and key management
5. **Input Sanitization**: Additional validation
6. **Audit Logging**: Track all operations
7. **Secret Management**: Use vault services

## Monitoring & Observability

### Built-in Features
- Performance metrics per endpoint
- Query history with response times
- Application logging (file + console)
- Health check endpoint

### Production Additions
- **APM**: Application Performance Monitoring (New Relic, DataDog)
- **Logging**: Centralized logging (ELK Stack, Splunk)
- **Alerting**: Error rate, latency thresholds
- **Tracing**: Distributed tracing (Jaeger, Zipkin)

## Deployment Architecture

### Development
```
Local Machine
├── Python Virtual Environment
├── SQLite Database
├── Local File Storage
└── Endee API Connection
```

### Production (Docker)
```
Container
├── FastAPI Application
├── Endee API Connection
├── SQLite Volume
└── Documents Volume
```

### Production (Kubernetes)
```
Kubernetes Cluster
├── Deployment (API Pods)
├── Service (Load Balancer)
├── PersistentVolume (Databases)
├── PersistentVolume (Documents)
└── ConfigMap/Secrets (Configuration)
```

## API Design Principles

1. **RESTful**: Standard HTTP methods and status codes
2. **Versioned**: `/api/v1/` prefix for future compatibility
3. **Documented**: OpenAPI/Swagger specification
4. **Validated**: Pydantic models for all I/O
5. **Consistent**: Uniform error responses
6. **Performance**: Async where beneficial

## Extension Points

The architecture supports easy extension:

1. **New Document Types**: Add processors in `document_processor.py`
2. **Additional Search Methods**: Extend `hybrid_search.py`
3. **Custom Citation Formats**: Add to `citation_manager.py`
4. **New Endpoints**: Add routes in `api/routes.py`
5. **Alternative LLMs**: Replace Google Gemini client in services
6. **Different Vector DBs**: Swap Endee client implementation in `services/vector_store.py` (Official SDK) or legacy `backend/endee_client.py`

---

This architecture provides a solid foundation for a production-ready legal research assistant with clear separation of concerns, modularity, and scalability paths.
