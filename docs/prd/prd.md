# PrismIQ Product Requirements Document (PRD)

## Goals and Background Context

### Goals

- **Deliver explainable, profit-maximizing price recommendations** through a conversational chat interface that bridges data science sophistication with business user accessibility
- **Enable rapid scenario exploration** allowing analysts to run ≥5 what-if scenarios in under 2 minutes each without rebuilding models
- **Achieve full transparency** with every recommendation including feature importance, decision traces, and natural language explanations analysts can articulate to stakeholders
- **Demonstrate ≥10% profit uplift** vs. baseline static pricing across test scenarios
- **Reduce time-to-recommendation from ~4 days to minutes** empowering analysts to respond immediately to pricing questions
- **Provide executive-ready insights** with a summary view consumable in ≤30 seconds conveying key metrics and profit impact
- **Map ride-sharing constructs to Honeywell catalog pricing context** proving transferability to enterprise parts/services/product tier pricing
- **Ensure 100% business rule compliance** with recommendations passing all constraints (caps, hierarchies, fairness, FAR compliance)

### Background Context

Enterprise pricing decisions today are hampered by a fundamental disconnect: static pricing leaves profit on the table, while sophisticated ML solutions are too opaque for business users to trust or explain. PrismIQ addresses this gap by combining behavioral economics simulation, ensemble ML models (Linear Regression, Decision Tree, Random Forest), and an explainable AI interface into a chat-driven copilot.

The hackathon context provides a ride-sharing use case via the `dynamic_pricing.xlsx` dataset, but the architecture maps directly to Honeywell's real-world catalog pricing challenges—parts, services, and product tier optimization. By grounding recommendations in interpretable models with full decision traces, PrismIQ enables analysts to justify every price point to executives while exploring scenarios in real-time.

### Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| Dec 2024 | 1.0 | Initial PRD from Project Brief | John (PM) |

---

## Requirements

### Functional Requirements

**FR1:** The system shall accept market context inputs (location, time, supply/demand ratio, customer segment, vehicle/product type, cost structure, duration) via a conversational chat interface.

**FR2:** The system shall segment market contexts using K-Means clustering to identify distinct pricing segments and display segment assignment to users.

**FR3:** The system shall simulate demand response using a behavioral economics model incorporating price elasticity, reference pricing, and segment-specific sensitivity parameters.

**FR4:** The system shall train and maintain three ML models (Linear Regression, Decision Tree, Random Forest) on synthetic demand data with proper train/test splits and hyperparameter tuning.

**FR5:** The system shall optimize price by searching for the profit-maximizing point on the demand curve using the trained demand model.

**FR6:** The system shall apply business rules layer to model-optimal prices including caps, hierarchies, fairness constraints, and FAR compliance requirements.

**FR7:** The system shall provide a `/optimize_price` endpoint returning recommended price with full context.

**FR8:** The system shall provide an `/explain_decision` endpoint returning feature importance, decision traces, and natural language explanation.

**FR9:** The system shall provide a `/sensitivity_analysis` endpoint demonstrating recommendation robustness across elasticity scenarios.

**FR10:** The system shall provide an `/eda_summary` endpoint returning exploratory data analysis of the dataset.

**FR11:** The system shall provide an `/evidence` endpoint returning model cards, data cards, and methodology documentation.

**FR12:** The system shall provide a `/honeywell_mapping` endpoint explaining the ride-sharing to catalog pricing translation.

**FR13:** The system shall integrate a LangChain-powered agent to orchestrate tool calls and generate natural language responses to user queries.

**FR14:** The system shall render an Analyst Workspace tab displaying price-profit curves, feature importance charts, segment information, and detailed recommendation context.

**FR15:** The system shall render an Executive Summary tab showing profit uplift vs. baseline across segments, high-level KPIs, and visual summaries consumable in ≤30 seconds.

**FR16:** The system shall render an Evidence & Methods tab providing full decision traces, model cards, data cards, and methodology documentation.

**FR17:** The system shall support what-if scenario exploration allowing analysts to modify context parameters and receive updated recommendations within 2 minutes per scenario.

**FR18:** The system shall display demand curves showing the price-demand relationship for the current context.

**FR19:** The system shall show feature importance visualizations explaining which factors most influence the recommended price.

**FR20:** The system shall provide confidence indicators for recommendations based on model agreement and data coverage.

### Non-Functional Requirements

