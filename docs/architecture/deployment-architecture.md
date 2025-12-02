# 14. Deployment Architecture

## 14.1 Local Deployment (Hackathon)

```yaml
Frontend:
  Platform: Local (Bun)
  Build: bun run build
  Start: bun run start
  Port: 3000

Backend:
  Platform: Local (uvicorn)
  Start: uvicorn src.main:app --host 0.0.0.0 --port 8000
  Port: 8000

n8n (optional):
  Platform: Local
  Start: n8n start
  Port: 5678
```

**Quick Start:**
```bash
# Terminal 1 - Backend
cd backend && source .venv/bin/activate
uvicorn src.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend && bun run dev

# Access at http://localhost:3000
```

## 14.2 Production Reference Architecture

```yaml
# Future deployment (out of scope for hackathon)
Frontend:
  Platform: Vercel
  Framework: Next.js
  CDN: Vercel Edge Network

Backend:
  Platform: Railway / Render
  Runtime: Python 3.12
  Workers: 2-4 (gunicorn + uvicorn)

Database:
  Platform: Supabase (PostgreSQL)
  
ML Models:
  Storage: S3 / Cloudflare R2
  
LLM:
  Provider: OpenAI API
  Fallback: Azure OpenAI
```

---
