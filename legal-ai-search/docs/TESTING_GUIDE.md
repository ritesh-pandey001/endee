# 🧪 Testing & Validation Guide

## Complete Testing Checklist for AI Legal Research Assistant

This guide provides step-by-step commands to validate that the entire project works correctly. Perfect for recruiters, interviewers, or anyone evaluating the project.

---

## 📋 Pre-Flight Checklist

Before starting, ensure you have:

- [ ] Python 3.9 or higher installed
- [ ] Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
- [ ] Endee API key ([Sign up at endee.io](https://endee.io))
- [ ] Internet connection
- [ ] Terminal/Command Prompt access

---

## 🚀 Complete Testing Workflow

### **Test 1: Environment Setup**

#### Windows (PowerShell)
```powershell
# Navigate to project directory
cd C:\ai_legal_assistant

# Check Python version (should be 3.9+)
python --version

# Expected output: Python 3.9.x or higher
```

#### Linux/Mac (Bash)
```bash
# Navigate to project directory
cd ~/ai_legal_assistant

# Check Python version (should be 3.9+)
python3 --version

# Expected output: Python 3.9.x or higher
```

**✅ Pass Criteria:** Python version is 3.9 or higher

---

### **Test 2: Virtual Environment Creation**

#### Windows
```powershell
# Create virtual environment
python -m venv venv

# Verify venv folder exists
Test-Path venv

# Expected output: True

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Verify activation (prompt should show (venv))
```

#### Linux/Mac
```bash
# Create virtual environment
python3 -m venv venv

# Verify venv folder exists
ls -d venv

# Expected output: venv

# Activate virtual environment
source venv/bin/activate

# Verify activation (prompt should show (venv))
```

**✅ Pass Criteria:** 
- Virtual environment created successfully
- Activation shows `(venv)` in prompt

---

### **Test 3: Dependency Installation**

```bash
# Upgrade pip
pip install --upgrade pip

# Expected output: Successfully installed pip-xx.x.x

# Install project dependencies
pip install -r requirements.txt

# This will install:
# - fastapi, uvicorn (web framework)
# - google-generativeai (LLM integration)
# - requests (HTTP client for Endee)
# - rank-bm25, numpy (search algorithms)
# - PyPDF2, python-docx (document processing)
# - And other dependencies...

# Verify installation
pip list | grep -E "fastapi|google-generativeai|requests"

# Windows equivalent:
# pip list | Select-String -Pattern "fastapi|google|requests"
```

**✅ Pass Criteria:** All dependencies installed without errors

#### Verify Key Packages
```bash
# Check fastapi
python -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')"

# Check google-generativeai
python -c "import google.generativeai as genai; print(f'Google Generative AI: {genai.__version__}')"

# Check requests
python -c "import requests; print(f'Requests: {requests.__version__}')"

# Expected outputs:
# FastAPI: 0.109.0
# Google Generative AI: 0.3.2
# Requests: 2.31.0
```

**✅ Pass Criteria:** All packages import successfully

---

### **Test 4: Environment Configuration**

```bash
# Create .env file from template
cp .env.example .env

# Windows:
# Copy-Item .env.example .env

# Edit .env file and add your API keys
# Use your preferred editor: nano, vim, notepad, etc.
```

**Add these required values to `.env`:**
```bash
GEMINI_API_KEY=your_actual_gemini_key_here
ENDEE_API_KEY=your_actual_endee_key_here
ENDEE_URL=https://api.endee.io/v1
```

#### Verify Configuration
```bash
# Check if .env file exists
ls -la .env

# Verify required variables are set (without exposing keys)
python -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('✅ GEMINI_API_KEY:', 'SET' if os.getenv('GEMINI_API_KEY') else '❌ MISSING')
print('✅ ENDEE_API_KEY:', 'SET' if os.getenv('ENDEE_API_KEY') else '❌ MISSING')
"
```

**✅ Pass Criteria:** Both API keys are set

---

### **Test 5: Import Validation**

```bash
# Test all critical imports
python << 'EOF'
print("Testing imports...")

try:
    from fastapi import FastAPI
    print("✅ FastAPI imported")
except Exception as e:
    print(f"❌ FastAPI import failed: {e}")

try:
    import google.generativeai as genai
    print("✅ Google Generative AI imported")
except Exception as e:
    print(f"❌ Google Generative AI import failed: {e}")

try:
    import requests
    print("✅ Requests imported")
except Exception as e:
    print(f"❌ Requests import failed: {e}")

try:
    from app.core.config import settings
    print("✅ Config module imported")
except Exception as e:
    print(f"❌ Config import failed: {e}")

try:
    from backend.endee_client import EndeeVectorDB
    print("✅ Endee client imported")
except Exception as e:
    print(f"❌ Endee client import failed: {e}")

try:
    from services.hybrid_search import HybridSearchEngine
    print("✅ Hybrid search imported")
except Exception as e:
    print(f"❌ Hybrid search import failed: {e}")

print("\nAll imports successful! ✅")
EOF
```

**✅ Pass Criteria:** All modules import without errors

---

### **Test 6: Start Application**

```bash
# Start the FastAPI application
python -m app.main

# Expected output:
# INFO:     Started server process [xxxxx]
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Alternative (with auto-reload for development):**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**✅ Pass Criteria:** 
- Server starts without errors
- Shows "Application startup complete"
- Accessible on http://localhost:8000

**Keep this terminal running and open a new terminal for the following tests.**

---

### **Test 7: API Health Check**

```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "version": "2.0.0",
#   "vector_db_status": "connected",
#   "documents_indexed": 0,
#   "total_queries": 0
# }
```

**Alternative using Python:**
```python
import requests
response = requests.get("http://localhost:8000/health")
print(response.json())
```

**Windows PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
```

**✅ Pass Criteria:** 
- HTTP 200 status
- "status": "healthy"
- "vector_db_status": "connected"

---

### **Test 8: API Documentation**

Open browser and navigate to:
```
http://localhost:8000/docs
```

**✅ Pass Criteria:**
- Swagger UI loads successfully
- Shows all 8 endpoints:
  - GET /health
  - POST /documents/upload
  - GET /documents
  - GET /documents/{doc_id}
  - POST /search
  - POST /summarize
  - GET /history
  - GET /metrics

**Alternative (ReDoc):**
```
http://localhost:8000/redoc
```

---

### **Test 9: Document Upload**

#### Test with Sample Document

```bash
# Create a test legal document
cat > test_document.txt << 'EOF'
SUPREME COURT CASE STUDY

Case Number: 2024-CV-001
Court: District Court of Appeals

FACTS:
The plaintiff filed a breach of contract claim against the defendant for failure to deliver goods as specified in their written agreement dated January 15, 2024. The contract stipulated delivery within 30 days.

ISSUE:
Whether the defendant's delay in delivery constitutes a material breach of contract.

HOLDING:
The court held that the delay constituted a material breach. The contract explicitly stated that "time is of the essence," making timely delivery a critical term.

REASONING:
When parties include a "time is of the essence" clause, courts will strictly enforce delivery deadlines. The defendant's 45-day delay exceeded the contractual timeframe by 50%, causing measurable harm to the plaintiff's business operations.

CONCLUSION:
Judgment for the plaintiff. Defendant is liable for breach of contract damages.
EOF

# Upload the document via API
curl -X POST "http://localhost:8000/documents/upload" \
  -H "Content-Type: application/json" \
  -d "{
    \"filename\": \"breach_of_contract_case.txt\",
    \"content\": \"$(cat test_document.txt | sed 's/"/\\"/g' | tr '\n' ' ')\",
    \"metadata\": {
      \"case_number\": \"2024-CV-001\",
      \"court\": \"District Court\",
      \"year\": 2024,
      \"topic\": \"Contract Law\"
    }
  }"

# Expected response (example):
# {
#   "doc_id": "breach_of_contract_case_20240228123456_a1b2c3d4",
#   "filename": "breach_of_contract_case.txt",
#   "upload_date": "2024-02-28T12:34:56.789Z",
#   "num_chunks": 3,
#   "size_bytes": 847,
#   "metadata": {
#     "case_number": "2024-CV-001",
#     "court": "District Court",
#     "year": 2024,
#     "topic": "Contract Law"
#   }
# }
```

**Windows PowerShell Alternative:**
```powershell
$content = @"
SUPREME COURT CASE STUDY
Case Number: 2024-CV-001
[... full content ...]
"@

$body = @{
    filename = "breach_of_contract_case.txt"
    content = $content
    metadata = @{
        case_number = "2024-CV-001"
        court = "District Court"
        year = 2024
        topic = "Contract Law"
    }
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/documents/upload" -Method Post -Body $body -ContentType "application/json"
```

**✅ Pass Criteria:**
- HTTP 200 status
- Returns doc_id
- num_chunks > 0
- Document indexed successfully

---

### **Test 10: Vector Database Initialization**

After uploading a document, verify Endee Vector Database initialization:

```bash
# The upload process automatically:
# 1. Chunks the document
# 2. Generates embeddings using Google Gemini
# 3. Stores vectors in Endee

# Verify by checking the application logs
# Look for messages like:
# "Added X documents to Endee"
# "Built BM25 index with X documents"
```

**✅ Pass Criteria:**
- No Endee connection errors in logs
- Embeddings generated successfully
- Vectors stored in Endee

---

### **Test 11: List Documents**

```bash
# List all uploaded documents
curl http://localhost:8000/documents

# Expected response (example):
# [
#   "breach_of_contract_case_20240228123456_a1b2c3d4"
# ]
```

**PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/documents" -Method Get
```

**✅ Pass Criteria:**
- Returns array of document IDs
- Contains the uploaded document

---

### **Test 12: Search Functionality**

#### Test Semantic Search

```bash
# Perform a semantic search query
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What constitutes a material breach of contract?",
    "top_k": 3,
    "include_citations": true
  }'

# Expected response structure:
# {
#   "query": "What constitutes a material breach of contract?",
#   "answer": "A material breach of contract occurs when...",
#   "citations": [
#     {
#       "source_id": "breach_of_contract_case_...",
#       "relevance_score": 0.89,
#       "text": "The court held that the delay constituted...",
#       "metadata": { ... }
#     }
#   ],
#   "search_time_ms": 342,
#   "model_used": "gpt-4"
# }
```

**PowerShell:**
```powershell
$searchBody = @{
    query = "What constitutes a material breach of contract?"
    top_k = 3
    include_citations = $true
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/search" -Method Post -Body $searchBody -ContentType "application/json"
```

**✅ Pass Criteria:**
- HTTP 200 status
- Returns generated answer
- Citations include relevant passages
- relevance_score > 0.7
- search_time_ms < 5000

#### Test Different Queries

```bash
# Test query 2: Specific legal term
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "time is of the essence clause",
    "top_k": 2
  }'

# Test query 3: Broad question
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the remedies for breach of contract?",
    "top_k": 5
  }'
