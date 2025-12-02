# 7. External APIs

## 7.1 OpenAI API (LLM Provider)

- **Purpose:** Powers the LangChain agent's natural language understanding and response generation
- **Documentation:** https://platform.openai.com/docs/api-reference
- **Base URL:** `https://api.openai.com/v1`
- **Authentication:** Bearer token (`OPENAI_API_KEY` env var)
- **Rate Limits:** Tier-dependent; typically 3,500 RPM for GPT-4o

**Key Endpoints:**
- `POST /chat/completions` - Agent reasoning and response generation

**Integration Notes:**
- Use GPT-4o for best tool-calling performance
- Temperature: 0.7 for conversational, 0.3 for structured outputs
- Max tokens: 2048 for responses, 4096 for complex analyses

**Error Handling:**
- 429 (Rate Limited): Exponential backoff with jitter
- 503 (Overloaded): Fallback to cached response or GPT-4o-mini
- Timeout (30s): Return graceful error with retry option

## 7.2 n8n Webhook (External Data Enrichment)

- **Purpose:** Fetches real-time external data (weather, events, traffic) and caches results
- **Base URL:** `http://localhost:5678/webhook/`
- **Authentication:** None (local development)

**Webhooks:**
- `POST /webhook/weather` - Current weather conditions
- `POST /webhook/events` - Local event detection
- `POST /webhook/traffic` - Traffic density estimation

**Response Caching:**
- Weather: 30 minutes TTL
- Events: 1 hour TTL
- Traffic: 5 minutes TTL

**Fallback Behavior:**
When n8n is unavailable, the system uses synthetic data:
- Weather: "Clear" (neutral impact)
- Events: None (no special event multiplier)
- Traffic: 0.5 (moderate)

---
