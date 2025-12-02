# PrismIQ - Dynamic Pricing Copilot

An AI-powered dynamic pricing assistant that provides explainable, evidence-backed pricing recommendations through natural conversation.

## 🚀 Quick Start for AI Agents

> **Tell your AI agent:** "Read `SETUP.md` and follow it step by step to set up this project."

The `SETUP.md` file contains detailed instructions that handle common issues like Conda interference, pytest path problems, and package manager enforcement.

### One-Command Development (After Setup)

```bash
bun run dev
```

This starts both frontend (http://localhost:3000) and backend (http://localhost:8000) servers.

---

## 📋 Setup Instructions

### Prerequisites: Install Bun & uv

**Install Bun** (if `bun --version` fails):
```bash
curl -fsSL https://bun.sh/install | bash
source ~/.bashrc  # or ~/.zshrc
```

**Install uv** (if `uv --version` fails):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # or ~/.zshrc
```

### Step 1: Clone & Prepare

```bash
git clone <repository-url> prisim_iq
cd prisim_iq
chmod +x scripts/dev.sh scripts/setup.sh
```

### Step 2: Backend Setup

```bash
# ⚠️ CRITICAL: Deactivate Conda first if you have it
conda deactivate 2>/dev/null || true

cd backend
uv venv
source .venv/bin/activate
uv pip install -r requirements.lock
uv pip install pytest pytest-asyncio httpx
cp .env.example .env
```

**Verify:**
```bash
pytest -v  # Should pass 3 tests
```

### Step 3: Frontend Setup

```bash
cd ../frontend
bun install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

### Step 4: Run Both Servers

From project root:
```bash
cd ..
bun run dev
```

**Verify:**
- http://localhost:3000 → PrismIQ landing page
- http://localhost:8000/health → `{"status":"healthy",...}`

---

## 🎮 Available Commands

Run these from the **project root**:

| Command | Description |
|---------|-------------|
| `bun run dev` | Start both frontend + backend |
| `bun run dev:backend` | Start backend only |
| `bun run dev:frontend` | Start frontend only |
| `bun run test` | Run all tests |
| `bun run setup` | Run initial setup script |
| `make dev` | Alternative: start both servers |
| `make help` | Show all make commands |

---

## 🏗️ Project Structure

```
prismiq/
├── backend/           # Python FastAPI backend
│   ├── src/           # Source code
│   ├── tests/         # pytest tests
│   └── .venv/         # Virtual environment (created during setup)
├── frontend/          # Next.js 15 frontend
│   ├── src/app/       # App router pages
│   └── src/components # React components
├── packages/shared/   # Shared TypeScript types
├── scripts/           # dev.sh, setup.sh
├── docs/              # Documentation
├── SETUP.md           # ⭐ Detailed setup guide for AI agents
└── package.json       # Root scripts (bun run dev, etc.)
```

---

## 🔧 Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 15, TypeScript 5.7, Tailwind CSS 4, Zustand, Recharts |
| **Backend** | Python 3.11+, FastAPI, Pydantic 2 |
| **ML** | scikit-learn, XGBoost, SHAP |
| **Agent** | LangChain, OpenAI GPT-4o |
| **Package Managers** | Bun (frontend), uv (backend) |

---

## ⚠️ Package Manager Rules

This project enforces specific package managers:

| Context | ✅ Use | ❌ Never Use |
|---------|--------|-------------|
| **Frontend** | `bun add`, `bun install` | npm, yarn, pnpm |
| **Backend** | `uv pip install` | pip, pip3 |

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'loguru'"

**Cause:** Conda is interfering or wrong Python is being used.

```bash
conda deactivate
source backend/.venv/bin/activate
which python  # Should show .venv/bin/python
uv pip install -r requirements.lock --reinstall
```

### pytest shows wrong path (Anaconda)

```bash
hash -r  # Clear shell cache
which pytest  # Should now show .venv/bin/pytest
```

### Frontend can't connect to backend

1. Ensure backend is running on port 8000
2. Check `frontend/.env.local` has `NEXT_PUBLIC_API_URL=http://localhost:8000`
3. Restart frontend after creating `.env.local`

**For more troubleshooting, see [`SETUP.md`](SETUP.md)**

---

## 📍 Access Points

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| Health Check | http://localhost:8000/health |

---

## 📚 Documentation

- **[SETUP.md](SETUP.md)** - Detailed setup guide (start here!)
- [Project Brief](docs/brief.md)
- [Architecture](docs/architecture.md)
- [PRD](docs/prd/prd.md)

---

## 🤖 For AI Agents

When working with this codebase:

1. **Install prerequisites** (if not already installed):
   ```bash
   # Install Bun (if bun --version fails)
   curl -fsSL https://bun.sh/install | bash && source ~/.bashrc
   
   # Install uv (if uv --version fails)
   curl -LsSf https://astral.sh/uv/install.sh | sh && source ~/.bashrc
   ```
2. **First time setup:** Read and follow `SETUP.md` step by step
3. **Starting development:** Run `bun run dev` from project root
4. **Package installations:**
   - Frontend: `cd frontend && bun add <package>`
   - Backend: `cd backend && source .venv/bin/activate && uv pip install <package>`
5. **Running tests:** `bun run test` from project root
6. **Conda users:** Always run `conda deactivate` before working on this project

---

## License

Proprietary - All rights reserved.
