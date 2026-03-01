# 🎯 RECRUITER QUICK START

This file provides the absolute fastest way to validate the AI Legal Assistant project.

## Prerequisites Checklist

Before running tests, ensure:

- [ ] Python 3.9+ installed: `python --version`
- [ ] Virtual environment created: `python -m venv venv`
- [ ] Virtual environment activated:
  - Windows: `.\venv\Scripts\Activate.ps1`
  - Linux/Mac: `source venv/bin/activate`
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] `.env` file created with API keys (copy from `.env.example`)
- [ ] Server is running: `python -m app.main`

## ⚡ One-Command Test

Once the server is running, test everything in one command:

### Windows
```powershell
powershell -ExecutionPolicy Bypass -File scripts\test_quick.ps1
```

Or use the batch file:
```cmd
scripts\test_one_command.bat
```

### Linux/Mac
```bash
bash scripts/test_quick.sh
```

## 🎬 Complete Demo (5 Minutes)

### Step 1: Setup (2 minutes)
```bash
# Clone & setup
git clone <repository-url>
cd ai_legal_assistant

# Windows setup
powershell -ExecutionPolicy Bypass -File scripts\setup_env.ps1

# Linux/Mac setup
bash scripts/setup_env.sh

# Edit .env and add your API keys
# GEMINI_API_KEY=your_key...
# ENDEE_API_KEY=...
```

### Step 2: Start Server (30 seconds)
```bash
# Activate virtual environment
# Windows:
.\venv\Scripts\Activate.ps1

# Linux/Mac:
source venv/bin/activate

# Start server
python -m app.main

# Wait for: "Application startup complete"
```

### Step 3: Run Tests (2 minutes)
**Open a new terminal window** and run:

```bash
# Windows
powershell -ExecutionPolicy Bypass -File scripts\test_quick.ps1

# Linux/Mac
bash scripts/test_quick.sh
```

### Step 4: Verify Results
Expected output:
```
🎉 ALL TESTS PASSED! System is fully functional.
✅ The AI Legal Assistant is ready for production use.

Tests Passed: 6 / 6
Success Rate: 100.0%
```

## 📊 What Gets Tested

The quick validation script tests:

1. ✅ **Health Check** - API is responsive and healthy
2. ✅ **API Documentation** - Swagger UI accessible
3. ✅ **Document Upload** - Can upload and process legal documents
4. ✅ **Document Listing** - Can retrieve document metadata
5. ✅ **Semantic Search** - Hybrid search returns relevant results  
6. ✅ **Query History** - Tracks all search queries

## 🔍 Manual Verification

If you prefer to test manually:

### Test 1: Health Check
```bash
curl http://localhost:8000/health
```

Should return:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "vector_db_status": "connected"
}
```

### Test 2: View API Documentation
Open browser: http://localhost:8000/docs

### Test 3: Upload a Document
```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "test.txt",
    "content": "This is a test legal document about contract law and breach of contract.",
    "metadata": {"test": true}
  }'
```

### Test 4: Search
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "contract law",
    "top_k": 3
  }'
```

## 📚 More Information

- **Full Testing Guide**: [docs/TESTING_GUIDE.md](../docs/TESTING_GUIDE.md) - 20+ comprehensive tests
- **Getting Started**: [docs/GETTING_STARTED.md](../docs/GETTING_STARTED.md) - Detailed setup
- **Architecture**: [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) - System design
- **Migration Summary**: [docs/MIGRATION_SUMMARY.md](../docs/MIGRATION_SUMMARY.md) - ChromaDB → Endee

## 🆘 Troubleshooting

### "Server is not running"
```bash
# Check if something is on port 8000
# Windows:
netstat -ano | findstr :8000

# Linux/Mac:
lsof -i :8000

# Start the server
python -m app.main
```

### "Module not found"
```bash
# Make sure you're in the virtual environment
# Prompt should show: (venv)

# Reinstall dependencies
pip install -r requirements.txt
```

### "Connection to Endee failed"
```bash
# Check API key is set
# Windows:
echo $env:ENDEE_API_KEY

# Linux/Mac:
echo $ENDEE_API_KEY

# Make sure .env file has the correct key
```

### "Gemini API error"
```bash
# Check API key is set and has credits
# Test manually:
curl "https://generativelanguage.googleapis.com/v1/models?key=$GEMINI_API_KEY"
```

## ✨ Expected Results

All tests should pass with these metrics:

| Test | Expected Time | Status |
|------|--------------|--------|
| Health Check | < 100ms | ✅ |
| Document Upload | < 1s | ✅ |
| Semantic Search | < 5s | ✅ |
| Query History | < 100ms | ✅ |

## 🎯 Success Criteria

The project is working correctly if:

✅ All 6 automated tests pass  
✅ No error messages in server logs  
✅ Search returns relevant results  
✅ Response times are reasonable  
✅ API documentation loads correctly  

---

**Total validation time: 2-3 minutes** ⚡

**For detailed evaluation criteria, see [TESTING_GUIDE.md](../docs/TESTING_GUIDE.md)**