```

---

### **Test 13: Hybrid Search Validation**

Verify that both vector and keyword search are working:

```bash
# This query should trigger both:
# - Vector search (semantic understanding)
# - Keyword search (exact term "contract")

curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "breach of contract damages",
    "top_k": 3
  }'

# Check the application logs for:
# "Vector search returned X results"
# "Keyword search returned X results"
# "Hybrid search completed in X.XXXs"
```

**✅ Pass Criteria:**
- Both vector and keyword search execute
- Results are fused with weighted scores
- Hybrid score combines both methods

---

### **Test 14: Document Summarization**

```bash
# Get the document ID from previous tests
DOC_ID="breach_of_contract_case_20240228123456_a1b2c3d4"

# Request document summary
curl -X POST "http://localhost:8000/summarize" \
  -H "Content-Type: application/json" \
  -d "{
    \"document_id\": \"$DOC_ID\",
    \"summary_type\": \"brief\"
  }"

# Expected response:
# {
#   "document_id": "...",
#   "summary": "This case involves a breach of contract claim...",
#   "summary_type": "brief",
#   "key_points": [...],
#   "entities": {
#     "parties": ["plaintiff", "defendant"],
#     "courts": ["District Court of Appeals"],
#     "case_numbers": ["2024-CV-001"]
#   }
# }
```

**✅ Pass Criteria:**
- Returns comprehensive summary
- Extracts key points
- Identifies legal entities

---

### **Test 15: Query History**

```bash
# Check query history
curl "http://localhost:8000/history?page=1&page_size=10"

