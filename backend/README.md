# PrismIQ Backend

FastAPI backend for the PrismIQ Dynamic Pricing Copilot.

## Setup

```bash
uv venv
source .venv/bin/activate
uv pip sync requirements.lock
```

## Development

```bash
uvicorn src.main:app --reload
```

## Testing

```bash
pytest
```

## External Data Integration (n8n)

PrismIQ integrates with n8n for real-time external data that affects pricing:

- **Fuel Prices**: Impacts cost basis calculations
- **Weather**: Impacts demand modifiers (rainy +15%, snowy +30%)
- **Events**: Impacts surge factors (concert +20%, sports +25%, convention +15%)

### n8n Setup

1. Install and run n8n locally:
   ```bash
   npx n8n
   # Or via Docker:
   docker run -it --rm -p 5678:5678 n8nio/n8n
   ```

2. Access n8n at `http://localhost:5678`

3. Create workflows that POST to PrismIQ webhooks:

### Webhook Endpoints

| Endpoint | Method | Purpose | TTL |
|----------|--------|---------|-----|
| `/api/v1/external/webhook/fuel` | POST | Receive fuel price updates | 1 hour |
| `/api/v1/external/webhook/weather` | POST | Receive weather conditions | 30 min |
| `/api/v1/external/webhook/events` | POST | Receive local events | 1 hour |

### Webhook Payload Examples

**Fuel Prices:**
```json
{
  "price_per_gallon": 3.75,
  "change_percent": 2.5,
  "source": "n8n-fuel-workflow"
}
```

**Weather:**
```json
{
  "condition": "rainy",
  "temperature_f": 65.0,
  "source": "n8n-weather-workflow"
}
```

**Events:**
```json
{
  "events": [
    {
      "name": "Taylor Swift Concert",
      "type": "concert",
      "venue": "City Arena",
      "start_time": "2024-12-15T19:00:00",
      "radius_miles": 5.0
    }
  ]
}
```

### Fallback Behavior

When n8n is unavailable or no data has been received, the system uses neutral defaults:
- **Fuel**: Uses baseline cost (no adjustment)
- **Weather**: Assumes "cloudy" (1.0 modifier)
- **Events**: Empty list (no surge)

### Viewing Current External Context

```bash
curl http://localhost:8000/api/v1/external/context
```

Returns current cached external factors with freshness information.

