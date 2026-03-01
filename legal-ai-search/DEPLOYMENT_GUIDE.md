# 🚀 AI Legal Research Assistant - Deployment & Usage Guide

**Complete guide for running the AI Legal Research Assistant**

This project was built for the Endee.io internship evaluation.

---

## 📋 Quick Start (3 Steps)

### 1. Backend Setup

```powershell
# Activate virtual environment
.venv\Scripts\activate

# Set API key for current session
$env:GEMINI_API_KEY = "your_api_key_here"

# Start backend server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

**Backend will be available at:** `http://localhost:8001`

**API Documentation:** `http://localhost:8001/docs`

### 2. Frontend Setup

Open a **new terminal**:

```powershell
# Activate virtual environment
.venv\Scripts\activate

# Start Streamlit frontend
streamlit run frontend/app.py
```

**Frontend will open automatically in your browser:** `http://localhost:8501`

### 3. Using the Application

1. **Upload Documents** - Go to "Upload Documents" tab, select a TXT file, click "Upload and Index"
2. **Ask Questions** - Go to "Ask Questions" tab, enter your question, click "Ask Question"
3. **View History** - Go to "Chat History" tab to see all previous Q&A

---

## 🔧 Complete Setup Instructions

### Prerequisites

- ✅ Python 3.11+ installed
- ✅ Virtual environment created (`.venv`)
- ✅ Dependencies installed (`pip install -r requirements.txt`)
- ✅ `.env` file configured with `GEMINI_API_KEY`

### Environment Configuration

Your `.env` file should contain:

```env
# REQUIRED: Google Gemini API Key
GEMINI_API_KEY=your_actual_api_key_here

# Model Configuration
GEMINI_MODEL=models/gemini-2.5-flash
EMBEDDING_MODEL=models/gemini-embedding-001

# Backend Configuration
API_HOST=0.0.0.0
API_PORT=8001

# Endee Vector Database (Optional - uses in-memory if not configured)
ENDEE_API_KEY=your_endee_key
ENDEE_URL=http://127.0.0.1:8081/api/v1

# Search Configuration
VECTOR_WEIGHT=0.7
KEYWORD_WEIGHT=0.3
TOP_K_RESULTS=5
```

### Directory Structure Check

Ensure these directories exist:

```
data/
  documents/
  vector_db/
logs/
frontend/
services/
app/
```

If they don't exist:

```powershell
New-Item -ItemType Directory -Force -Path data/documents, data/vector_db, logs
```

---

## 🎯 Testing the System

### 1. Health Check

Open browser: `http://localhost:8001/api/v1/health`

