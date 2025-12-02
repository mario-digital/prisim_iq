#!/bin/bash
# PrismIQ Setup Script
# Initializes the development environment for both frontend and backend

set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${CYAN}╔════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║     PrismIQ Development Setup          ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check for Bun
if ! command -v bun &> /dev/null; then
    echo -e "${RED}Error: Bun is not installed.${NC}"
    echo "Please install Bun: https://bun.sh"
    echo "  curl -fsSL https://bun.sh/install | bash"
    exit 1
fi
echo -e "  ${GREEN}✓${NC} Bun $(bun --version)"

# Check for uv
if ! command -v uv &> /dev/null; then
    echo -e "${RED}Error: uv is not installed.${NC}"
    echo "Please install uv: https://docs.astral.sh/uv/getting-started/installation/"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi
echo -e "  ${GREEN}✓${NC} uv $(uv --version)"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed.${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "  ${GREEN}✓${NC} Python $PYTHON_VERSION"

echo ""

# Setup Backend
echo -e "${CYAN}Setting up backend...${NC}"
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "  Creating virtual environment..."
    uv venv
fi

# Activate and install dependencies
echo "  Installing dependencies..."
source .venv/bin/activate
uv pip sync requirements.lock

# Create .env from example if it doesn't exist
if [ ! -f ".env" ]; then
    echo "  Creating .env from .env.example..."
    cp .env.example .env
fi

echo -e "  ${GREEN}✓${NC} Backend setup complete"
cd ..

echo ""

# Setup Frontend
echo -e "${CYAN}Setting up frontend...${NC}"
cd frontend

# Install dependencies
echo "  Installing dependencies..."
bun install

# Create .env.local from example if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo "  Creating .env.local from .env.local.example..."
    if [ -f ".env.local.example" ]; then
        cp .env.local.example .env.local
    fi
fi

echo -e "  ${GREEN}✓${NC} Frontend setup complete"
cd ..

echo ""

# Setup shared package
echo -e "${CYAN}Setting up shared package...${NC}"
cd packages/shared
bun install
echo -e "  ${GREEN}✓${NC} Shared package setup complete"
cd ../..

echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     Setup Complete!                    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "To start development servers:"
echo -e "  ${CYAN}make dev${NC}     - Start both frontend and backend"
echo -e "  ${CYAN}make help${NC}    - Show all available commands"
echo ""
echo -e "Or start individually:"
echo -e "  Backend:  ${CYAN}cd backend && source .venv/bin/activate && uvicorn src.main:app --reload${NC}"
echo -e "  Frontend: ${CYAN}cd frontend && bun run dev${NC}"