**NFR1:** Price recommendations shall be returned within 5 seconds of context submission (recommendation latency).

**NFR2:** UI screens shall render within 2 seconds of navigation.

**NFR3:** The system shall support at least 10 concurrent analyst sessions without performance degradation.

**NFR4:** 100% of recommendations shall include a complete decision trace and explanation (explainability coverage).

**NFR5:** 100% of recommendations shall pass all configured business rule constraints (compliance rate).

**NFR6:** The chat interface shall handle common query patterns reliably with consistent response formatting.

**NFR7:** The system shall run entirely within hackathon constraints (no external paid services, no cloud infrastructure costs).

**NFR8:** The system shall use the provided `dynamic_pricing.xlsx` dataset without requiring external data sources.

**NFR9:** The codebase shall follow a monorepo structure with clear separation between `/backend`, `/frontend`, `/data`, and `/docs` directories.

**NFR10:** Backend shall be implemented in Python using FastAPI; frontend shall use Next.js with TypeScript and Tailwind CSS.

**NFR11:** ML models shall use scikit-learn implementations for consistency and interpretability.

**NFR12:** The system shall be demo-stable with pre-tested representative scenarios and fallback static examples.

---

## User Interface Design Goals

### Overall UX Vision

PrismIQ's interface embodies the "pricing analyst's copilot" metaphor—a trusted partner that augments human judgment rather than replacing it. The design prioritizes **transparency over abstraction**, showing analysts exactly how recommendations are derived while keeping executives focused on outcomes. The conversational chat serves as the primary interaction paradigm, with supporting visualizations that reveal depth on demand without overwhelming. Every screen answers the question: "Why should I trust this recommendation?"

### Key Interaction Paradigms

- **Chat-First Interaction:** Users submit market contexts and questions through natural language; the LangChain agent orchestrates responses and surfaces relevant visualizations automatically
- **Progressive Disclosure:** Summary insights are immediately visible; detailed breakdowns (feature importance, decision traces, demand curves) are one click away
- **Scenario Exploration Loop:** Modify context parameters → see updated recommendation → compare to baseline → iterate rapidly
- **Dual-Persona Design:** Analyst Workspace provides depth and detail; Executive Summary provides at-a-glance KPIs and narratives
- **Evidence-on-Demand:** Full methodology, model cards, and data cards are accessible but not in the critical path

### Master Layout Structure

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                  HEADER                                         │
│  🔷 PrismIQ                     ○────●────●────●                    [READY] 🟢  │
│     Dynamic Pricing Copilot     Context → ML → Optimize → Price                 │
│                                                                                  │
│  [Analyst Workspace]  [Executive Summary]  [Evidence & Methods]    💡 Honeywell │
├─────────────────┬───────────────────────────────┬───────────────────────────────┤
│                 │                               │                               │
│   LEFT PANEL    │        CENTER PANEL           │        RIGHT PANEL            │
│   (Collapsible) │    (Content varies by tab)    │        (Collapsible)          │
│                 │                               │                               │
│  Context &      │   ┌─────────────────────────┐ │   Explainability &            │
│  Inputs         │   │  Content Area           │ │   Analysis                    │
│                 │   │  (Chat or Dashboard)    │ │                               │
│                 │   │                         │ │                               │
│                 │   │                         │ │                               │
│                 │   ├─────────────────────────┤ │                               │
│                 │   │  Input (if applicable)  │ │                               │
│                 │   └─────────────────────────┘ │                               │
│    [◀ Collapse] │                               │               [Collapse ▶]    │
├─────────────────┴───────────────────────────────┴───────────────────────────────┤
│                                  FOOTER                                         │
│         Segment: Urban Peak  •  Models: 3/3 Ready  •  Last Response: 2.3s       │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Header Content

| Element | Description |
|---------|-------------|
| **Brand** | 🔷 PrismIQ + "Dynamic Pricing Copilot" tagline |
| **Pipeline Status** | Visual progress: Context → ML → Optimize → Price |
| **System Status** | [READY] 🟢 indicator |
| **Tab Navigation** | [Analyst Workspace] [Executive Summary] [Evidence & Methods] |
| **Honeywell Toggle** | 💡 Honeywell — quick access to mapping overlay |

### Footer Content

| Element | Description |
|---------|-------------|
| **Current Segment** | Name of assigned pricing segment |
| **Model Status** | 3/3 Ready (or individual model states) |
| **Response Time** | Last recommendation latency (e.g., "2.3s") |

