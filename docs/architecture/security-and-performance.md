# 15. Security and Performance

## 15.1 Security Requirements

```yaml
Frontend:
  XSS Prevention:
    - React built-in escaping
    - No dangerouslySetInnerHTML
    - Markdown sanitization
  Storage:
    - No sensitive data in localStorage
    - Context/scenarios only

Backend:
  Input Validation:
    - Pydantic models on all endpoints
    - Type coercion and range checks
  API Security:
    - CORS restricted to frontend origin
    - Rate limiting (100 req/min/IP)
  Secrets:
    - Environment variables only
    - No hardcoded credentials
  
LLM Security:
  - Prompt injection guards
  - Output sanitization
  - Token limits enforced
```

## 15.2 Performance Targets

```yaml
Frontend:
  First Contentful Paint: < 1.5s
  Time to Interactive: < 3s
  Largest Contentful Paint: < 2.5s
  Bundle Size: < 200KB (gzipped)

Backend:
  P50 Response Time: < 200ms (non-LLM)
  P95 Response Time: < 500ms (non-LLM)
  LLM Response Time: < 5s (streaming)
  Throughput: 50 req/sec

ML Pipeline:
  Model Load: < 2s (cold start)
  Inference: < 100ms
  Demand Simulation: < 500ms
```

## 15.3 Caching Strategy

```yaml
Frontend:
  - React Query for API responses (5 min stale time)
  - localStorage for scenarios
  - Session storage for chat history

Backend:
  - LRU cache for model predictions (1000 entries)
  - File cache for n8n responses (TTL-based)
  - In-memory segment cache
```

---
