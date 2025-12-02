# 3. Tech Stack

## 3.1 Technology Stack Table

| Category | Technology | Version | Purpose | Rationale |
|----------|------------|---------|---------|-----------|
| **Frontend Language** | TypeScript | 5.7 | Type-safe JavaScript | Latest stable; strict mode catches errors at compile time |
| **Frontend Framework** | Next.js | 15.1 | React meta-framework | Latest stable (Dec 2024); App Router, Server Components |
| **UI Component Library** | shadcn/ui | latest | Accessible component primitives | Copy-paste components; Radix primitives; full customization |
| **Styling** | Tailwind CSS | 4.0 | Utility-first CSS | v4 stable (Dec 2024); CSS-first config; native cascade layers |
| **State Management** | Zustand | 5.0 | Lightweight React state | Simple API; TypeScript-first; devtools support |
| **Charts** | Recharts | 2.14 | React charting library | Composable; responsive; great defaults |
| **HTTP Client** | ky | 1.7 | Fetch wrapper | Tiny; retry logic; typed responses |
| **JS Runtime** | Bun | 1.1.38+ | JavaScript runtime & package manager | Fastest runtime; built-in bundler; npm compatible |
| **Backend Language** | Python | 3.12 | ML and API development | Latest stable; performance improvements |
| **Backend Framework** | FastAPI | 0.115 | Async Python web framework | Auto OpenAPI; Pydantic v2 native; async-first |
| **ML Framework** | scikit-learn | 1.5 | Machine learning | Stable; XGBoost integration |
| **Gradient Boosting** | XGBoost | 2.1 | Price prediction models | State-of-the-art for tabular data |
| **Explainability** | SHAP | 0.46 | Model interpretation | Industry standard; feature importance |
| **Agent Framework** | LangChain | 0.3 | LLM orchestration | Tool-calling; conversation memory |
| **LLM Provider** | OpenAI | GPT-4o | Large language model | Best reasoning for agentic tasks |
| **Python Package Manager** | uv | 0.5+ | Fast Python package management | 10-100x faster than pip; lockfile support |
| **Python Environment** | venv | built-in | Virtual environment | Standard; no external deps |
| **Data Processing** | Pandas | 2.2 | DataFrame operations | Industry standard; Excel support |
| **Logging** | Loguru | 0.7 | Structured logging | Zero config; beautiful output |
| **Validation** | Pydantic | 2.10 | Data validation | FastAPI native; TypeScript-like |

## 3.2 Package Manager Enforcement

**Frontend (Bun):**
```jsonc
// frontend/package.json
{
  "packageManager": "bun@1.1.38",
  "engines": {
    "bun": ">=1.1.38",
    "node": ">=22.0.0"
  },
  "scripts": {
    "preinstall": "npx only-allow bun"
  }
}
```

**npm/pnpm Disabled:**
```ini
# frontend/.npmrc
engine-strict=true
package-manager-strict=true
```

**Backend (uv with venv):**
```toml
# backend/pyproject.toml
[project]
requires-python = ">=3.12"

[tool.uv]
python-preference = "only-system"
```

## 3.3 Environment Setup

```bash
# Verify Bun (disables npm/pnpm)
cd frontend
bun install  # Creates bun.lockb, ignores package-lock.json

# Python virtual environment with uv
cd backend
uv venv                    # Creates .venv/
source .venv/bin/activate  # Activate
uv pip sync requirements.lock  # Install from lockfile
```

---
