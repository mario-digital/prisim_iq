# 11. Backend Architecture

## 11.1 Service Architecture

```
backend/
├── src/
│   ├── __init__.py
│   ├── main.py                   # FastAPI app factory
│   ├── config.py                 # Settings (pydantic-settings)
│   │
│   ├── api/                      # HTTP layer
│   │   ├── __init__.py
│   │   ├── dependencies.py       # Dependency injection
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   ├── cors.py
│   │   │   ├── logging.py
│   │   │   └── timing.py
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── health.py
│   │       ├── data.py
│   │       ├── chat.py
│   │       ├── pricing.py
│   │       └── scenarios.py
│   │
│   ├── services/                 # Business logic
│   │   ├── __init__.py
│   │   ├── pricing_service.py
│   │   ├── data_service.py
│   │   ├── scenario_service.py
│   │   └── external_service.py
│   │
│   ├── agent/                    # LangChain agent
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── pricing_tool.py
│   │   │   ├── analysis_tool.py
│   │   │   └── scenario_tool.py
│   │   └── prompts/
│   │       ├── system.py
│   │       └── templates.py
│   │
│   ├── ml/                       # Machine learning
│   │   ├── __init__.py
│   │   ├── model_manager.py
│   │   ├── demand_simulator.py
│   │   ├── segmenter.py
│   │   └── preprocessor.py
│   │
│   ├── rules/                    # Business rules
│   │   ├── __init__.py
│   │   ├── engine.py
│   │   └── rules/
│   │       ├── surge_limits.py
│   │       ├── loyalty.py
│   │       └── price_bounds.py
│   │
│   ├── explainability/           # SHAP + narratives
│   │   ├── __init__.py
│   │   ├── shap_explainer.py
│   │   └── narrative.py
│   │
│   └── schemas/                  # Pydantic models
│       ├── __init__.py
│       ├── market.py
│       ├── pricing.py
│       ├── chat.py
│       └── scenario.py
│
├── data/
│   ├── dynamic_pricing.xlsx      # Source dataset
│   ├── models/                   # Trained models
│   │   ├── price_predictor.joblib
│   │   ├── demand_model.joblib
│   │   └── segmenter.joblib
│   └── scenarios/                # Saved scenarios (JSON)
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_ml/
│   │   ├── test_rules/
│   │   └── test_services/
│   └── integration/
│       ├── test_api/
│       └── test_agent/
│
├── pyproject.toml                # Project config
├── requirements.lock             # Locked dependencies
└── .python-version               # Python version (3.12)
```

## 11.2 Dependency Injection

```python
# src/api/dependencies.py
from functools import lru_cache
from src.config import Settings
from src.ml.model_manager import ModelManager
from src.ml.demand_simulator import DemandSimulator
from src.ml.segmenter import Segmenter
from src.rules.engine import RulesEngine
from src.explainability.shap_explainer import ShapExplainer
from src.services.pricing_service import PricingService

@lru_cache
def get_settings() -> Settings:
    return Settings()

@lru_cache
def get_model_manager() -> ModelManager:
    return ModelManager()

@lru_cache
def get_demand_simulator() -> DemandSimulator:
    return DemandSimulator()

@lru_cache
def get_segmenter() -> Segmenter:
    return Segmenter()

@lru_cache
def get_rules_engine() -> RulesEngine:
    return RulesEngine()

@lru_cache
def get_shap_explainer() -> ShapExplainer:
    return ShapExplainer(get_model_manager())

def get_pricing_service(
    model_manager: ModelManager = Depends(get_model_manager),
    demand_simulator: DemandSimulator = Depends(get_demand_simulator),
    segmenter: Segmenter = Depends(get_segmenter),
    rules_engine: RulesEngine = Depends(get_rules_engine),
    explainer: ShapExplainer = Depends(get_shap_explainer),
) -> PricingService:
    return PricingService(
        model_manager=model_manager,
        demand_simulator=demand_simulator,
        segmenter=segmenter,
        rules_engine=rules_engine,
        explainer=explainer,
    )
```

## 11.3 Configuration Management

```python
# src/config.py
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False
    
    # OpenAI
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = "gpt-4o"
    openai_temperature: float = 0.7
    
    # n8n
    n8n_webhook_base: str = "http://localhost:5678/webhook"
    n8n_enabled: bool = True
    
    # Paths
    data_path: str = "data/dynamic_pricing.xlsx"
    models_path: str = "data/models"
    scenarios_path: str = "data/scenarios"
    
    # Pricing
    max_surge_multiplier: float = 3.0
    min_price: float = 5.0
    max_price: float = 200.0
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
```

---
