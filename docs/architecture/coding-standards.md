# 17. Coding Standards

## 17.0 CRITICAL: Package Manager Rules for AI Agents

> ⚠️ **AI AGENTS MUST READ THIS SECTION FIRST**

### JavaScript/TypeScript: Bun ONLY

**NEVER use npm, pnpm, yarn, or npx.** This project uses Bun exclusively.

```bash
# ❌ FORBIDDEN - DO NOT USE
npm install <package>
npm run <script>
npx <command>
pnpm install <package>
yarn add <package>

# ✅ CORRECT - ALWAYS USE BUN
bun add <package>           # Install dependency
bun add -d <package>        # Install dev dependency
bun install                 # Install all dependencies
bun run <script>            # Run package.json script
bun run dev                 # Start development server
bun run build               # Build for production
bun run test                # Run tests
bunx <command>              # Execute package binary (replaces npx)
```

**Why Bun?**
- 10-100x faster than npm/yarn/pnpm
- Built-in bundler and test runner
- Native TypeScript execution
- npm/pnpm are disabled via `.npmrc` configuration

### Python: uv with Virtual Environment

**ALWAYS activate the virtual environment before running Python commands.**

```bash
# ❌ FORBIDDEN - DO NOT USE
pip install <package>
pip install -r requirements.txt
python -m pip install <package>

# ✅ CORRECT - ALWAYS USE UV
cd backend                          # Navigate to backend directory
source .venv/bin/activate           # ALWAYS activate venv first!

# After venv is activated:
uv pip install <package>            # Install single package
uv pip install -r requirements.txt  # Install from requirements
uv pip sync requirements.lock       # Install exact versions from lockfile
uv pip freeze > requirements.lock   # Update lockfile after changes

# Running Python
python src/main.py                  # Run Python script (venv must be active)
uvicorn src.main:app --reload       # Start FastAPI dev server
pytest                              # Run tests
```

**Virtual Environment Setup (if .venv doesn't exist):**
```bash
cd backend
uv venv                             # Create .venv directory
source .venv/bin/activate           # Activate it
uv pip sync requirements.lock       # Install dependencies
```

**Why uv?**
- 10-100x faster than pip
- Reliable lockfile format
- Handles dependency resolution correctly
- Virtual environment ensures consistent dependencies across all developers

### Quick Reference Card

| Task | Frontend (Bun) | Backend (uv) |
|------|----------------|--------------|
| Install deps | `bun install` | `source .venv/bin/activate && uv pip sync requirements.lock` |
| Add package | `bun add <pkg>` | `uv pip install <pkg>` |
| Run dev server | `bun run dev` | `uvicorn src.main:app --reload` |
| Run tests | `bun run test` | `pytest` |
| Build | `bun run build` | N/A (Python doesn't build) |

---

## 17.1 Critical Rules

1. **Type Sharing:** Define shared types in `packages/shared/src/types/`. Never duplicate types.

2. **API Calls:** Use service layer (`services/*.ts`). Never direct `fetch()` in components.

3. **Environment Variables:** 
   - Frontend: `process.env.NEXT_PUBLIC_*` only
   - Backend: via `Settings` class, never `os.getenv()` directly

4. **Error Handling:** All service calls wrapped in try/catch. Components show user-friendly errors.

5. **Async/Await:** Use async/await everywhere. No raw Promises or callbacks.

6. **Naming:**
   - React components: PascalCase (`ChatPanel.tsx`)
   - Python modules: snake_case (`pricing_service.py`)
   - TypeScript utilities: camelCase (`formatPrice.ts`)

## 17.2 Frontend Standards

```typescript
// Component structure
// 1. Imports
// 2. Types
// 3. Component
// 4. Styles (if any)

'use client'; // Only when needed

import { useState } from 'react';
import type { FC } from 'react';
import type { MarketContext } from '@prismiq/shared';

interface Props {
  context: MarketContext;
  onUpdate: (context: MarketContext) => void;
}

export const ContextPanel: FC<Props> = ({ context, onUpdate }) => {
  // Hooks first
  const [isOpen, setIsOpen] = useState(true);
  
  // Handlers
  const handleChange = (field: keyof MarketContext, value: unknown) => {
    onUpdate({ ...context, [field]: value });
  };
  
  // Render
  return (
    <div className="p-4">
      {/* JSX */}
    </div>
  );
};
```

## 17.3 Backend Standards

```python
# Service structure
# 1. Imports
# 2. Logger
# 3. Class

from loguru import logger
from src.schemas.market import MarketContext
from src.schemas.pricing import PricingResult

class PricingService:
    """Service for price optimization orchestration."""
    
    def __init__(
        self,
        model_manager: ModelManager,
        rules_engine: RulesEngine,
    ) -> None:
        self._model_manager = model_manager
        self._rules_engine = rules_engine
    
    async def optimize_price(
        self,
        context: MarketContext,
    ) -> PricingResult:
        """
        Optimize price for the given market context.
        
        Args:
            context: Market conditions and customer profile.
            
        Returns:
            Complete pricing result with explanation.
            
        Raises:
            ValidationError: If context is invalid.
            ModelError: If prediction fails.
        """
        logger.info(f"Optimizing price for segment: {context.customer_segment}")
        
        # Implementation
        ...
```

---
