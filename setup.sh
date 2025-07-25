#!/bin/bash

echo "Adobe Combined Solution - Quick Setup"
echo "===================================="

echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

echo ""
echo "Creating directories..."
mkdir -p input output cache

echo ""
echo "Setup complete!"
echo ""
echo "To run the combined solution:"
echo "  python main.py"
echo ""
echo "To run with specific mode:"
echo "  python main.py --mode 1a"
echo "  python main.py --mode 1b"  
echo "  python main.py --mode both"
echo ""
echo "To run with Docker:"
echo "  docker-compose up"
echo ""
