# 12. Unified Project Structure

```plaintext
prismiq/
├── .github/
│   └── workflows/
│       └── ci.yaml                 # Future CI/CD
│
├── backend/                        # Python FastAPI
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── dependencies.py
│   │   │   ├── middleware/
│   │   │   └── routers/
│   │   ├── services/
│   │   ├── agent/
│   │   │   ├── agent.py
│   │   │   ├── tools/
│   │   │   └── prompts/
│   │   ├── ml/
│   │   │   ├── model_manager.py
│   │   │   ├── demand_simulator.py
│   │   │   ├── segmenter.py
│   │   │   └── preprocessor.py
│   │   ├── rules/
│   │   ├── explainability/
│   │   └── schemas/
│   ├── data/
│   │   ├── dynamic_pricing.xlsx
│   │   ├── models/
│   │   └── scenarios/
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── unit/
│   │   └── integration/
│   ├── pyproject.toml
│   ├── requirements.lock
│   ├── .python-version
│   └── .env.example
│
├── frontend/                       # Next.js 15
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── workspace/
│   │   │   ├── executive/
│   │   │   └── evidence/
│   │   ├── components/
│   │   │   ├── ui/
│   │   │   ├── chat/
│   │   │   ├── context/
│   │   │   ├── visualizations/
│   │   │   └── layout/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── stores/
│   │   ├── lib/
│   │   └── types/
│   ├── public/
│   │   ├── fonts/
│   │   └── images/
│   ├── tests/
│   │   ├── unit/
│   │   └── e2e/
│   ├── package.json
│   ├── bun.lockb
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── next.config.ts
│   ├── .npmrc
│   └── .env.local.example
│
├── packages/                       # Shared code
│   └── shared/
│       ├── src/
│       │   ├── types/
│       │   │   ├── index.ts
│       │   │   ├── market.ts
│       │   │   ├── pricing.ts
│       │   │   ├── chat.ts
│       │   │   └── scenario.ts
│       │   └── constants/
│       │       └── index.ts
│       ├── package.json
│       └── tsconfig.json
│
├── docs/                           # Documentation
│   ├── brief.md
│   ├── prd.md
│   ├── architecture.md             # This document
│   └── api/
│       └── openapi.yaml
│
├── scripts/                        # Development scripts
│   ├── setup.sh                    # Initial setup
│   ├── dev.sh                      # Start both services
│   └── train-models.py             # ML model training
│
├── .gitignore
├── .env.example
├── README.md
└── Makefile                        # Common commands
```

---
