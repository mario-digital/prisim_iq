# Epic 3: Explainability & Full API

## Epic Goal

Implement comprehensive explainability outputs including feature importance, decision traces, sensitivity analysis, and model/data cards. Complete the full REST API surface for all pricing and analysis features.

## Epic Context

**PRD Reference:** PrismIQ Dynamic Pricing Copilot  
**Priority:** P0 - Core Differentiator  
**Dependencies:** Epic 2 (ML Models & Price Optimization)  
**Estimated Effort:** Sprint 3

---

## Stories

### Story 3.1: Feature Importance Calculation

**As a** pricing analyst,  
**I want** to see which factors most influenced the recommendation,  
**so that** I can understand and explain decisions to stakeholders.

#### Acceptance Criteria

1. Feature importance extracted from Random Forest/XGBoost `feature_importances_` attribute
2. Linear Regression coefficients normalized to percentage scale
3. Decision Tree importances extracted via `feature_importances_`
4. **Per-prediction importance** using SHAP values (not just global importance)
5. Results returned as ranked list with percentages (sum to 100%)
6. Top 3 features include plain-English descriptions (e.g., "High demand-to-supply ratio (+32%)")
7. Unit tests verify: all importance values sum to 1.0 (within tolerance)

#### Technical Notes

- **SHAP Integration:** `backend/src/explainability/shap_explainer.py`
- **Library:** SHAP 0.46 for local explanations
- **Refer to:** `docs/architecture/components.md` Section 6.1 (Explainability)

---

### Story 3.2: Decision Trace Generation

**As a** pricing analyst,  
**I want** a step-by-step trace of how the system arrived at a price,  
**so that** I can audit decisions.

#### Acceptance Criteria

1. Trace captures complete pipeline: Input → Segment → External Factors → Model Prediction → Optimization → Rules → Final Price
2. Each step includes: timestamp, duration (ms), input values, output values
3. Trace exportable as JSON (API response) and formatted text (for display)
4. Model agreement indicator: shows if all models agree within 10% or diverge
5. Trace stored for audit purposes (optional file logging)

#### Technical Notes

- **Implementation:** Decorator pattern or context manager to capture timing
- **Storage:** In-memory for response, optional file append for audit log
- **Schema:** Part of `PriceExplanation` in `docs/architecture/data-models.md`

---

### Story 3.3: Sensitivity Analysis Engine

**As a** pricing analyst,  
**I want** to see how recommendations change under different assumptions,  
**so that** I can assess robustness and communicate uncertainty.

#### Acceptance Criteria

1. **Elasticity sensitivity:** Recalculate at ±10%, ±20%, ±30% elasticity
2. **Demand sensitivity:** Recalculate at ±10%, ±20% demand modifier
3. **Cost sensitivity:** Recalculate at ±5%, ±10% cost changes
4. Results returned as visualization-ready arrays (price vs. scenario)
5. Confidence band calculated (min/max recommended price across scenarios)
6. Worst-case and best-case scenarios highlighted in response

#### Technical Notes

- **Implementation:** `backend/src/services/sensitivity_service.py`
- **Performance:** Run scenarios in parallel (asyncio) to meet latency target
- **Caching:** Cache base prediction, vary only sensitivity parameters

---

### Story 3.4: Model Cards & Data Cards

**As an** auditor,  
**I want** standardized documentation of models and data,  
**so that** I can assess reliability and compliance.

#### Acceptance Criteria

1. **Model Card** per model (Random Forest, Decision Tree, Linear Regression) following Google Model Cards format
2. Each card includes: model details, intended use, training data summary, performance metrics, ethical considerations, limitations
3. **Data Card** for `dynamic_pricing.xlsx` dataset: source, features, distributions, known biases
4. Cards stored as JSON in `backend/data/cards/`
5. Cards renderable as Markdown for documentation display
6. Cards include generation timestamps and model versions

#### Technical Notes

- **Format:** JSON primary, Markdown rendering on demand
- **Template:** Based on Google's Model Cards for ML Transparency
- **Generation:** Script `backend/scripts/generate_cards.py`

---

### Story 3.5: Explain Decision Endpoint

**As a** frontend developer,  
**I want** an API endpoint returning full explanation,  
**so that** UI can display "why" information alongside recommendations.

#### Acceptance Criteria

1. `POST /api/v1/explain_decision` endpoint accepts MarketContext + optional pricing result reference
2. Returns: `recommendation`, `feature_importance[]`, `decision_trace`, `natural_language_summary`, `model_agreement`
3. Natural language summary generated (e.g., "The recommended price of $42.50 is primarily driven by high demand in your urban segment during evening hours...")
4. Response time < 2 seconds
5. Documented in Swagger with comprehensive examples

#### Technical Notes

- **Narrative Generation:** Template-based with variable substitution, not LLM-generated
- **Integration:** Can be called standalone or combined with optimize_price response
- **Schema:** See `docs/architecture/api-specification.md`

---

### Story 3.6: Sensitivity Analysis Endpoint

**As a** frontend developer,  
**I want** an API endpoint for sensitivity analysis,  
**so that** UI can display robustness charts.

#### Acceptance Criteria

1. `POST /api/v1/sensitivity_analysis` endpoint accepts MarketContext
2. Returns: `elasticity_sensitivity[]`, `demand_sensitivity[]`, `cost_sensitivity[]`
3. Returns: `confidence_band` (min/max price range) and `robustness_score` (0-100)
4. Response time < 3 seconds (parallel scenario calculation)
5. Documented in Swagger with chart-ready response format

#### Technical Notes

- **Response Format:** Arrays suitable for Recharts line/area charts
- **Scenarios:** Pre-defined scenario levels, not user-configurable (for hackathon)
- **Refer to:** `docs/architecture/api-specification.md`

---

### Story 3.7: Evidence & Honeywell Mapping Endpoints

**As a** frontend developer,  
**I want** API endpoints for model/data cards and Honeywell mapping,  
**so that** the Evidence tab can display documentation.

#### Acceptance Criteria

1. `GET /api/v1/evidence` endpoint returns all model cards, data card, and methodology documentation
2. `GET /api/v1/honeywell_mapping` endpoint returns ride-sharing to Honeywell catalog mapping table and rationale
3. Both endpoints support response caching (long TTL - content is static)
4. Support both JSON and Markdown output formats (via Accept header or query param)
5. Documented in Swagger

#### Technical Notes

- **Honeywell Mapping:** Static content explaining how ride-sharing concepts map to enterprise pricing
- **Content Location:** `backend/data/evidence/` directory
- **Caching:** 24-hour cache, content changes only on deploy

---

## Epic Definition of Done

- [ ] All 7 stories completed with acceptance criteria met
- [ ] SHAP explanations working for all model types
- [ ] Decision trace captures full pipeline with timing
- [ ] Model cards generated for all 3 models
- [ ] All endpoints documented in Swagger
- [ ] Unit tests for explainability module (>80% coverage)
- [ ] Integration tests for explain and sensitivity endpoints
- [ ] Natural language summaries reviewed for clarity

## Technical References

| Document | Purpose |
|----------|---------|
| `docs/architecture/components.md` | Explainability component specs |
| `docs/architecture/api-specification.md` | API contracts |
| `docs/architecture/data-models.md` | PriceExplanation, FeatureContribution schemas |
| `docs/architecture/security-and-performance.md` | Response time targets |
| `docs/architecture/error-handling-strategy.md` | Graceful degradation |