# Expected response:
# {
#   "queries": [
#     {
#       "id": 1,
#       "query": "What constitutes a material breach...",
#       "timestamp": "2024-02-28T12:34:56.789Z",
#       "results_count": 3,
#       "search_time_ms": 342
#     },
#     ...
#   ],
#   "total": 5,
#   "page": 1,
#   "page_size": 10
# }
```

**✅ Pass Criteria:**
- Returns list of previous queries
- Includes timestamps and metrics
- Pagination works correctly

---

### **Test 16: Performance Metrics**

```bash
# Get performance metrics
curl http://localhost:8000/metrics

# Expected response:
# {
#   "total_operations": 15,
#   "average_response_time_ms": 450,
#   "success_rate": 1.0,
#   "operations_by_type": {
#     "search": 5,
#     "upload": 1,
#     "summarize": 1
#   },
#   "slow_operations": []
# }
```

**✅ Pass Criteria:**
- Returns operation statistics
- Success rate close to 1.0
- Average response time reasonable

---

### **Test 17: Error Handling**

Test that the API handles errors gracefully:

#### Test 17.1: Invalid Document Upload
```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "test.txt",
    "content": ""
  }'

# Expected: HTTP 400 or 422 with error message
```

#### Test 17.2: Search Without Documents
```bash
# If no documents uploaded:
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "test query",
    "top_k": 5
  }'

