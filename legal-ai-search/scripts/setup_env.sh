#!/bin/bash
# Setup script for AI Legal Research Assistant

echo "🏛️  AI Legal Research Assistant - Setup"
echo "========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
if [ "$(echo "$python_version >= 3.9" | bc)" -eq 0 ]; then
    echo "❌ Python 3.9+ required. Found: $python_version"
    exit 1
fi
echo "✅ Python $python_version"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv
echo "✅ Virtual environment created"

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  Please edit .env and add your API keys:"
    echo "   - GEMINI_API_KEY"
    echo "   - ENDEE_API_KEY"
else
    echo ""
    echo "✅ .env file already exists"
fi

# Create necessary directories
echo ""
echo "Creating data directories..."
mkdir -p data/documents data/vector_db logs
echo "✅ Directories created"

# Done
echo ""
echo "========================================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your API keys"
echo "2. Run: source venv/bin/activate"
echo "3. Run: python -m app.main"
echo "4. Open: http://localhost:8000/docs"
echo ""