Expected response:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "vector_db_status": "connected",
  "documents_indexed": 0,
  "total_queries": 0
}
```

### 2. Test Document Upload (via API)

```powershell
$body = @{
    filename = "test_contract.txt"
    content = "This Agreement is entered into on January 1, 2024, between ABC Corporation and XYZ Limited..."
    metadata = @{ type = "contract" }
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri 'http://localhost:8001/api/v1/upload' -Body $body -ContentType 'application/json'
```

### 3. Test Question Answering (via API)

```powershell
$query = @{
    query = "What is the contract about?"
    top_k = 5
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri 'http://localhost:8001/api/v1/ask' -Body $query -ContentType 'application/json'
```

### 4. Run Integration Test

```powershell
python test_final_integration.py
```

Expected output:
```
✅ Server Status: healthy
✅ Search completed successfully
✅ Summarization successful
✅ GEMINI API INTEGRATION: FULLY FUNCTIONAL
```

---

## 🖥️ Frontend Usage Guide

### Main Interface

The Streamlit frontend has 3 tabs:

#### Tab 1: Upload Documents 📤

1. Click **"Choose a file"** button
2. Select a `.txt`, `.pdf`, or `.docx` file
3. Preview the content in the expandable section
4. Click **"Upload and Index"** button
5. Wait for processing (status shown with spinner)
6. Success message appears with chunk count

**Supported Formats:**
- ✅ TXT (fully supported)
- ⚠️ PDF (basic support)
- ⚠️ DOCX (basic support)

#### Tab 2: Ask Questions 💬

1. Check that documents are uploaded (green success message)
2. Enter your question in the text area
3. Adjust "Number of sources" slider (1-10)
4. Click **"Ask Question"** button
5. View AI-generated answer
6. Expand sources to see relevant excerpts

**Example Questions:**
- "What are the payment terms?"
- "Who are the parties involved?"
- "Summarize the main obligations"
- "What is the termination clause?"

#### Tab 3: Chat History 📚

- Browse all previous questions and answers
- View response times
- See number of sources used for each answer
- Expandable entries for full details

### Sidebar Features

- **System Status**: Real-time health check
- **Documents Indexed**: Count of uploaded documents
- **Total Queries**: Number of questions asked
- **About Section**: Project information
- **Refresh Stats**: Update system metrics

---

## 🔍 API Endpoints Reference

### Core Endpoints

#### Health Check
```
GET /api/v1/health
```
Returns system status.

#### Upload Document
```
POST /api/v1/upload
Body: {
  "filename": "document.txt",
  "content": "Document text...",
  "metadata": {}
}
```

#### Ask Question
```
POST /api/v1/ask
Body: {
  "query": "Your question",
  "top_k": 5
}
```

### Additional Endpoints

- `GET /api/v1/documents` - List all documents
- `POST /api/v1/search` - Advanced search with citations
- `POST /api/v1/summarize` - Summarize documents
- `GET /api/v1/history` - Query history
- `GET /api/v1/stats` - System statistics

**Full API documentation:** `http://localhost:8001/docs` (Swagger UI)

---

## 🐛 Troubleshooting

### Backend Issues

**Problem: Port 8001 already in use**
```powershell
# Find and kill process using port 8001
netstat -ano | findstr :8001
taskkill /F /PID <process_id>
```

**Problem: Gemini API key error**
```
# Check if key is set
$env:GEMINI_API_KEY
# If empty, set it:
$env:GEMINI_API_KEY = "your_key"
```

**Problem: Import errors**
```powershell
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend Issues

**Problem: Cannot connect to backend**
- Ensure backend is running on port 8001
- Check frontend/api_client.py for correct URL
- Verify firewall settings

**Problem: Streamlit port conflict**
```powershell
# Use different port
streamlit run frontend/app.py --server.port 8502
```

### Common Errors

**"No documents uploaded"**
- Upload at least one document first
- Check data/documents/ directory

**"Connection refused"**
- Backend not running
- Wrong port configuration

**"API key not valid"**
- Check GEMINI_API_KEY in .env
- Verify key is from Google AI Studio, not Cloud Console

---

## 📊 System Requirements

### Minimum
- CPU: 2 cores
- RAM: 4 GB
- Disk: 2 GB free
- Network: Internet connection for Gemini API

### Recommended
- CPU: 4+ cores
- RAM: 8+ GB
- Disk: 10+ GB
- Network: Stable broadband

---

## 🚀 Performance Tips

1. **Batch Processing**: Upload multiple documents before querying
2. **Chunk Size**: Adjust `CHUNK_SIZE` in .env for better results
3. **Top-K Results**: Use 5-7 sources for balanced speed/accuracy
4. **Model Selection**: `gemini-2.5-flash` is fastest, `gemini-2.5-pro` is most accurate

---

## 📝 Example Workflow

### Complete Testing Workflow

```powershell
# 1. Start backend
$env:GEMINI_API_KEY = "your_key"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001

# 2. In new terminal, start frontend
streamlit run frontend/app.py

# 3. In browser (http://localhost:8501):
#    - Upload sample legal document
#    - Ask: "What are the key terms?"
#    - View answer and sources
#    - Check chat history

# 4. Test via API (optional)
python test_final_integration.py
```

---

## 🎓 Internship Evaluation Notes

This project demonstrates:

✅ **Full-Stack Development**
- FastAPI backend with async endpoints
- Streamlit frontend with real-time updates
- RESTful API design

✅ **AI/ML Integration**
- Google Gemini AI for embeddings and generation
- RAG (Retrieval-Augmented Generation) pipeline
- Hybrid search (vector + keyword)

✅ **Vector Database**
- Endee integration with proper SDK usage
- Efficient 3072-dimensional vector storage
- Cosine similarity search

✅ **Production Best Practices**
- Environment configuration
- Error handling
- Logging and monitoring
- Clean code structure
- Comprehensive documentation

---

## 📧 Support & Contact

For issues or questions:

1. Check logs in `logs/app.log`
2. Review API docs at `/docs`
3. Test with provided integration scripts

---

**Built for Endee.io Internship Evaluation**
*Demonstrating production-ready AI application development*
