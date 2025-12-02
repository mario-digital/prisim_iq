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

