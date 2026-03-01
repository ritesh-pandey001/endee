"""
pytest configuration file.
"""

import pytest
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment."""
    # Set test environment variables
    os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY", "test-key")
    os.environ["ENDEE_API_KEY"] = os.getenv("ENDEE_API_KEY", "test-endee-key")
    os.environ["VECTOR_DB_PATH"] = "./data/test_vector_db"
    os.environ["QUERY_HISTORY_DB"] = "./data/test_query_history.db"
    os.environ["DOCUMENTS_PATH"] = "./data/test_documents"
    os.environ["LOG_LEVEL"] = "ERROR"
    
    yield
    
    # Cleanup test data
    import shutil
    test_dirs = ["./data/test_vector_db", "./data/test_documents"]
    for test_dir in test_dirs:
        if Path(test_dir).exists():
            shutil.rmtree(test_dir)
    
    test_db = Path("./data/test_query_history.db")
    if test_db.exists():
        test_db.unlink()
