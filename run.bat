@echo off
:: AI Code Reviewer - Windows Startup Script
title AI Code Reviewer

echo.
echo  ╔═══════════════════════════════════════════╗
echo  ║         AI CODE REVIEWER v1.0             ║
echo  ║     Powered by Google Gemini AI           ║
echo  ╚═══════════════════════════════════════════╝
echo.

:: Check Python
py -3.13 --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install from https://python.org
    pause
    exit /b 1
)

:: Check .env
if not exist .env (
    echo No .env found - copying from .env.example
    copy .env.example .env
    echo ACTION REQUIRED: Edit .env and set your GEMINI_API_KEY
    notepad .env
    pause
)

:: Backend
echo [1/3] Setting up backend...
cd backend
if not exist venv (
    py -3.13 -m venv venv
)
call venv\Scripts\activate.bat
pip install -q -r requirements.txt
echo Starting FastAPI backend...
start "AI Code Reviewer - Backend" cmd /k "venv\Scripts\activate && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
cd ..

:: Wait
echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

:: Frontend
echo [2/3] Setting up frontend...
cd frontend
if not exist venv (
    py -3.13 -m venv venv
)
call venv\Scripts\activate.bat
pip install -q -r requirements.txt
echo Starting Streamlit frontend...
start "AI Code Reviewer - Frontend" cmd /k "venv\Scripts\activate && streamlit run app.py --server.port 8501"
cd ..

:: Done
echo.
echo ╔══════════════════════════════════════════╗
echo ║         APPLICATION STARTED!            ║
echo ╠══════════════════════════════════════════╣
echo ║  Frontend:  http://localhost:8501        ║
echo ║  Backend:   http://localhost:8000        ║
echo ║  API Docs:  http://localhost:8000/docs   ║
echo ╚══════════════════════════════════════════╝
echo.
echo Two terminal windows have opened.
echo Close them to stop the application.
pause
