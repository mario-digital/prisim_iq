# 19. Monitoring and Observability

## 19.1 Logging Strategy

```yaml
Frontend:
  Tool: Browser console + React DevTools
  Levels: error, warn, info, debug
  
Backend:
  Tool: Loguru
  Format: JSON (production), colored (development)
  Correlation: X-Request-ID header
  
Log Levels:
  ERROR: Exceptions, failed operations
  WARNING: Degraded behavior, fallbacks used
  INFO: Request/response summary, key events
  DEBUG: Detailed execution, ML parameters
```

## 19.2 Metrics (Future)

```yaml
# Key metrics to track post-hackathon
API:
  - Request count by endpoint
  - Response time percentiles (p50, p95, p99)
  - Error rate by type
  
ML:
  - Prediction latency
  - Model confidence distribution
  - Feature importance drift
  
Business:
  - Scenarios created per session
  - Price recommendations accepted
  - Chat messages per session
```

## 19.3 Health Check Implementation

```python
# backend/src/api/routers/health.py
@router.get("/health")
async def health_check(
    model_manager: ModelManager = Depends(get_model_manager),
) -> HealthResponse:
    checks = {
        "api": True,
        "models": model_manager.is_loaded(),
        "openai": await check_openai_connection(),
        "n8n": await check_n8n_connection(),
    }
    
    status = "healthy" if all(checks.values()) else "degraded"
    
    return HealthResponse(
        status=status,
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat(),
        checks=checks,
    )
```

---
