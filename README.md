# PrismIQ

**AI-Powered Dynamic Pricing Copilot with Explainable ML**

> 🎬 **[View the Presentation](https://app.chroniclehq.com/share/8b606ee7-7740-4488-8399-a327cb022d48/113dceb9-3b93-45bd-a19b-68a868b87b9a/intro)**

An intelligent pricing assistant that provides explainable, evidence-backed pricing recommendations through natural conversation. Built for the Honeywell Aerospace Hackathon, PrismIQ demonstrates how ML-driven dynamic pricing concepts translate from ride-sharing to enterprise applications.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🤖 **Conversational AI Agent** | Natural language chat powered by GPT-4o with LangChain tool-calling |
| 📊 **ML Price Optimization** | Ensemble models (XGBoost, Decision Tree, Linear Regression) with 98% accuracy |
| 🔍 **Full Explainability** | SHAP values, decision traces, sensitivity analysis for every recommendation |
| 📈 **Real-time Visualizations** | Demand curves, profit curves, feature importance charts with Recharts |
| 🔄 **n8n Integration** | External data feeds for weather, events, and fuel prices |
| 🎯 **Multi-Agent Orchestrator** | LangGraph-based specialized agents for complex queries |
| 💼 **Business Rules Engine** | Configurable floors, caps, and loyalty discounts |
| ⚡ **Streaming Responses** | Real-time SSE streaming for responsive chat experience |

---

## 🖼️ Screenshots

<details>
<summary>Click to view screenshots</summary>

### Main Workspace
Three-panel layout with context controls (left), chat interface (center), and explainability visualizations (right).

### Explainability Panel
Feature importance charts, decision traces, demand/profit curves, and sensitivity analysis.

### Honeywell Mapping
Enterprise translation overlay showing ride-sharing to aerospace parts mapping.

</details>

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              Frontend                                    │
│  Next.js 15 + React 19 + TypeScript + Tailwind CSS + Zustand + Recharts │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ SSE Streaming
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                              Backend                                     │
│                         FastAPI + Python 3.11+                          │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │  LangChain  │  │   ML        │  │  Business   │  │  Explain-   │    │
│  │  Agent      │  │   Pipeline  │  │  Rules      │  │  ability    │    │
│  │  + Tools    │  │  (XGBoost)  │  │  Engine     │  │  (SHAP)     │    │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                      │
│  │  Orchestrator│  │  n8n       │  │  Decision   │                      │
│  │  (LangGraph) │  │  External  │  │  Trace      │                      │
│  │             │  │  Data      │  │  Audit      │                      │
│  └─────────────┘  └─────────────┘  └─────────────┘                      │
└─────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           Data Layer                                     │
│  Trained Models (.joblib) │ EDA Summary │ Model Cards │ Evidence Docs   │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key Components:**

- **AI Agent**: LangChain tool-calling agent with 8 specialized tools
- **ML Pipeline**: K-Means segmentation → Demand prediction → Price optimization
- **Business Rules**: Priority-ordered rules for floors, caps, and discounts
- **Explainability**: SHAP analysis, decision traces, model agreement metrics
- **Orchestrator**: Multi-agent coordination for complex pricing queries

---

## 🚀 Quick Start

### Prerequisites

| Tool | Version | Installation |
|------|---------|--------------|
| **Bun** | 1.0+ | `curl -fsSL https://bun.sh/install \| bash` |
| **uv** | 0.1+ | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **Python** | 3.11+ | System or pyenv |
| **Node.js** | 20+ | For Next.js compatibility |

### One-Command Start (After Setup)

```bash
bun run dev
```

This starts both frontend (http://localhost:3000) and backend (http://localhost:8000).

---

### Local Development Setup

#### Step 1: Clone & Prepare

```bash
git clone <repository-url> prismiq
cd prismiq
chmod +x scripts/dev.sh scripts/setup.sh
```

#### Step 2: Backend Setup

```bash
# ⚠️ CRITICAL: Deactivate Conda first if active
conda deactivate 2>/dev/null || true

cd backend
uv venv
source .venv/bin/activate
uv pip install -r requirements.lock

# Create environment file
cp .env.example .env
# Add your OpenAI API key to .env:
# OPENAI_API_KEY=sk-...
```

**Verify backend:**
```bash
pytest -v  # Should pass all tests
uvicorn src.main:app --reload --port 8000
# Visit http://localhost:8000/docs for Swagger UI
```

#### Step 3: Frontend Setup

```bash
cd ../frontend
bun install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

**Verify frontend:**
```bash
bun dev
# Visit http://localhost:3000
```

#### Step 4: Run Both Together

From project root:
```bash
bun run dev
```

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'loguru'` | Run `conda deactivate` then `source backend/.venv/bin/activate` |
| pytest shows Anaconda path | Run `hash -r` to clear shell cache |
| Frontend can't connect to backend | Ensure `.env.local` has `NEXT_PUBLIC_API_URL=http://localhost:8000` |
| OpenAI API errors | Verify `OPENAI_API_KEY` is set in `backend/.env` |
| Models not found (503 error) | ML models should be pre-trained in `backend/data/models/` |
| Chat not streaming | Check browser console for SSE connection errors |

**Health Checks:**

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- Health Endpoint: http://localhost:8000/health

---

## 📁 Monorepo Structure

```
prismiq/
├── frontend/                    # Next.js 15 frontend (Bun workspace)
│   ├── src/
│   │   ├── app/                 # Next.js App Router pages
│   │   │   ├── workspace/       # Main pricing workspace
│   │   │   ├── executive/       # Executive summary dashboard
│   │   │   └── evidence/        # Model documentation viewer
│   │   ├── components/          # React components
│   │   │   ├── chat/            # Chat interface components
│   │   │   ├── context/         # Market context controls
│   │   │   ├── visualizations/  # Charts and explainability
│   │   │   ├── layout/          # Three-panel layout system
│   │   │   ├── honeywell/       # Enterprise mapping overlay
│   │   │   └── ui/              # shadcn/ui components
│   │   ├── stores/              # Zustand state management
│   │   ├── services/            # API client services
│   │   └── lib/                 # Utilities
│   ├── tests/                   # Frontend tests
│   └── README.md                # Frontend documentation
│
├── backend/                     # FastAPI backend (Python uv project)
│   ├── src/
│   │   ├── api/                 # HTTP endpoints
│   │   │   ├── routers/         # FastAPI routers (chat, pricing, explain)
│   │   │   └── middleware/      # Logging, timing middleware
│   │   ├── agent/               # LangChain AI agent
│   │   │   ├── tools/           # Agent tools (optimize, explain, etc.)
│   │   │   ├── prompts/         # System prompts
│   │   │   └── streaming.py     # SSE streaming utilities
│   │   ├── ml/                  # ML pipeline
│   │   │   ├── segmenter.py     # K-Means market segmentation
│   │   │   ├── demand_simulator.py  # Log-linear demand model
│   │   │   ├── model_manager.py # Model serving
│   │   │   ├── price_optimizer.py   # Grid search optimization
│   │   │   └── training.py      # Model training pipeline
│   │   ├── rules/               # Business rules engine
│   │   ├── explainability/      # SHAP, decision traces
│   │   ├── orchestrator/        # Multi-agent LangGraph system
│   │   ├── services/            # Business logic services
│   │   ├── schemas/             # Pydantic models
│   │   └── main.py              # FastAPI app entry
│   ├── data/
│   │   ├── models/              # Trained ML models (.joblib)
│   │   ├── cards/               # Model & data cards (JSON + MD)
│   │   ├── evidence/            # Methodology documentation
│   │   ├── cache/               # External data cache (weather, fuel)
│   │   └── processed/           # Training data (parquet)
│   ├── tests/                   # pytest tests
│   │   ├── unit/                # Unit tests
│   │   └── integration/         # Integration tests
│   └── README.md                # Backend documentation
│
├── packages/
│   └── shared/                  # Shared TypeScript package
│       └── src/
│           ├── schemas/         # Zod schemas (FE/BE contract)
│           ├── types/           # TypeScript types
│           └── constants/       # Shared constants
│
├── docs/                        # Comprehensive documentation
│   ├── architecture/            # Architecture documents
│   │   ├── index.md             # Architecture overview
│   │   ├── tech-stack.md        # Technology decisions
│   │   ├── coding-standards.md  # Code style guide
│   │   ├── testing-strategy.md  # Testing approach
│   │   └── ...                  # More architecture docs
│   ├── prd/                     # Product requirements
│   │   ├── prd.md               # Main PRD
│   │   └── epic-*.md            # Epic breakdowns
│   ├── stories/                 # User stories
│   └── qa/                      # Quality assurance gates
│
├── prismIQ-N8N/                 # n8n workflow exports
│   ├── prismiq_weather.json     # Weather data workflow
│   ├── prismiq_events.json      # Events data workflow
│   └── prismiq_fuel.json        # Fuel prices workflow
│
├── scripts/                     # Utility scripts
│   ├── dev.sh                   # Development startup
│   └── setup.sh                 # Initial setup
│
├── .bmad-core/                  # BMAD-Method agent configs
├── AGENTS.md                    # AI agent instructions
├── SETUP.md                     # Detailed setup guide
├── Makefile                     # Make commands
├── package.json                 # Root workspace config
└── README.md                    # This file
```

**Workspace Management:**

- **Root `package.json`**: Defines workspaces and unified scripts
- **Bun workspaces**: Shared dependencies, single lockfile
- **Unified commands**: `bun run dev`, `bun run test`, `bun run lint`

---

## 🎮 Available Commands

Run from **project root**:

| Command | Description |
|---------|-------------|
| `bun run dev` | Start both frontend + backend |
| `bun run dev:backend` | Start backend only |
| `bun run dev:frontend` | Start frontend only |
| `bun run test` | Run all tests |
| `bun run setup` | Run initial setup script |
| `make dev` | Alternative: start both servers |
| `make help` | Show all make commands |

**Backend-specific** (from `backend/`):

| Command | Description |
|---------|-------------|
| `uv run pytest` | Run backend tests |
| `uv run pytest --cov` | Run with coverage |
| `uvicorn src.main:app --reload` | Start dev server |

**Frontend-specific** (from `frontend/`):

| Command | Description |
|---------|-------------|
| `bun dev` | Start Next.js dev server |
| `bun test` | Run frontend tests |
| `bun run build` | Production build |

---

## 🔧 Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 15, React 19, TypeScript 5.7, Tailwind CSS 4, Zustand, Recharts |
| **Backend** | Python 3.11+, FastAPI, Pydantic 2, Loguru |
| **ML/AI** | scikit-learn, XGBoost, SHAP, LangChain, LangGraph, OpenAI GPT-4o |
| **Data** | Pandas, NumPy, Parquet, Joblib |
| **Streaming** | SSE (Server-Sent Events), sse-starlette |
| **External Data** | n8n workflows for weather, events, fuel prices |
| **Package Managers** | Bun (frontend), uv (backend) |
| **Validation** | Zod (shared schemas for FE/BE contract) |

---

## ⚠️ Package Manager Rules

This project enforces specific package managers:

| Context | ✅ Use | ❌ Never Use |
|---------|--------|-------------|
| **Frontend** | `bun add`, `bun install` | npm, yarn, pnpm |
| **Backend** | `uv pip install` | pip, pip3 |

---

## 📚 Detailed Documentation

### Deep Dive Documentation

- **[SETUP.md](SETUP.md)** - Detailed setup guide for AI agents
- **[Architecture Overview](docs/architecture/index.md)** - System design and components
- **[Tech Stack](docs/architecture/tech-stack.md)** - Technology decisions
- **[Coding Standards](docs/architecture/coding-standards.md)** - Code style guide
- **[Testing Strategy](docs/architecture/testing-strategy.md)** - Testing approach
- **[API Specification](docs/architecture/api-specification.md)** - REST API docs
- **[PRD](docs/prd/prd.md)** - Product requirements document

### Epic Documentation

- [Epic 1: Foundation & Data Pipeline](docs/prd/epic-1-foundation-data-pipeline.md)
- [Epic 2: ML Price Optimization](docs/prd/epic-2-ml-price-optimization.md)
- [Epic 3: Explainability & Full API](docs/prd/epic-3-explainability-full-api.md)
- [Epic 4: Frontend & Agent Integration](docs/prd/epic-4-frontend-agent-integration.md)

---

## 🤝 Contributing

We welcome contributions! When working with this codebase:

### Development Workflow

1. **Install prerequisites** (if not already installed):
   ```bash
   # Install Bun
   curl -fsSL https://bun.sh/install | bash && source ~/.bashrc
   
   # Install uv
   curl -LsSf https://astral.sh/uv/install.sh | sh && source ~/.bashrc
   ```

2. **First time setup**: Read and follow `SETUP.md` step by step

3. **Starting development**: Run `bun run dev` from project root

4. **Package installations**:
   - Frontend: `cd frontend && bun add <package>`
   - Backend: `cd backend && source .venv/bin/activate && uv pip install <package>`

5. **Running tests**: `bun run test` from project root

6. **Conda users**: Always run `conda deactivate` before working on this project

### Code Standards

- **TypeScript**: Strict mode, ESLint
- **Python**: Type hints, Ruff linting
- **Testing**: Unit + integration tests required
- **Commits**: Conventional commit messages

---

## 📍 Access Points

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Health Check | http://localhost:8000/health |
| OpenAPI Schema | http://localhost:8000/openapi.json |

---

## 👥 Team

| Name | Role |
|------|------|
| **Mario** | Team Lead & Solution Architect |
| **Grace** | Full Stack Engineer & ML Pipeline Architect |
| **David** | Frontend Experience Engineer |
| **Gabriel** | UI/UX & Visualization Engineer |

---

## 📄 License

Proprietary - All rights reserved.

---

## 🆘 Support

- **Documentation**: See `docs/` folder
- **Setup Issues**: Check `SETUP.md` troubleshooting section
- **Architecture Questions**: See `docs/architecture/`

---

**Built with Next.js 15, FastAPI, LangChain, XGBoost, and SHAP**
