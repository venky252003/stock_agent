#!/bin/bash

# Check if 'uv' is installed
if ! command -v uv &> /dev/null
then
    echo "Error: 'uv' is not installed."
    echo "Please install 'uv' by running: pip install uv"
    pip install uv    
fi

echo "✅ 'uv' is installed. Proceeding with dependency installation..."

# Install dependencies from requirements.txt
# uv pip install -r requirements.txt
uv sync --upgrade

# Optional: Install project in editable mode if using pyproject.toml
# if [ -f "pyproject.toml" ]; then
#     echo "📦 Installing project in editable mode..."
#     uv pip install -e .
# fi

echo "✅ Setup completed successfully."
