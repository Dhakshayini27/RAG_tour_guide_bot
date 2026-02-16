#!/bin/bash

echo "=========================================="
echo "Tour Guide RAG Bot - Setup Script"
echo "=========================================="
echo ""

# Create virtual environment
echo "[1/4] Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "[2/4] Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "[3/4] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "[4/4] Creating .env file..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your GROQ_API_KEY"
    echo "   Get it from: https://console.groq.com/"
else
    echo "[4/4] .env file already exists"
fi

echo ""
echo "=========================================="
echo "✓ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Get API key from https://console.groq.com/"
echo "2. Add it to .env file"
echo "3. Run: source venv/bin/activate"
echo "4. Run: python main.py"
echo ""