### Tab Configurations

#### Tab 1: Analyst Workspace (Default)

| Panel | Content |
|-------|---------|
| **Left Panel** | Market Context, Supply/Demand, Customer Profile, Product/Service, Scenario Controls, Saved Scenarios |
| **Center Panel** | Interactive Chat with messages, recommendations, confidence indicators, and chat input |
| **Right Panel** | Recommendation card, Feature Importance chart, Decision Trace, Demand/Profit Curves, Sensitivity Analysis, Business Rules Applied |

#### Tab 2: Executive Summary

| Panel | Content |
|-------|---------|
| **Left Panel** | Collapsed by default (expandable) |
| **Center Panel** | Summary Dashboard: Profit Uplift headline, Key Insight narrative, Segment Performance chart, Share/Download buttons |
| **Right Panel** | KPI Cards (Profit Uplift, Recommendations count, Compliance rate), Risk Alerts |

#### Tab 3: Evidence & Methods

| Panel | Content |
|-------|---------|
| **Left Panel** | Documentation navigation (Model Cards, Data Card, Methodology, Audit Trail, Downloads) |
| **Center Panel** | Documentation Viewer rendering selected document, "Questions? Open Chat" button |
| **Right Panel** | Model cards summary, Data card summary, Quick Actions (Email to Execs, Download All) |

#### Honeywell Mapping Overlay

Modal overlay triggered by 💡 button showing ride-sharing to Honeywell catalog mapping table with download option.

### Accessibility

**WCAG AA** — Standard web accessibility compliance including keyboard navigation, color contrast, screen reader compatibility, and focus indicators.

### Target Platforms

**Web Responsive (Desktop-First)**
- Primary: Desktop browsers (Chrome, Firefox, Safari, Edge)
- Secondary: Tablet landscape mode
- Out of Scope: Mobile-responsive design

---

## Technical Assumptions

### Repository Structure: Monorepo

```
/prismiq
├── /backend      # Python/FastAPI
├── /frontend     # Next.js/TypeScript
├── /data         # Datasets, trained models
└── /docs         # Documentation
```

### Service Architecture: Single Backend Service

- **Architecture Type:** Monolith (single FastAPI service)
- **API Style:** REST endpoints consumed by frontend and LangChain agent
- **No microservices:** Complexity not justified for hackathon scope

### Testing Requirements: Unit + Integration

| Test Type | Scope | Tools |
|-----------|-------|-------|
| **Unit Tests** | ML model functions, business rules, utility functions | pytest |
| **Integration Tests** | API endpoint responses, LangChain tool orchestration | pytest + httpx |
| **Manual Testing** | UI flows, chat interactions, demo scenarios | Pre-scripted scenarios |

### Technology Stack

**Backend:**
- Language: Python 3.11+
- Framework: FastAPI with Uvicorn
- ML Libraries: pandas, NumPy, scikit-learn
- Agent Framework: LangChain
- Workflow Automation: n8n (for external data integration)

**Frontend:**
- Framework: Next.js 14+ (App Router)
- Language: TypeScript (strict mode)
- Styling: Tailwind CSS
- Charts: Recharts

**Data:**
- Source Dataset: `dynamic_pricing.xlsx`
- Model Storage: Pickle files in `/data/models/`
- No Database: In-memory data loading

**Deployment:**
- Local development only (hackathon)
- No CI/CD, no cloud infrastructure

---

## Epic List

| # | Epic Title | Goal Statement |
|---|------------|----------------|
| **1** | Foundation & Data Pipeline | Establish project infrastructure, load and analyze the dataset, implement K-Means segmentation, and expose initial API endpoints. |
| **2** | ML Models & Price Optimization | Build demand simulator, train ML models, implement optimization loop, apply business rules, integrate external data via n8n. |
| **3** | Explainability & Full API | Implement feature importance, decision traces, sensitivity analysis, model/data cards, and complete all API endpoints. |
| **4** | Frontend & Agent Integration | Build Next.js UI with all tabs, integrate LangChain agent, deliver complete interactive experience. |

---

## Epic 1: Foundation & Data Pipeline

### Epic Goal

Establish the complete project infrastructure including monorepo structure, development environment, and CI basics. Load and analyze the `dynamic_pricing.xlsx` dataset, implement K-Means clustering for market segmentation, and expose initial FastAPI endpoints for data exploration and health verification.