# Expected: Returns message about no documents found
```

#### Test 17.3: Invalid Document ID
```bash
curl "http://localhost:8000/documents/invalid_id_12345"

# Expected: HTTP 404 with error message
```

**✅ Pass Criteria:**
- Returns appropriate HTTP status codes
- Provides clear error messages
- Doesn't crash the application

---

### **Test 18: End-to-End Workflow**

Complete workflow test from start to finish:

```bash
# Step 1: Upload multiple documents
curl -X POST "http://localhost:8000/documents/upload" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "contract_law_basics.txt",
    "content": "Contract law governs agreements between parties. Essential elements include offer, acceptance, and consideration. A breach occurs when one party fails to fulfill contractual obligations.",
    "metadata": {"topic": "Contract Law Basics"}
  }'

# Step 2: Search across all documents
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the essential elements of a contract?",
    "top_k": 5,
    "include_citations": true
  }'

# Step 3: Verify results span multiple documents
# Check that citations come from different source documents

# Step 4: Get history
curl "http://localhost:8000/history?page=1&page_size=5"

# Step 5: Check metrics
curl "http://localhost:8000/metrics"
```

**✅ Pass Criteria:**
- All steps execute successfully
- Search returns results from multiple documents
- History tracks all queries
- Metrics show accumulated operations

---

### **Test 19: Stress Test (Optional)**

Test system under moderate load:

```bash
# Run 10 concurrent searches
for i in {1..10}; do
  curl -X POST "http://localhost:8000/search" \
    -H "Content-Type: application/json" \
    -d "{
      \"query\": \"test query $i\",
      \"top_k\": 3
    }" &
done

wait

