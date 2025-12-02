# Epic 2: ML Models & Price Optimization

## Epic Goal

Build the behavioral demand simulator, train all three ML models on synthetic demand data, implement the price optimization loop, apply configurable business rules, and integrate external data via n8n workflows.

## Epic Context

**PRD Reference:** PrismIQ Dynamic Pricing Copilot  
**Priority:** P0 - Core ML Capability  
**Dependencies:** Epic 1 (Foundation & Data Pipeline)  
**Estimated Effort:** Sprint 2

---

## Stories

### Story 2.1: Behavioral Demand Simulator

**As a** data scientist,  
**I want** a demand simulator that models realistic price-demand relationships,  
**so that** I can generate training labels for ML models.

#### Acceptance Criteria

1. Demand simulator implemented in `backend/src/ml/demand_simulator.py` with configurable elasticity
2. Demand modulated by: supply/demand ratio, time of day, segment, loyalty tier
3. Reference pricing effect included (anchoring to historical cost)
4. Segment-specific sensitivity parameters (e.g., Premium less elastic than Economy)
5. Function signature: `simulate_demand(context: MarketContext, price: float, elasticity_params: dict, external_factors: dict) -> float`
6. Demand values bounded realistically (0.0 to 1.0 probability scale or absolute units)
7. Unit tests validate: demand decreases as price increases (negative elasticity)

#### Technical Notes

- **Elasticity Model:** Log-linear or constant elasticity of demand
- **Parameters:** Load from config file for easy tuning
- **Refer to:** Behavioral economics literature on price sensitivity

---

### Story 2.2: Synthetic Training Data Generation

**As a** data scientist,  
**I want** synthetic demand labels generated for the entire dataset,  
**so that** I have labeled training data.

#### Acceptance Criteria

1. For each row in dataset, generate demand at multiple price points (e.g., 10 price levels)
2. Price points span reasonable range (e.g., $5 to $100 in $10 increments)
3. Training dataset includes: context features, price, simulated demand, calculated profit
4. Profit calculated as `(price - cost) * demand`
5. Train/test split (80/20) with stratification by segment
6. Data saved to `/backend/data/processed/training_data.parquet`
7. Generation reproducible with random seed (default: 42)

#### Technical Notes

- **Output Format:** Parquet for efficiency, CSV fallback
- **Data Size:** ~10x original dataset rows (one per price point per context)
- **Script Location:** `backend/scripts/generate_training_data.py`

---

### Story 2.3: ML Model Training Pipeline

**As a** data scientist,  
**I want** three ML models trained to predict demand,  
**so that** I can compare performance and use the best predictor.

#### Acceptance Criteria

1. Training pipeline in `backend/src/ml/training.py`
2. **Linear Regression** trained as interpretable baseline
3. **Decision Tree** trained with `max_depth` tuning (grid search 3-10)
4. **Random Forest** (or XGBoost) trained with GridSearchCV for hyperparameters
5. All models predict demand given context features + price as input
6. Models evaluated with: R², MAE, RMSE on test set
7. Comparison table generated and logged
8. Models serialized to `backend/data/models/*.joblib`

#### Technical Notes

- **Primary Model:** XGBoost recommended for production (per architecture)
- **Model Manager:** `backend/src/ml/model_manager.py` loads and serves models
- **Refer to:** `docs/architecture/components.md` Section 6.1 (ML Pipeline)

---

### Story 2.4: Price Optimization Loop

**As a** pricing analyst,  
**I want** the system to find the profit-maximizing price,  
**so that** I receive optimal recommendations.

#### Acceptance Criteria

1. Optimization function in `backend/src/ml/price_optimizer.py`
2. Objective: Maximize `(price - cost) * predicted_demand(price)`
3. Price bounds configurable (default: $5 min, $200 max from Settings)
4. Returns: `optimal_price`, `expected_demand`, `expected_profit`, `profit_vs_baseline`
5. Baseline comparison using static historical price
6. Optimization completes in < 500ms per context
7. Unit tests verify optimizer finds known optimal on synthetic data

#### Technical Notes