### Story 1.1: Project Setup & Monorepo Structure

**As a** developer,  
**I want** a properly structured monorepo with backend, frontend, data, and docs directories,  
**so that** all team members can contribute to a well-organized codebase from day one.

**Acceptance Criteria:**

1. Monorepo created with `/backend`, `/frontend`, `/data`, `/docs` directories
2. Backend initialized with Python 3.11+ virtual environment and `requirements.txt`
3. Frontend initialized with Next.js 14+, TypeScript, Tailwind CSS, Recharts
4. `.gitignore` properly configured
5. Basic `README.md` with setup instructions
6. Backend runs with `uvicorn main:app --reload` at `/health`
7. Frontend runs with `npm run dev` displaying placeholder page

### Story 1.2: Data Loading & Exploratory Data Analysis

**As a** data scientist,  
**I want** the `dynamic_pricing.xlsx` dataset loaded and analyzed,  
**so that** I understand the data distribution before building models.

**Acceptance Criteria:**

1. Dataset placed in `/data/raw/`
2. Data loading utility created
3. EDA documents: row count, column types, missing values, statistics
4. Feature distributions analyzed
5. Supply/demand ratio calculated as derived feature
6. EDA summary exportable as JSON
7. Data quality issues documented

### Story 1.3: K-Means Market Segmentation

**As a** pricing analyst,  
**I want** market contexts automatically segmented into distinct clusters,  
**so that** I can understand different pricing contexts.

**Acceptance Criteria:**

1. K-Means clustering implemented using scikit-learn
2. Optimal k determined using elbow method or silhouette score
3. Features selected and scaled appropriately
4. Each cluster labeled with descriptive name
5. Cluster centroids stored for assignment
6. Function to assign new contexts to clusters
7. Segment distribution visualized

### Story 1.4: FastAPI Foundation & Initial Endpoints

**As a** frontend developer,  
**I want** REST API endpoints for health check and EDA summary,  
**so that** I can verify the backend is operational.

**Acceptance Criteria:**

1. FastAPI app structured with routers
2. `/health` endpoint returns status
3. `/eda_summary` endpoint returns dataset statistics
4. CORS configured for localhost:3000
5. Request/response models with Pydantic
6. Basic error handling
7. Swagger documentation at `/docs`

### Story 1.5: Segment Assignment Endpoint

**As a** pricing analyst,  
**I want** to submit a market context and receive its segment assignment,  
**so that** I can understand which pricing cluster applies.

**Acceptance Criteria:**

1. `/segment` POST endpoint accepts market context
2. Returns segment name, cluster ID, characteristics
3. Returns distance to centroid as confidence
4. Validates input with error messages
5. Includes segment description
6. Response time < 100ms

---

## Epic 2: ML Models & Price Optimization

### Epic Goal

Build the behavioral demand simulator, train all three ML models on synthetic demand data, implement the price optimization loop, apply configurable business rules, and integrate external data via n8n workflows.

### Story 2.1: Behavioral Demand Simulator

**As a** data scientist,  
**I want** a demand simulator that models realistic price-demand relationships,  
**so that** I can generate training labels for ML models.

**Acceptance Criteria:**

1. Demand simulator implemented with configurable elasticity
2. Demand modulated by supply/demand ratio, time, segment, loyalty
3. Reference pricing effect included
4. Segment-specific sensitivity parameters
5. Function signature: `simulate_demand(context, price, elasticity_params, external_factors)`
6. Demand values bounded realistically
7. Unit tests validate demand decreases as price increases

### Story 2.2: Synthetic Training Data Generation

**As a** data scientist,  
**I want** synthetic demand labels generated for the entire dataset,  
**so that** I have labeled training data.

**Acceptance Criteria:**

1. For each row, generate demand at multiple price points
2. Price points span reasonable range
3. Training dataset includes context features, price, demand, profit
4. Profit calculated as `(price - cost) * demand`
5. Train/test split (80/20) with stratification
6. Data saved to `/data/processed/`
7. Generation reproducible with random seed

### Story 2.3: ML Model Training Pipeline

**As a** data scientist,  
**I want** three ML models trained to predict demand,  
**so that** I can compare performance and use the best predictor.

**Acceptance Criteria:**

1. Training pipeline in `/backend/src/ml/training.py`
2. Linear Regression trained as baseline
3. Decision Tree trained with max_depth tuning
4. Random Forest trained with GridSearchCV
5. All models predict demand given context + price
6. Models evaluated with R², MAE, RMSE
7. Comparison table generated
8. Models serialized to `/data/models/`

