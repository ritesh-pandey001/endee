# Quick Start Guide

## Getting Started in 5 Minutes

### 1. Install Dependencies
```bash
cd ai_legal_assistant
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Set Up Environment
```bash
copy .env.example .env
# Edit .env and add your Google Gemini API key:
# GEMINI_API_KEY=your-actual-key-here
```

### 3. Start the Server
```bash
python -m app.main
```

The server will start at `http://localhost:8000`

### 4. Test the API

#### Option A: Use the Web Interface
Open your browser to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

#### Option B: Use the CLI
```bash
# Check health
python cli.py health

# Upload a document
python cli.py upload examples/sample_case.txt

# Search
python cli.py search "What is contract breach?"

# View history
python cli.py history
```

#### Option C: Use Python
```bash
python examples/usage_example.py
```

#### Option D: Use curl
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Upload document
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -H "Content-Type: application/json" \
  -d "{\"filename\":\"test.txt\",\"content\":\"Legal document text here\"}"

# Search
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"contract law\",\"top_k\":5}"
```

## Common Use Cases

### Upload Multiple Documents
```python
import requests

documents = [
    ("case1.txt", "Content of case 1..."),
    ("case2.txt", "Content of case 2..."),
]

for filename, content in documents:
    requests.post(
        "http://localhost:8000/api/v1/documents/upload",
        json={"filename": filename, "content": content}
    )
```

### Search and Get Citations
```python
response = requests.post(
    "http://localhost:8000/api/v1/search",
    json={
        "query": "What is the statute of limitations for breach of contract?",
        "top_k": 5,
        "include_citations": True
    }
)

result = response.json()
print(result['answer'])
for citation in result['citations']:
    print(f"[{citation['doc_name']}] - Score: {citation['score']}")
```

### Summarize Cases
```python
response = requests.post(
    "http://localhost:8000/api/v1/summarize",
    json={
        "text": "Long legal document text...",
        "summary_type": "comprehensive"
    }
)

summary = response.json()
print(summary['summary'])
print("Key Points:", summary['key_points'])
```

## Troubleshooting

### "Gemini API key not found"
- Ensure your `.env` file exists and contains: `GEMINI_API_KEY=your-key`
- Restart the server after adding the key

### "Module not found" errors
- Activate the virtual environment: `venv\Scripts\activate`
- Install dependencies: `pip install -r requirements.txt`

### Slow search performance
- Reduce `CHUNK_SIZE` in `.env` for faster indexing
- Adjust `TOP_K_RESULTS` to fewer results
- Check logs at `./logs/app.log` for performance metrics

## Next Steps

1. **Read the full README.md** for detailed documentation
2. **Explore the API docs** at http://localhost:8000/docs
3. **Run the test suite**: `pytest tests/`
4. **View metrics**: `curl http://localhost:8000/api/v1/metrics`
5. **Check system stats**: `curl http://localhost:8000/api/v1/stats`

## Production Deployment

### Using Docker
```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Using Gunicorn (Linux/Mac)
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

For more information, see the [README.md](README.md)
