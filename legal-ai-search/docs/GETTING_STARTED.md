# 🚀 GETTING STARTED - Quick Reference

## 5-Minute Setup Guide

### Prerequisites
- Python 3.9+
- Google Gemini API key
- Endee API key

---

## Setup Steps

### Windows (PowerShell)

```powershell
# 1. Navigate to project
cd ai_legal_assistant

# 2. Run setup script
powershell -ExecutionPolicy Bypass -File scripts\setup_env.ps1

# 3. Edit .env file (add your API keys)
notepad .env

# 4. Activate environment
.\venv\Scripts\Activate.ps1

# 5. Run application
python -m app.main

# 6. Open browser → http://localhost:8000/docs
```

### Linux/Mac (Bash)

```bash
# 1. Navigate to project
cd ai_legal_assistant

# 2. Run setup script
bash scripts/setup_env.sh

# 3. Edit .env file (add your API keys)
nano .env

# 4. Activate environment
source venv/bin/activate

# 5. Run application
python -m app.main

# 6. Open browser → http://localhost:8000/docs
```

---

## API Quick Test

### 1. Check Health
```bash
curl http://localhost:8000/health
```

### 2. Upload Document
```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "test.txt",
    "content": "This is a test legal document about contract law."
  }'
```

### 3. Search
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "contract law",
    "top_k": 3
  }'
```

---

## Environment Variables

Required in `.env`:

```bash
# Google Gemini (required)
GEMINI_API_KEY=your_key_here

# Endee (required)
ENDEE_API_KEY=your_endee_key_here
ENDEE_URL=https://api.endee.io/v1
```

---

## Folder Structure

```
legal-ai-search/
├── api/              → API endpoints
├── backend/          → Endee Vector DB client
├── services/         → Business logic
├── utils/            → Helpers
├── app/              → Core application
├── data/             → Data storage
├── docs/             → Documentation
├── tests/            → Tests
├── docker/           → Docker configs
└── scripts/          → Setup scripts
```

---

## Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run application
python -m app.main

# Run with custom port
uvicorn app.main:app --host 0.0.0.0 --port 8080

# Run with auto-reload (development)
uvicorn app.main:app --reload

# Run tests
pytest

# Format code
black .

# Lint code
flake8
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/documents/upload` | Upload document |
| GET | `/documents` | List documents |
| GET | `/documents/{id}` | Get document |
| POST | `/search` | Search documents |
| POST | `/summarize` | Summarize document |
| GET | `/history` | Query history |
| GET | `/metrics` | Performance metrics |

---

## Troubleshooting

### Import Error
```bash
# Make sure you're in project root
python -m app.main  # ✅ Correct
cd app && python main.py  # ❌ Wrong
```

### Endee Connection Error
```bash
# Check API key in .env
cat .env | grep ENDEE

# Test Endee connection
curl -H "Authorization: Bearer YOUR_KEY" https://api.endee.io/v1/collections
```

### Port Already in Use
```bash
# Use different port
uvicorn app.main:app --port 8001
```

---

## Key Files

- **README.md** - Full documentation
- **PROJECT_COMPLETE.md** - Completion summary
- **docs/MIGRATION_SUMMARY.md** - Detailed changes
- **docs/ARCHITECTURE.md** - System architecture
- **.env.example** - Environment template

---

## Next Steps

1. ✅ Setup complete
2. → Review README.md for full details
3. → Test API endpoints
4. → Upload sample documents
5. → Try search queries
6. → Deploy to production

---

## Support

- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Documentation: See `docs/` folder

---

**Status: Ready to Use** ✅
