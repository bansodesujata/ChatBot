#!/bin/bash

# Exit immediately if a command fails
set -e

echo "🚀 Starting deployment of Bajaj Finance Assistant..."

# Step 1: Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Step 2: Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Step 3: Install required packages from requirements.txt
echo "📚 Installing dependencies from requirements.txt..."
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
else
    echo "❌ requirements.txt not found. Please make sure it's in the project root."
    exit 1
fi

# Step 4: Check for documents folder
echo "📁 Checking for 'documents' folder..."
if [ ! -d "documents" ]; then
  mkdir documents
  echo "⚠️ 'documents' folder created. Please add your PDF files before running the bot."
  exit 1
fi

# Step 5: Install and configure Ollama
echo "🦙 Checking Ollama installation..."
if ! command -v ollama &> /dev/null; then
  echo "Installing Ollama..."
  curl -fsSL https://ollama.com/install.sh | sh
else
  echo "✅ Ollama is already installed."
fi

echo "📥 Pulling Gemma model with Ollama..."
ollama pull gemma:2b

# Step 6: Launch the Streamlit app
echo "🚀 Launching Bajaj Finance Assistant..."
streamlit run ollama.py