### Story 2.4: Price Optimization Loop

**As a** pricing analyst,  
**I want** the system to find the profit-maximizing price,  
**so that** I receive optimal recommendations.

**Acceptance Criteria:**

1. Optimization function searches price space
2. Maximizes: `(price - cost) * predicted_demand(price)`
3. Price bounds configurable
4. Returns optimal_price, expected_demand, expected_profit, profit_vs_baseline
5. Baseline comparison using static pricing
6. Completes in < 500ms per context
7. Unit tests verify optimizer finds known optimal

### Story 2.5: Business Rules Layer

**As a** compliance officer,  
**I want** business rules applied to model-optimal prices,  
**so that** recommendations comply with policy.

**Acceptance Criteria:**

1. Rules engine in `/backend/src/rules/engine.py`
2. Rules loaded from `/backend/config/business_rules.yaml`
3. Price Caps by segment/vehicle type
4. Price Floors ensuring margin
5. Fairness constraints (surge multiplier caps)
6. FAR compliance for government pricing
7. Loyalty tier discounts applied
8. Rules applied in priority order, logged
9. Final price returned with rules triggered

### Story 2.6: Optimize Price Endpoint

**As a** frontend developer,  
**I want** an API endpoint that returns optimized price recommendations,  
**so that** the chat can display pricing guidance.

**Acceptance Criteria:**

1. `/optimize_price` POST endpoint accepts market context
2. Returns recommended_price, confidence_score, expected_profit, profit_uplift_percent
3. Returns segment assignment and model used
4. Returns business rules applied
5. Response time < 3 seconds
6. Error handling for invalid contexts
7. Documented in Swagger

### Story 2.7: External Data Integration via n8n

**As a** pricing analyst,  
**I want** real-time external data factored into recommendations,  
**so that** pricing reflects current market conditions.

**Acceptance Criteria:**

1. n8n instance running with workflows at localhost:5678
2. Fuel Price Workflow fetches current fuel prices
3. Weather Workflow fetches weather conditions
4. Events Workflow fetches local events
5. Each workflow exposes webhook endpoint
6. External data cached with TTL
7. Demand simulator accepts external modifiers
8. `/external_context` endpoint returns current factors
9. Agent can articulate external factors in explanations

---

## Epic 3: Explainability & Full API

### Epic Goal

Implement comprehensive explainability outputs including feature importance, decision traces, sensitivity analysis, and model/data cards. Complete the full REST API surface.

### Story 3.1: Feature Importance Calculation

**As a** pricing analyst,  
**I want** to see which factors most influenced the recommendation,  
**so that** I can understand and explain decisions.

**Acceptance Criteria:**

1. Feature importance from Random Forest `feature_importances_`
2. Linear Regression coefficients normalized
3. Decision Tree importances extracted
4. Per-prediction importance (not just global)
5. Results as ranked list with percentages
6. Top 3 features with plain-English descriptions
7. Unit tests verify values sum to 1.0

### Story 3.2: Decision Trace Generation

**As a** pricing analyst,  
**I want** a step-by-step trace of how the system arrived at a price,  
**so that** I can audit decisions.

**Acceptance Criteria:**

1. Trace captures: Input → Segment → External Factors → Model Prediction → Optimization → Rules → Final
2. Each step includes timestamp and duration
3. Trace exportable as JSON and text
4. Model agreement indicator included
5. Trace stored for audit purposes

### Story 3.3: Sensitivity Analysis Engine

**As a** pricing analyst,  
**I want** to see how recommendations change under different assumptions,  
**so that** I can assess robustness.

**Acceptance Criteria:**

1. Elasticity sensitivity at ±10%, ±20%, ±30%
2. Demand sensitivity at ±10%, ±20%
3. Cost sensitivity at ±5%, ±10%
4. Results as visualization-ready arrays
5. Confidence band calculated
6. Worst-case and best-case highlighted

### Story 3.4: Model Cards & Data Cards

**As an** auditor,  
**I want** standardized documentation of models and data,  
**so that** I can assess reliability.

**Acceptance Criteria:**

1. Model Card per model (RF, DT, LR) following Google format
2. Each card includes: details, intended use, training data, metrics, ethical considerations
3. Data Card for `dynamic_pricing.xlsx`
4. Cards stored as JSON in `/data/cards/`
5. Cards rendered as Markdown
6. Cards include timestamps

