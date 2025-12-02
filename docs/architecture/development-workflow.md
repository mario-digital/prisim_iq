# 13. Development Workflow

## 13.1 Prerequisites

```bash
# Required software
bun --version       # v1.1.38+
python3.12 --version # v3.12.x
uv --version        # v0.5.x+

# Install (macOS)
curl -fsSL https://bun.sh/install | bash
brew install pyenv
pyenv install 3.12.7
pyenv global 3.12.7
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 13.2 Initial Setup

```bash
# Clone and setup
git clone <repo>
cd prismiq

# Backend setup
cd backend
uv venv
source .venv/bin/activate
uv pip sync requirements.lock
cp .env.example .env
# Add OPENAI_API_KEY to .env

# Frontend setup
cd ../frontend
bun install
cp .env.local.example .env.local

# Shared package
cd ../packages/shared
bun install
bun run build
```

## 13.3 Development Commands

```bash
# Start both services (from root)
make dev

# Or individually:
# Backend (from backend/)
source .venv/bin/activate
uvicorn src.main:app --reload --port 8000

# Frontend (from frontend/)
bun run dev

# Run tests
make test

# Type check
make typecheck

# Lint
make lint
```

## 13.4 Environment Variables

```bash
# backend/.env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
N8N_WEBHOOK_BASE=http://localhost:5678/webhook
DEBUG=true
LOG_LEVEL=DEBUG

# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---
