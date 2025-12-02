# 6. Components

## 6.1 Backend Components

### API Layer

**Responsibility:** HTTP request handling, routing, validation, and response formatting.

**Key Interfaces:**
- `POST /optimize_price` → PricingRouter
- `POST /chat` → ChatRouter
- `GET /health` → HealthRouter

**Dependencies:** All backend services (injected)

**Technology:** FastAPI routers, Pydantic models, CORS middleware

```
backend/src/api/
├── __init__.py
├── main.py              # FastAPI app factory
├── dependencies.py      # DI container
├── middleware/
│   ├── cors.py
│   ├── logging.py
│   └── timing.py
└── routers/
    ├── health.py
    ├── data.py
    ├── chat.py
    ├── pricing.py
    └── scenarios.py
```

### LangChain Agent

**Responsibility:** Orchestrates conversation flow, determines user intent, invokes appropriate tools, formats responses.

**Key Interfaces:**
- `process_message(message, context) → AgentResponse`
- `stream_message(message, context) → AsyncGenerator[str]`

**Tools Exposed:**
- `optimize_price`: Get optimal price for context
- `analyze_segment`: Deep dive into customer segment
- `compare_scenarios`: Compare multiple scenarios
- `get_demand_curve`: Fetch demand elasticity data
- `explain_factors`: Get SHAP-based explanations

**Technology:** LangChain 0.3, OpenAI GPT-4o, Tool-calling pattern

```
backend/src/agent/
├── __init__.py
├── agent.py             # Main agent class
├── tools/
│   ├── __init__.py
│   ├── pricing_tool.py
│   ├── analysis_tool.py
│   ├── scenario_tool.py
│   └── visualization_tool.py
├── prompts/
│   ├── system.py
│   └── templates.py
└── memory/
    └── conversation.py
```

### ML Pipeline

**Responsibility:** Data loading, model training, prediction, and demand simulation.

**Key Interfaces:**
- `ModelManager.predict(context) → PricePrediction`
- `DemandSimulator.simulate(price_range, context) → DemandCurve`
- `Segmenter.classify(context) → SegmentResult`

**Models:**
- XGBoost regressor for price prediction
- Demand elasticity model per segment
- Customer segmentation classifier

**Technology:** scikit-learn, XGBoost, pandas, numpy

```
backend/src/ml/
├── __init__.py
├── model_manager.py     # Model loading and inference
├── demand_simulator.py  # Demand curve generation
├── segmenter.py         # Customer segmentation
├── preprocessor.py      # Feature engineering
└── models/              # Serialized models (.joblib)
    ├── price_predictor.joblib
    ├── demand_model.joblib
    └── segmenter.joblib
```

### Services

**Responsibility:** Business logic encapsulation, orchestration between ML and rules.

```
backend/src/services/
├── __init__.py
├── pricing_service.py   # Price optimization orchestration
├── data_service.py      # Dataset access and summaries
├── scenario_service.py  # Scenario CRUD operations
└── external_service.py  # n8n webhook integration
```

### Rules Engine

**Responsibility:** Apply business constraints and guardrails to ML predictions.

**Key Interfaces:**
- `evaluate(prediction, context) → RulesResult`

**Rules:**
- Max surge multiplier (3.0x)
- Loyalty discounts (5-20% by tier)
- Floor/ceiling prices by segment
- Competition-based adjustments

```
backend/src/rules/
├── __init__.py
├── engine.py           # Rule evaluation engine
├── rules/
│   ├── surge_limits.py
│   ├── loyalty.py
│   ├── price_bounds.py
│   └── competition.py
└── config.yaml         # Rule parameters
```

### Explainability

**Responsibility:** Generate human-readable explanations for pricing decisions.

**Key Interfaces:**
- `explain(prediction, context) → PriceExplanation`

**Technology:** SHAP, custom narrative generation

```
backend/src/explainability/
├── __init__.py
├── shap_explainer.py   # SHAP value calculation
├── narrative.py        # Natural language generation
└── visualizations.py   # Chart data preparation
```

## 6.2 Frontend Components

### App Shell

**Responsibility:** Root layout, navigation, and global providers.

```
frontend/src/app/
├── layout.tsx          # Root layout with providers
├── page.tsx            # Redirect to /workspace
├── workspace/page.tsx  # Main analyst workspace
├── executive/page.tsx  # Executive summary view
└── evidence/page.tsx   # Evidence & methods view
```

### Chat Components

**Responsibility:** Conversational interface, message rendering, input handling.

```
frontend/src/components/chat/
├── ChatPanel.tsx       # Main chat container
├── MessageList.tsx     # Message history
├── Message.tsx         # Individual message
├── ChatInput.tsx       # User input with suggestions
├── ToolResult.tsx      # Tool execution display
└── StreamingMessage.tsx # Animated typing effect
```

### Visualization Components

**Responsibility:** Data visualization and chart rendering.

```
frontend/src/components/visualizations/
├── DemandCurve.tsx     # Demand elasticity chart
├── FeatureImportance.tsx # SHAP waterfall chart
├── PriceComparison.tsx # Scenario comparison
├── SegmentAnalysis.tsx # Segment breakdown
└── OptimalPriceGauge.tsx # Price recommendation dial
```

### Context Components

**Responsibility:** Market context input and management.

```
frontend/src/components/context/
├── ContextPanel.tsx    # Collapsible context panel
├── LocationSelector.tsx
├── DemandSliders.tsx   # Riders/drivers inputs
├── CustomerProfile.tsx # Segment and loyalty
└── ScenarioManager.tsx # Save/load scenarios
```

---
