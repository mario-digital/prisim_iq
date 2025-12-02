#!/bin/bash
# PrismIQ Development Server Script
# Starts both frontend and backend development servers

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${CYAN}╔════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     PrismIQ Development Servers        ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"
echo ""

# Deactivate conda if active
if [ -n "$CONDA_DEFAULT_ENV" ]; then
    echo -e "${YELLOW}Deactivating Conda environment: $CONDA_DEFAULT_ENV${NC}"
    conda deactivate 2>/dev/null || true
fi

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down servers...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    # Kill any child processes
    pkill -P $$ 2>/dev/null || true
    echo -e "${GREEN}Servers stopped.${NC}"
    exit 0
}

# Set up signal handling
trap cleanup SIGINT SIGTERM EXIT

# Check if backend venv exists
if [ ! -d "$PROJECT_ROOT/backend/.venv" ]; then
    echo -e "${RED}Backend virtual environment not found.${NC}"
    echo "Please run './scripts/setup.sh' first."
    exit 1
fi

# Check if frontend node_modules exists
if [ ! -d "$PROJECT_ROOT/frontend/node_modules" ]; then
    echo -e "${RED}Frontend dependencies not installed.${NC}"
    echo "Please run 'cd frontend && bun install' first."
    exit 1
fi

# Start backend using venv's uvicorn directly (avoids activation issues)
echo -e "${CYAN}Starting backend server...${NC}"
cd "$PROJECT_ROOT/backend"
"$PROJECT_ROOT/backend/.venv/bin/uvicorn" src.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo -e "  ${GREEN}✓${NC} Backend starting on http://localhost:8000 (PID: $BACKEND_PID)"

# Wait a moment for backend to start
sleep 2

# Check if backend started successfully
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}Backend failed to start!${NC}"
    exit 1
fi

# Start frontend
echo -e "${CYAN}Starting frontend server...${NC}"
cd "$PROJECT_ROOT/frontend"
bun run dev &
FRONTEND_PID=$!
echo -e "  ${GREEN}✓${NC} Frontend starting on http://localhost:3000 (PID: $FRONTEND_PID)"

# Wait for frontend to initialize
sleep 2

echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     Servers Running                    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "  Frontend:   ${CYAN}http://localhost:3000${NC}"
echo -e "  Backend:    ${CYAN}http://localhost:8000${NC}"
echo -e "  API Docs:   ${CYAN}http://localhost:8000/docs${NC}"
echo -e "  Health:     ${CYAN}http://localhost:8000/health${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}"
echo ""

# Wait for both processes (will exit when either dies or Ctrl+C)
wait $BACKEND_PID $FRONTEND_PID