### Story 3.5: Explain Decision Endpoint

**As a** frontend developer,  
**I want** an API endpoint returning full explanation,  
**so that** UI can display "why" information.

**Acceptance Criteria:**

1. `/explain_decision` POST endpoint
2. Returns: recommendation, feature_importance, decision_trace, natural_language_summary, model_agreement
3. Natural language summary generated
4. Response time < 2 seconds
5. Documented with examples

### Story 3.6: Sensitivity Analysis Endpoint

**As a** frontend developer,  
**I want** an API endpoint for sensitivity analysis,  
**so that** UI can display robustness charts.

**Acceptance Criteria:**

1. `/sensitivity_analysis` POST endpoint
2. Returns elasticity, demand, cost sensitivity arrays
3. Returns confidence_band and robustness_score
4. Response time < 3 seconds
5. Documented in Swagger

### Story 3.7: Evidence & Honeywell Mapping Endpoints

**As a** frontend developer,  
**I want** API endpoints for model/data cards and Honeywell mapping,  
**so that** Evidence tab can display documentation.

**Acceptance Criteria:**

1. `/evidence` GET endpoint returns all cards and methodology
2. `/honeywell_mapping` GET endpoint returns mapping table and rationale
3. Both endpoints cached
4. Support JSON and Markdown formats
5. Documented in Swagger

---

## Epic 4: Frontend & Agent Integration

### Epic Goal

Build the complete Next.js UI with all tabs and panels, integrate the LangChain agent for chat orchestration, and deliver the demo-ready MVP.

### Story 4.1: Next.js Project Setup & Layout Shell

**As a** frontend developer,  
**I want** the base application with master layout structure,  
**so that** all UI work builds on a consistent foundation.

**Acceptance Criteria:**

1. Next.js 14+ App Router with TypeScript
2. Tailwind CSS configured
3. Master layout with Header, 3 panels, Footer
4. Panel collapse/expand functionality
5. Tab navigation working
6. Loading and error states
7. Environment variables for API URL

### Story 4.2: Analyst Workspace - Left Panel

**As a** pricing analyst,  
**I want** to see and modify market context,  
**so that** I can explore scenarios.

**Acceptance Criteria:**

1. Left panel displays all context sections
2. Context values editable
3. "Apply Changes" button
4. Scenario Controls with sliders
5. Saved Scenarios list with save/load
6. Collapse functionality
7. State persisted in local storage

### Story 4.3: Analyst Workspace - Center Panel (Chat)

**As a** pricing analyst,  
**I want** a conversational chat interface,  
**so that** I can ask questions naturally.

**Acceptance Criteria:**

1. Chat message area with history
2. Messages styled for user vs AI
3. AI responses include Markdown, confidence, timestamp
4. Chat input with send button and Enter key
5. Loading state with typing indicator
6. Auto-scroll to latest message
7. Welcome message on load

### Story 4.4: Analyst Workspace - Right Panel

**As a** pricing analyst,  
**I want** explainability visualizations,  
**so that** I can understand recommendations.

**Acceptance Criteria:**

1. Recommendation summary card
2. Feature Importance bar chart
3. Decision Trace collapsible steps
4. Demand/Profit Curve charts
5. Sensitivity Analysis section
6. Business Rules Applied list
7. Collapse functionality

### Story 4.5: Executive Summary Tab

**As an** executive,  
**I want** a simplified dashboard view,  
**so that** I can understand metrics quickly.

**Acceptance Criteria:**

1. Left panel collapsed by default
2. Center panel: Summary Dashboard (not chat)
3. Right panel: KPI Cards
4. Share Report and Download PDF buttons
5. Data refreshes on tab switch
6. Clean aesthetic

### Story 4.6: Evidence & Methods Tab

**As an** auditor,  
**I want** access to methodology documentation,  
**so that** I can verify reliability.

**Acceptance Criteria:**

1. Left panel: documentation navigation
2. Center panel: Documentation Viewer
3. Right panel: quick reference and actions
4. "Questions? Open Chat" button
5. Email to Executives button
6. Download All button

### Story 4.7: Header & Footer Implementation

**As a** user,  
**I want** header and footer showing system status,  
**so that** I know the system is operational.

**Acceptance Criteria:**

