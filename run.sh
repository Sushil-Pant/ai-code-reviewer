#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# AI Code Reviewer — Local Development Startup Script
# Usage: chmod +x run.sh && ./run.sh
# ─────────────────────────────────────────────────────────────

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "  ╔═══════════════════════════════════════════╗"
echo "  ║         AI CODE REVIEWER v1.0             ║"
echo "  ║     Powered by Google Gemini AI           ║"
echo "  ╚═══════════════════════════════════════════╝"
echo -e "${NC}"

# ── Check prerequisites ──────────────────────────────────────
echo -e "${YELLOW}[1/5] Checking prerequisites...${NC}"

if ! command -v python3 &>/dev/null; then
    echo -e "${RED}ERROR: Python 3 not found. Install from https://python.org${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
echo -e "    Python version: ${GREEN}${PYTHON_VERSION}${NC}"

# ── Check .env file ──────────────────────────────────────────
echo -e "${YELLOW}[2/5] Checking environment...${NC}"

if [ ! -f ".env" ]; then
    echo -e "    ${YELLOW}No .env found — copying from .env.example${NC}"
    cp .env.example .env
    echo -e "    ${RED}ACTION REQUIRED: Edit .env and add your GEMINI_API_KEY${NC}"
    echo -e "    Get your key at: https://aistudio.google.com/app/apikey"
    read -p "    Press Enter after editing .env to continue..."
fi

source .env
if [ -z "$GEMINI_API_KEY" ] || [ "$GEMINI_API_KEY" = "your-gemini-api-key-here" ]; then
    echo -e "${RED}ERROR: GEMINI_API_KEY not set in .env file${NC}"
    exit 1
fi
echo -e "    ${GREEN}✓ GEMINI_API_KEY found${NC}"

# ── Install backend dependencies ─────────────────────────────
echo -e "${YELLOW}[3/5] Installing backend dependencies...${NC}"
cd backend

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt
echo -e "    ${GREEN}✓ Backend dependencies installed${NC}"
cd ..

# ── Install frontend dependencies ────────────────────────────
echo -e "${YELLOW}[4/5] Installing frontend dependencies...${NC}"
cd frontend

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt
echo -e "    ${GREEN}✓ Frontend dependencies installed${NC}"
cd ..

# ── Start services ───────────────────────────────────────────
echo -e "${YELLOW}[5/5] Starting services...${NC}"

# Start backend
echo -e "    Starting FastAPI backend on port 8000..."
cd backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to be ready
echo -n "    Waiting for backend"
for i in {1..15}; do
    sleep 1
    echo -n "."
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
done

# Start frontend
echo -e "    Starting Streamlit frontend on port 8501..."
cd frontend
source venv/bin/activate
streamlit run app.py --server.port 8501 --server.headless true &
FRONTEND_PID=$!
cd ..

sleep 2

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           APPLICATION STARTED!                   ║${NC}"
echo -e "${GREEN}╠══════════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║  🌐 Frontend:  http://localhost:8501             ║${NC}"
echo -e "${GREEN}║  🔌 Backend:   http://localhost:8000             ║${NC}"
echo -e "${GREEN}║  📚 API Docs:  http://localhost:8000/docs        ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Press Ctrl+C to stop all services${NC}"

# Cleanup on exit
trap "echo -e '\n${RED}Shutting down...${NC}'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

wait