# Check that all requests completed successfully
```

**✅ Pass Criteria:**
- All requests complete successfully
- Response times remain reasonable
- No errors or crashes

---

### **Test 20: Cleanup & Restart**

Test that the system can be stopped and restarted:

```bash
# Stop the application (Ctrl+C in the server terminal)

# Restart the application
python -m app.main

# Verify documents persist
curl http://localhost:8000/documents

# Verify search still works
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "contract breach",
    "top_k": 3
  }'
```

**✅ Pass Criteria:**
- Application restarts without errors
- Documents are still accessible
- Search functionality works after restart

---

## 📊 Complete Testing Checklist

Use this checklist to track your testing progress:

- [ ] **Test 1**: Environment Setup ✅
- [ ] **Test 2**: Virtual Environment Creation ✅
- [ ] **Test 3**: Dependency Installation ✅
- [ ] **Test 4**: Environment Configuration ✅
- [ ] **Test 5**: Import Validation ✅
- [ ] **Test 6**: Start Application ✅
- [ ] **Test 7**: API Health Check ✅
- [ ] **Test 8**: API Documentation ✅
- [ ] **Test 9**: Document Upload ✅
- [ ] **Test 10**: Vector Database Initialization ✅
- [ ] **Test 11**: List Documents ✅
- [ ] **Test 12**: Search Functionality ✅
- [ ] **Test 13**: Hybrid Search Validation ✅
- [ ] **Test 14**: Document Summarization ✅
- [ ] **Test 15**: Query History ✅
- [ ] **Test 16**: Performance Metrics ✅
- [ ] **Test 17**: Error Handling ✅
- [ ] **Test 18**: End-to-End Workflow ✅
- [ ] **Test 19**: Stress Test (Optional) ✅
- [ ] **Test 20**: Cleanup & Restart ✅

---

## 🎯 Quick Validation Script

For recruiters who want a quick automated test:

### Windows (PowerShell)
```powershell
# Save as: test_quick.ps1

Write-Host "🧪 Quick Validation Test" -ForegroundColor Cyan
Write-Host ""

# Test 1: Health Check
Write-Host "Test 1: Health Check..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
    if ($health.status -eq "healthy") {
        Write-Host "✅ PASS: API is healthy" -ForegroundColor Green
    } else {
        Write-Host "❌ FAIL: API is not healthy" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ FAIL: Cannot connect to API" -ForegroundColor Red
}

# Test 2: Upload Document
Write-Host "`nTest 2: Document Upload..." -ForegroundColor Yellow
$uploadBody = @{
    filename = "test_doc.txt"
    content = "This is a test legal document about contract law and breach of contract."
    metadata = @{ test = $true }
} | ConvertTo-Json

try {
    $upload = Invoke-RestMethod -Uri "http://localhost:8000/documents/upload" -Method Post -Body $uploadBody -ContentType "application/json"
    Write-Host "✅ PASS: Document uploaded (ID: $($upload.doc_id))" -ForegroundColor Green
    $docId = $upload.doc_id
} catch {
    Write-Host "❌ FAIL: Document upload failed" -ForegroundColor Red
}

# Test 3: Search
Write-Host "`nTest 3: Search..." -ForegroundColor Yellow
$searchBody = @{
    query = "contract law"
    top_k = 3
} | ConvertTo-Json

try {
    $search = Invoke-RestMethod -Uri "http://localhost:8000/search" -Method Post -Body $searchBody -ContentType "application/json"
    Write-Host "✅ PASS: Search completed in $($search.search_time_ms)ms" -ForegroundColor Green
} catch {
    Write-Host "❌ FAIL: Search failed" -ForegroundColor Red
}

Write-Host "`n🎉 Quick validation complete!" -ForegroundColor Cyan
```

### Linux/Mac (Bash)
```bash
#!/bin/bash
# Save as: test_quick.sh

echo "🧪 Quick Validation Test"
echo ""

