# ⚖️ AI Legal Research Assistant

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31-red.svg)](https://streamlit.io/)
[![AI](https://img.shields.io/badge/AI-Gemini-purple.svg)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **AI-powered legal document search and analysis using vector databases and large language models.**

Built for the **Endee.io Internship Evaluation** - A production-ready legal research assistant that combines semantic search with AI-generated answers.

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [System Architecture](#-system-architecture)
- [Screenshots](#-screenshots)
- [Installation](#-installation)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [API Documentation](#-api-documentation)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### Core Capabilities

- **📤 Document Upload** - Support for PDF, DOCX, and TXT legal documents
- **🔍 Semantic Search** - Advanced vector embeddings for precise document retrieval
- **🤖 AI-Generated Answers** - Context-aware responses using Google Gemini
- **📚 Source Citations** - Automatic citation tracking with relevance scores
- **💬 Chat History** - Persistent conversation tracking across sessions
- **⚡ Real-time Processing** - Fast document indexing and query responses
- **🎨 Modern UI** - Premium dark theme with glassmorphism effects
- **📊 System Monitoring** - Live health checks and statistics dashboard

### Advanced Features

- **Hybrid Vector Search** - Combines BM25 and semantic similarity
- **Multi-document Analysis** - Query across multiple uploaded documents
- **Confidence Scoring** - Relevance scores for all search results
- **Document Persistence** - Automatic saving and loading of uploaded files
- **Responsive Design** - Works seamlessly on desktop and tablet

---

## � Tech Stack

### Frontend

- **Streamlit** - Modern web interface with custom CSS styling
- **HTML/CSS** - Premium glassmorphism design system

### Backend

- **FastAPI** - High-performance Python web framework
- **Uvicorn** - ASGI server for production deployment

### AI & Machine Learning

- **Google Gemini** - `gemini-2.0-flash-exp` for answer generation
- **Gemini Embeddings** - `text-embedding-004` for vector search

### Vector Database

- **Endee** - High-performance vector database for semantic search
- **Hybrid Search** - BM25 + cosine similarity ranking

### Additional Tools

- **Python-dotenv** - Environment variable management
- **Pydantic** - Data validation and settings management
- **NumPy** - Numerical computations for embeddings

---

## 🏗 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                         USER                                │
│                                                             │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│             FRONTEND (Streamlit on :8501)                   │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Upload     │  │  Ask         │  │   Chat       │     │
│  │  Documents   │  │  Questions   │  │   History    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                             │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP/REST API
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│             BACKEND (FastAPI on :8001)                      │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │  API Routes                                        │   │
│  │  • /upload  • /ask  • /health  • /clear           │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │  Services                                          │   │
│  │  • Document Processor  • Hybrid Search            │   │
│  │  • Citation Manager    • Summarization            │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
└───────┬─────────────────────────┬───────────────────────────┘
        │                         │
        ▼                         ▼
┌───────────────────┐   ┌─────────────────────────┐
│                   │   │                         │
│  ENDEE VECTOR DB  │   │   GOOGLE GEMINI API     │
│                   │   │                         │
│  • Embeddings     │   │  • Answer Generation    │
│  • Hybrid Search  │   │  • Summarization        │
│  • BM25 Ranking   │   │  • Text Embeddings      │
│                   │   │                         │
└───────────────────┘   └─────────────────────────┘
```

---

## 📸 Screenshots

### Upload Documents Interface

![Upload UI](screenshots/upload.png)

*Clean, modern interface for uploading legal documents with drag-and-drop support*

---

### Ask Questions & Get AI Answers

![Query UI](screenshots/query.png)

*AI-powered question answering with context from uploaded documents*

---

### Search Results with Citations

![Results UI](screenshots/results.png)

*Detailed source citations with relevance scores and document references*

---

### Chat History

![Chat History](screenshots/history.png)

*Complete conversation tracking with expandable question/answer pairs*

---

## 🚀 Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager
- Google Gemini API key ([Get one here](https://ai.google.dev/))

### Step 1: Clone the Repository

```bash
git clone https://github.com/ritesh-pandey001/endee.git
cd endee/legal-ai-search
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
BACKEND_URL=http://localhost:8001
```

### Step 5: Run the Backend Server

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

The backend API will be available at `http://localhost:8001`

### Step 6: Run the Frontend Application

Open a new terminal window:

```bash
streamlit run frontend/app.py --server.port 8501
```

The application will open in your browser at `http://localhost:8501`

---

## 💡 Usage

### 1. Upload Documents

1. Navigate to the **"Upload Documents"** tab
2. Click **"Browse Files"** or drag and drop files
3. Supported formats: PDF, DOCX, TXT
4. Wait for processing confirmation

### 2. Ask Questions

1. Switch to the **"Ask Questions"** tab
2. Type your legal question in the text area
3. Click **"Get Answer"**
4. View AI-generated answer with source citations

### 3. View Chat History

1. Go to the **"Chat History"** tab
2. Review all previous questions and answers
3. Expand entries to see full details
4. Check response times and source counts

### 4. System Monitoring

- Check the **sidebar** for system status
- View document count and query statistics
- Monitor backend health in real-time

---

## 📁 Project Structure

```
AI-Legal-Research-Assistant/
│
├── backend/                    # FastAPI Backend
│   ├── api/                   # API routes and endpoints
│   │   ├── __init__.py
│   │   └── routes.py          # REST API endpoints
│   ├── core/                  # Core configurations
│   │   ├── __init__.py
│   │   ├── config.py          # Settings and environment
│   │   └── logging_config.py  # Logging configuration
│   ├── models/                # Data models
│   │   ├── __init__.py
│   │   └── schemas.py         # Pydantic models
│   ├── services/              # Business logic
│   │   ├── __init__.py
│   │   ├── citation_manager.py    # Citation tracking
│   │   ├── document_processor.py  # Document processing
│   │   ├── hybrid_search.py       # Vector search
│   │   ├── query_history.py       # History management
│   │   └── summarization.py       # AI summarization
│   ├── utils/                 # Utility functions
│   │   ├── __init__.py
│   │   └── performance.py     # Performance monitoring
│   └── main.py                # FastAPI application entry
│
├── frontend/                   # Streamlit Frontend
│   └── app.py                 # Main Streamlit application
│
├── data/                       # Data storage
│   └── documents/             # Uploaded documents
│
├── screenshots/                # UI screenshots for README
│   ├── upload.png
│   ├── query.png
│   ├── results.png
│   └── history.png
│
├── docs/                       # Documentation
│   ├── API.md                 # API documentation
│   ├── ARCHITECTURE.md        # System architecture
│   ├── DEPLOYMENT.md          # Deployment guide
│   └── QUICKSTART.md          # Quick start guide
│
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
├── requirements.txt           # Python dependencies
├── LICENSE                    # MIT License
└── README.md                  # This file
```

## 📖 API Documentation

### Base URL

```
http://localhost:8001
```

### Endpoints

#### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "documents_indexed": 5,
  "total_queries": 23
}
```

#### Upload Document

```http
POST /upload
Content-Type: multipart/form-data

file: <binary>
```

**Response:**
```json
{
  "success": true,
  "filename": "contract.pdf",
  "message": "Document processed successfully"
}
```

#### Ask Question

```http
POST /ask
Content-Type: application/json

{
  "question": "What is the termination clause?"
}
```

**Response:**
```json
{
  "answer": "Based on the documents...",
  "sources": [
    {
      "filename": "contract.pdf",
      "chunk": "Termination clause...",
      "score": 0.89
    }
  ],
  "response_time": 1.23
}
```

#### Clear All Documents

```http
DELETE /clear
```

**Response:**
```json
{
  "success": true,
  "message": "All documents cleared"
}
```

For complete API documentation, visit `http://localhost:8001/docs` when the backend is running.

---
## 🤝 Contributing

This project was developed for the **Endee.io Internship Evaluation**. 

If you'd like to contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Ritesh Pandey**

- GitHub: [@ritesh-pandey001](https://github.com/ritesh-pandey001)
- Project Repository: [endee/legal-ai-search](https://github.com/ritesh-pandey001/endee/tree/master/legal-ai-search)

---

## 🙏 Acknowledgments

- **Endee.io** - For the internship opportunity and vector database technology
- **Google Gemini** - For powerful AI capabilities
- **Streamlit** - For rapid frontend development
- **FastAPI** - For high-performance backend framework

---

## 📊 Project Statistics

- **Lines of Code:** ~3,500
- **Development Time:** 2 weeks
- **Technologies Used:** 8+
- **API Endpoints:** 6
- **UI Screens:** 3 main tabs

---

## 🎯 Project Purpose

This project was specifically built for the **Endee.io Internship Evaluation** to demonstrate:

✅ Full-stack development skills  
✅ AI/ML integration expertise  
✅ Vector database implementation  
✅ RESTful API design  
✅ Modern UI/UX development  
✅ Production-ready code quality  
✅ Comprehensive documentation  

---

## 📞 Support

If you encounter any issues or have questions:

1. Check the [documentation](docs/)
2. Search existing [issues](https://github.com/ritesh-pandey001/endee/issues)
3. Create a new issue with details

---

<div align="center">

**Made with ❤️ for Endee.io Internship Evaluation**

⭐ Star this repo if you find it helpful!

</div>

