@echo off
echo ========================================================
echo Starting Local AI Worker (Native Python)
echo ========================================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ and try again.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo [INFO] Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/Upgrade pip and requirements
echo [INFO] Installing requirements...
python -m pip install --upgrade pip >nul
pip install -r requirements.txt

REM Run the FastAPI worker (no --reload to prevent CUDA multiprocessing conflicts)
echo [INFO] Starting FastAPI server on port 8001...
echo [INFO] The server will detect your GPU automatically.
uvicorn app.main:app --host 0.0.0.0 --port 8001