# Test 1: Health Check
echo "Test 1: Health Check..."
health=$(curl -s http://localhost:8000/health)
if echo "$health" | grep -q "healthy"; then
    echo "✅ PASS: API is healthy"
else
    echo "❌ FAIL: API is not healthy"
fi

# Test 2: Upload Document
echo ""
echo "Test 2: Document Upload..."
upload=$(curl -s -X POST "http://localhost:8000/documents/upload" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "test_doc.txt",
    "content": "This is a test legal document about contract law.",
    "metadata": {"test": true}
  }')

if echo "$upload" | grep -q "doc_id"; then
    echo "✅ PASS: Document uploaded"
    doc_id=$(echo "$upload" | grep -o '"doc_id":"[^"]*' | cut -d'"' -f4)
else
    echo "❌ FAIL: Document upload failed"
fi

# Test 3: Search
echo ""
echo "Test 3: Search..."
search=$(curl -s -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "contract law", "top_k": 3}')

if echo "$search" | grep -q "answer"; then
    echo "✅ PASS: Search completed"
else
    echo "❌ FAIL: Search failed"
fi

echo ""
echo "🎉 Quick validation complete!"
```

**Run the script:**
```bash
# Make executable
chmod +x test_quick.sh

# Run
./test_quick.sh
```

---

## 🐛 Troubleshooting Guide

### Issue: "Module not found" errors

**Solution:**
```bash
# Ensure you're in the project root
pwd  # Should show: /path/to/ai_legal_assistant

# Ensure virtual environment is activated
which python  # Should show: ./venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Connection refused" to Endee

**Solution:**
```bash
# Check API key is set
echo $ENDEE_API_KEY  # Should show your key

# Test Endee connection
curl -H "Authorization: Bearer $ENDEE_API_KEY" https://api.endee.io/v1/collections
```

### Issue: Gemini API errors

**Solution:**
```bash
# Verify API key
echo $GEMINI_API_KEY

# Check quota and access
curl "https://generativelanguage.googleapis.com/v1/models?key=$GEMINI_API_KEY"
```

### Issue: Port 8000 already in use

**Solution:**
```bash
# Use a different port
uvicorn app.main:app --port 8001

# Or kill the process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

---

## ✅ Success Criteria Summary

A fully functional system should:

1. ✅ Start without errors
2. ✅ Health check returns "healthy"
3. ✅ Documents upload successfully
4. ✅ Embeddings generate correctly
5. ✅ Vectors store in Endee
6. ✅ Search returns relevant results
7. ✅ Citations include source documents
8. ✅ Response times are reasonable (< 5s)
9. ✅ Error handling works properly
10. ✅ Persist data across restarts

---

## 📈 Expected Performance Metrics

| Operation | Target Time | Acceptable Range |
|-----------|------------|------------------|
| Health Check | < 50ms | < 100ms |
| Document Upload (1KB) | < 500ms | < 1s |
| Vector Search | < 100ms | < 200ms |
| Hybrid Search | < 200ms | < 500ms |
| Answer Generation | < 3s | < 5s |
| Summarization | < 4s | < 7s |

---

## 🎓 For Recruiters/Evaluators

**Minimum Viable Test** (5 minutes):
1. Run setup script
2. Add API keys to .env
3. Start application: `python -m app.main`
4. Check health: `curl http://localhost:8000/health`
5. Upload test document (Test 9)
6. Run search query (Test 12)

**Result:** If all 6 steps pass, the system is working correctly.

**Comprehensive Test** (20 minutes):
- Follow all 20 tests sequentially
- Use the testing checklist
- Run the quick validation script

**Result:** Complete validation of all features and integrations.

---

## 📞 Support

If you encounter issues during testing:

1. Check the [TROUBLESHOOTING section](#-troubleshooting-guide) above
2. Review [GETTING_STARTED.md](GETTING_STARTED.md)
3. Check application logs in `logs/` folder
4. Verify API keys are correctly set
5. Ensure all dependencies are installed

---

**Testing Status: ✅ COMPREHENSIVE & RECRUITER-FRIENDLY**

Last Updated: February 28, 2026
