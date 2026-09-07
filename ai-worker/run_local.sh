#!/bin/bash
echo "========================================================"
echo "Starting Local AI Worker (Native Python)"
echo "========================================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "[ERROR] python3 could not be found."
    echo "Please install Python 3.10+ and try again."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "[INFO] Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "[INFO] Activating virtual environment..."
source venv/bin/activate

# Install/Upgrade pip and requirements
echo "[INFO] Installing requirements..."
python -m pip install --upgrade pip > /dev/null
pip install -r requirements.txt

# Run the FastAPI worker
echo "[INFO] Starting FastAPI server on port 8001..."
echo "[INFO] The server will detect your GPU automatically."
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