- **Algorithm:** Grid search or scipy.optimize with demand model
- **Resolution:** Test prices at $0.50 increments within bounds
- **Caching:** Cache results for identical contexts (LRU)

---

### Story 2.5: Business Rules Layer

**As a** compliance officer,  
**I want** business rules applied to model-optimal prices,  
**so that** recommendations comply with policy.

#### Acceptance Criteria

1. Rules engine implemented in `backend/src/rules/engine.py`
2. Rules loaded from `backend/src/rules/config.yaml`
3. **Price Caps:** Max surge multiplier by segment/vehicle (default 3.0x)
4. **Price Floors:** Minimum price ensuring positive margin
5. **Fairness Constraints:** Surge caps for vulnerable segments
6. **FAR Compliance:** Government pricing rules (if applicable)
7. **Loyalty Discounts:** Tier-based discounts (Bronze 0%, Silver 5%, Gold 10%, Platinum 15%)
8. Rules applied in priority order, each application logged
9. Final price returned with list of rules triggered and their impact

#### Technical Notes

- **Rule Format:** YAML with conditions and actions
- **Rule Types:** See `docs/architecture/components.md` Section 6.1 (Rules Engine)
- **Logging:** Use loguru for rule application trace

---

### Story 2.6: Optimize Price Endpoint

**As a** frontend developer,  
**I want** an API endpoint that returns optimized price recommendations,  
**so that** the chat can display pricing guidance.

#### Acceptance Criteria

1. `POST /api/v1/optimize_price` endpoint accepts MarketContext
2. Returns: `recommended_price`, `confidence_score`, `expected_profit`, `profit_uplift_percent`
3. Returns: segment assignment and model used for prediction
4. Returns: list of business rules applied with individual impacts
5. Response time < 3 seconds (including all ML inference)
6. Error handling for invalid contexts (422) and model errors (500)
7. Documented in Swagger with example request/response

#### Technical Notes

- **Response Schema:** `PricingResult` from `docs/architecture/data-models.md`
- **Orchestration:** PricingService coordinates Segmenter → ML → Optimizer → Rules → Explainer
- **Refer to:** `docs/architecture/api-specification.md`

---

### Story 2.7: External Data Integration via n8n

**As a** pricing analyst,  
**I want** real-time external data factored into recommendations,  
**so that** pricing reflects current market conditions.

#### Acceptance Criteria

1. n8n instance configuration documented (localhost:5678)
2. **Fuel Price Workflow:** Fetches current fuel prices → impacts cost basis
3. **Weather Workflow:** Fetches weather conditions → impacts demand modifier
4. **Events Workflow:** Fetches local events → impacts surge factor
5. Each workflow exposes webhook endpoint (POST)
6. External data cached with TTL (weather 30min, events 1hr, traffic 5min)
7. Demand simulator accepts external modifiers from n8n data
8. `GET /api/v1/external_context` endpoint returns current external factors
9. Agent can articulate external factors in natural language explanations

#### Technical Notes

- **Fallback:** When n8n unavailable, use neutral defaults (see `docs/architecture/external-apis.md`)
- **Service:** `backend/src/services/external_service.py`
- **Caching:** File-based JSON cache with TTL

---

## Epic Definition of Done

- [ ] All 7 stories completed with acceptance criteria met
- [ ] ML models trained and serialized with documented metrics
- [ ] Price optimization returns results in < 3 seconds
- [ ] Business rules configurable via YAML
- [ ] All endpoints documented in Swagger
- [ ] Unit tests for ML pipeline (>80% coverage)
- [ ] Integration tests for `/optimize_price` endpoint
- [ ] n8n workflows documented (even if using mocks for demo)

## Technical References

| Document | Purpose |
|----------|---------|
| `docs/architecture/components.md` | ML Pipeline, Rules Engine specs |
| `docs/architecture/backend-architecture.md` | Service architecture |
| `docs/architecture/api-specification.md` | API contracts |
| `docs/architecture/data-models.md` | PricingResult schema |
| `docs/architecture/external-apis.md` | n8n integration |
| `docs/architecture/security-and-performance.md` | Performance targets |

