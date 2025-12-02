# PrismIQ Development Setup Guide

> **For AI Agents & Developers:** Follow these steps exactly to avoid common setup issues.

## Prerequisites

### Install Bun (JavaScript runtime & package manager)

```bash
# Check if Bun is installed
bun --version

# If not installed or command not found, install it:
curl -fsSL https://bun.sh/install | bash

# Reload shell to get bun in PATH
source ~/.bashrc  # or ~/.zshrc for zsh users

# Verify installation
bun --version   # Should show 1.1.38 or higher
```

### Install uv (Python package manager)

```bash
# Check if uv is installed
uv --version

# If not installed or command not found, install it:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Reload shell to get uv in PATH
source ~/.bashrc  # or ~/.zshrc for zsh users

# Verify installation
uv --version    # Should show 0.5 or higher
```

### Prerequisites Summary

| Tool | Version | Status Check | Install Command |
|------|---------|--------------|-----------------|
| **Bun** | 1.1.38+ | `bun --version` | `curl -fsSL https://bun.sh/install \| bash` |
| **uv** | 0.5+ | `uv --version` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |

---

## ⚠️ Critical: Conda/Anaconda Users

If you have Conda installed, you **MUST** deactivate it before setting up this project:

```bash
# Check if conda is active (look for "base" or environment name in prompt)
conda deactivate

# Verify conda is deactivated
echo $CONDA_DEFAULT_ENV  # Should be empty
```

**Why?** Conda's Python and packages will interfere with the project's virtual environment, causing import errors even after installing dependencies.

---

## Step 1: Clone & Navigate

```bash
cd /path/to/your/projects
git clone <repository-url> prisim_iq
cd prisim_iq

# Make scripts executable (one time)
chmod +x scripts/dev.sh scripts/setup.sh
```

---

## Step 2: Backend Setup

### 2.1 Navigate to Backend
```bash
cd backend
```

### 2.2 Deactivate Conda (if applicable)
```bash
# CRITICAL: Do this BEFORE creating the venv
conda deactivate 2>/dev/null || true
```

### 2.3 Create Virtual Environment
```bash
uv venv
```

**Expected output:**
```
Using CPython 3.11.x
Creating virtual environment at: .venv
Activate with: source .venv/bin/activate
```

> **Troubleshooting:** If you see "No interpreter found for Python 3.11", uv will download it automatically (the pyproject.toml has `python-preference = "managed"`).

### 2.4 Activate Virtual Environment
```bash
source .venv/bin/activate
```

### 2.5 Verify Correct Python
```bash
which python
```

**Expected output:**
```
/path/to/prisim_iq/backend/.venv/bin/python
```

❌ **If it shows `/opt/anaconda3/...` or similar, conda is still active. Run `conda deactivate` and try again.**

### 2.6 Install Dependencies
```bash
uv pip install -r requirements.lock
```

### 2.7 Install Dev Dependencies (pytest, etc.)
```bash
uv pip install pytest pytest-asyncio httpx
```

### 2.8 Verify pytest is from venv
```bash
which pytest
```

**Expected output:**
```
/path/to/prisim_iq/backend/.venv/bin/pytest
```

❌ **If it shows `/opt/anaconda3/bin/pytest`, run:**
```bash
hash -r  # Clear shell's command cache
which pytest  # Should now show venv path
```

### 2.9 Create Environment File
```bash
cp .env.example .env
```

### 2.10 Run Tests
```bash
pytest -v
```

**Expected output:**
```
tests/unit/test_health.py::test_health_check_returns_healthy PASSED
tests/unit/test_health.py::test_health_check_version_format PASSED
tests/unit/test_health.py::test_root_endpoint PASSED
```

### 2.11 Start Backend Server
```bash
uvicorn src.main:app --reload
```

### 2.12 Verify Health Endpoint
Open in browser or run:
```bash
curl http://localhost:8000/health
```

**Expected response:**
```json
{"status":"healthy","version":"1.0.0","timestamp":"2024-..."}
```

✅ **Backend setup complete!** Keep this terminal running or press `Ctrl+C` to stop.

---

## Step 3: Frontend Setup

Open a **new terminal** for frontend.