1. Header: logo, pipeline status, system status, tabs, Honeywell toggle
2. Pipeline status updates during processing
3. Footer: segment, model status, response time
4. Footer updates after each recommendation
5. Graceful handling when API unavailable

### Story 4.8: Honeywell Mapping Overlay

**As a** hackathon judge,  
**I want** to see ride-sharing to Honeywell mapping,  
**so that** I understand business applicability.

**Acceptance Criteria:**

1. 💡 toggle opens modal overlay
2. Overlay displays mapping table with rationale
3. Close button and Escape key dismiss
4. Download PDF button
5. Overlay accessible from any tab

### Story 4.9: LangChain Agent Integration

**As a** pricing analyst,  
**I want** chat powered by an intelligent agent,  
**so that** questions are routed to the right tools.

**Acceptance Criteria:**

1. LangChain agent with access to all tools
2. Tools: optimize_price, explain_decision, sensitivity_analysis, get_segment, get_eda_summary, get_external_context, get_evidence, get_honeywell_mapping
3. Agent routes queries appropriately
4. Agent generates natural language responses
5. Agent maintains conversation context
6. `/chat` POST endpoint
7. Error handling for edge cases

### Story 4.10: Visualizations & Charts

**As a** pricing analyst,  
**I want** interactive, professional charts,  
**so that** I can visually understand pricing dynamics.

**Acceptance Criteria:**

1. Recharts integrated
2. Feature Importance horizontal bar chart
3. Demand Curve line chart with optimal point
4. Profit Curve line chart with area fill
5. Segment Performance bar chart
6. Sensitivity Band area chart
7. All charts responsive

### Story 4.11: Final Integration & Demo Polish

**As the** team,  
**I want** the complete system tested end-to-end,  
**so that** we deliver a polished presentation.

**Acceptance Criteria:**

1. End-to-end flow tested
2. All tabs and panels functional
3. Honeywell overlay working
4. Chat flows naturally for demo scenarios
5. Error states handled gracefully
6. Performance acceptable
7. Demo script prepared
8. Fallback examples available

---

## Checklist Results Report

### Executive Summary

| Metric | Assessment |
|--------|------------|
| **Overall PRD Completeness** | **94%** |
| **MVP Scope Appropriateness** | ✅ Just Right |
| **Readiness for Architecture Phase** | ✅ **Ready** |

### Category Statuses

| Category | Status | Critical Issues |
|----------|--------|-----------------|
| 1. Problem Definition & Context | ✅ PASS | None |
| 2. MVP Scope Definition | ✅ PASS | None |
| 3. User Experience Requirements | ✅ PASS | None |
| 4. Functional Requirements | ✅ PASS | None |
| 5. Non-Functional Requirements | ✅ PASS | None |
| 6. Epic & Story Structure | ✅ PASS | None |
| 7. Technical Guidance | ⚠️ PARTIAL | n8n workflow details need architect review |
| 8. Cross-Functional Requirements | ✅ PASS | None |
| 9. Clarity & Communication | ✅ PASS | None |

### Recommendations

1. Architect should validate external API availability for n8n workflows
2. Architect should define LangChain tool schemas
3. Consider fallback mock data for demo reliability

### Final Decision

**✅ READY FOR ARCHITECT**

---

## Next Steps

### UX Expert Prompt

> Sally, please review this PRD for PrismIQ, focusing on the User Interface Design Goals section. The UI follows a three-panel collapsible layout with header/footer. Please create the Front-End Specification document that details:
> 1. Component hierarchy and specifications
> 2. Interaction patterns and state management
> 3. Visual design tokens and styling guidelines
> 4. Responsive behavior and accessibility implementation
> 5. Chart/visualization specifications for Recharts
>
> The PRD is located at `docs/prd.md` and the project brief at `docs/brief.md`.

### Architect Prompt

> Winston, please review this PRD for PrismIQ and create the Architecture Document. Key areas requiring your attention:
> 1. FastAPI backend structure with all endpoints
> 2. LangChain agent tool schemas and orchestration patterns
> 3. n8n workflow integration architecture
> 4. ML pipeline design (simulator, training, optimization)
> 5. Data flow from context input through recommendation output
> 6. Business rules engine configuration
> 7. Frontend-backend API contract specifications
>
> The PRD is located at `docs/prd.md` and includes 4 epics with 30 stories. Pay special attention to Story 2.7 (n8n integration) which addresses the hackathon requirement for workflow automation.