### 3.1 Navigate to Frontend
```bash
cd /path/to/prisim_iq/frontend
```

### 3.2 Install Dependencies
```bash
bun install
```

**Note:** This project uses Bun exclusively. Do NOT use `npm install` or `yarn install`.

### 3.3 Create Environment File
```bash
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

### 3.4 Start Frontend Server
```bash
bun run dev
```

### 3.5 Verify Frontend
Open browser to: **http://localhost:3000**

**Expected:** PrismIQ landing page with "Dynamic Pricing Copilot" text.

✅ **Frontend setup complete!**

---

## Step 4: Shared Package Setup (Optional)

Only needed if you're modifying shared types:

```bash
cd /path/to/prisim_iq/packages/shared
bun install
```

---

## Quick Start (After Initial Setup)

Once setup is complete, use these commands for daily development:

### Start Both Services (Recommended)
From the project root:
```bash
cd /path/to/prisim_iq
bun run dev
```

This single command starts both frontend and backend servers. Press `Ctrl+C` to stop both.

### Alternative: Start Services Individually
```bash
# Backend only
bun run dev:backend

# Frontend only  
bun run dev:frontend
```

### Or Use Make Commands
```bash
make dev  # Starts both (requires initial setup complete)
```

### Run Tests
```bash
# All tests
bun run test

# Or individually
bun run test:backend
bun run test:frontend
```

---

## Common Issues & Solutions

### Issue: `ModuleNotFoundError: No module named 'loguru'`

**Cause:** Wrong Python/pytest being used (usually Anaconda's).

**Solution:**
```bash
conda deactivate
source .venv/bin/activate
which python  # Verify it's the venv python
uv pip install -r requirements.lock --reinstall
```

### Issue: `pytest` still uses Anaconda after installing in venv

**Solution:**
```bash
hash -r  # Clear shell command cache
which pytest  # Should now show venv path
```

### Issue: `No interpreter found for Python 3.11`

**Solution:** The `pyproject.toml` is configured to allow uv to download Python. Just run:
```bash
uv venv
```
It will automatically download Python 3.11.

### Issue: `npm install` or `yarn add` fails in frontend

**Cause:** This project enforces Bun only.

**Solution:** Always use `bun` commands:
```bash
bun install        # Instead of npm install
bun add <package>  # Instead of npm install <package>
bun run dev        # Instead of npm run dev
```

### Issue: Frontend can't connect to backend API

**Solution:** 
1. Ensure backend is running on port 8000
2. Check `frontend/.env.local` contains: `NEXT_PUBLIC_API_URL=http://localhost:8000`
3. Restart frontend after creating `.env.local`

---

## Available Commands (from project root)

| Command | Description |
|---------|-------------|
| `bun run dev` | Start both frontend and backend servers |
| `bun run dev:backend` | Start backend only |
| `bun run dev:frontend` | Start frontend only |
| `bun run test` | Run all tests |
| `bun run test:backend` | Run backend tests only |
| `bun run test:frontend` | Run frontend tests only |
| `bun run setup` | Run initial setup script |
| `make dev` | Alternative: start both servers |
| `make help` | Show all make commands |

---

## Environment Summary

| Service | URL | Port |
|---------|-----|------|
| Frontend | http://localhost:3000 | 3000 |
| Backend API | http://localhost:8000 | 8000 |
| API Docs | http://localhost:8000/docs | 8000 |
| Health Check | http://localhost:8000/health | 8000 |

---

## Package Manager Rules

| Context | Use | Never Use |
|---------|-----|-----------|
| Frontend | `bun` | `npm`, `yarn`, `pnpm` |
| Backend | `uv pip` | `pip`, `pip3` |

---

## Verification Checklist

After setup, verify all checkpoints:

- [ ] `which python` shows `.venv/bin/python` (in backend dir with venv active)
- [ ] `which pytest` shows `.venv/bin/pytest`
- [ ] `pytest -v` passes all 3 tests
- [ ] `curl http://localhost:8000/health` returns healthy
- [ ] http://localhost:3000 shows PrismIQ page
- [ ] No Conda environment is active during development
- [ ] `bun run dev` from project root starts both servers

