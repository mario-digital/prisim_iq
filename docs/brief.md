# Project Brief: PrismIQ

## Executive Summary

**PrismIQ** is an agentic, chat-driven dynamic pricing copilot designed for business analysts at enterprise organizations. The system combines behavioral economics simulation, machine learning models (clustering, regression, random forests), and an explainable AI interface to recommend profit-maximizing prices across different market contexts.

**Primary Problem:** Business analysts lack intuitive, explainable tools to optimize dynamic pricing decisions. Current approaches are either too simplistic (static markup) or too opaque (black-box ML), leaving analysts unable to justify recommendations to executives or respond to "what-if" scenarios confidently.

**Target Market:** Enterprise pricing teams, initially demonstrated via a ride-sharing use case with direct applicability to Honeywell's catalog pricing context (parts, services, product tiers).

**Key Value Proposition:** PrismIQ delivers profit-maximizing price recommendations through a conversational interface, with full transparency into the "why" behind every recommendation—bridging the gap between data science sophistication and business user accessibility.

---

## Problem Statement

### Current State & Pain Points

Enterprise pricing decisions today suffer from several critical challenges:

1. **Static Pricing Inertia:** Most organizations rely on cost-plus markup or historical pricing, leaving significant profit on the table in dynamic market conditions.

2. **Black-Box Distrust:** When ML-based pricing tools exist, analysts cannot explain recommendations to stakeholders, leading to low adoption and overrides.

3. **Context Blindness:** Existing tools fail to account for the interplay of supply/demand ratios, customer segments, time-of-day patterns, and loyalty tiers simultaneously.

4. **Scenario Paralysis:** Analysts cannot quickly explore "what-if" scenarios (e.g., "What if fuel costs rise 10%?" or "How sensitive is this recommendation to demand elasticity?").

### Impact of the Problem

- **Revenue Leakage:** Suboptimal pricing across thousands of SKUs/contexts compounds into millions in lost profit annually.
- **Analyst Frustration:** Skilled analysts spend time on manual calculations rather than strategic analysis.
- **Executive Skepticism:** Without explainability, pricing recommendations face resistance at approval stages.
- **Competitive Disadvantage:** Competitors with dynamic pricing capabilities capture margin that static-price organizations forfeit.

### Why Existing Solutions Fall Short

- **Spreadsheet Models:** Cannot handle the dimensionality of real pricing contexts or provide real-time recommendations.
- **Traditional BI Tools:** Descriptive, not prescriptive—show what happened, not what to do.
- **Pure ML Solutions:** Lack interpretability, business rule integration, and conversational interfaces.
- **Consulting Engagements:** Expensive, slow, and produce static deliverables rather than living systems.

### Urgency

The hackathon context demands a working prototype that demonstrates the full pipeline: data → simulation → ML → optimization → explainability → UI. This is a proof-of-concept that maps directly to Honeywell's real-world catalog pricing challenges.

---

## Proposed Solution

### Core Concept

PrismIQ is a **chat-driven pricing copilot** that:

1. **Ingests market context** (location, time, supply/demand, customer segment, vehicle/product type, cost structure)
2. **Segments the market** using K-Means clustering to identify distinct pricing contexts
3. **Simulates demand response** using a behavioral economics model grounded in the provided dataset
4. **Trains ML models** (Linear Regression, Decision Tree, Random Forest) on synthetic demand labels
5. **Optimizes price** by searching for the profit-maximizing point on the demand curve
6. **Applies business rules** (caps, hierarchies, fairness constraints) to ensure recommendations are policy-compliant
7. **Explains everything** through feature importance, decision traces, model cards, and natural language narratives
8. **Delivers via chat** using a LangChain-powered agent that orchestrates tools and renders results in a Next.js UI

### Key Differentiators

| Competitor Approach | PrismIQ Advantage |
|---------------------|-------------------|
| Black-box ML | Full explainability (feature importance, SHAP, decision traces) |
| Static dashboards | Conversational, exploratory interface |
| Single-model solutions | Ensemble approach with interpretable baselines |
| Generic pricing tools | Domain-specific (ride-sharing → Honeywell catalog mapping) |
| No business rules | Integrated constraint layer (caps, hierarchies, contracts) |

### Why This Will Succeed

- **Grounded in Real Data:** Uses the provided `dynamic_pricing.xlsx` as the state space, not synthetic toy data.
- **Economically Sound:** Behavioral simulator encodes price elasticity, reference pricing, and segment-specific sensitivity.
- **Technically Rigorous:** Multiple ML models with proper train/test splits, hyperparameter tuning, and evaluation.
- **Business-Ready:** Rules layer mirrors real-world constraints (Honeywell's catalog rules, FAR compliance, contract ceilings).
- **User-Centric:** Designed for analysts (detailed workspace) AND executives (summary view).

### High-Level Vision

PrismIQ becomes the "pricing analyst's copilot"—a trusted tool that augments human judgment with data-driven recommendations, scenario exploration, and audit-ready explanations.

---

## Target Users

### Primary User Segment: Business Analyst (BA)

**Profile:**
- Role: Pricing Analyst, Revenue Manager, Commercial Analyst
- Experience: 3-10 years in pricing, finance, or commercial operations
- Technical comfort: Proficient with Excel, BI tools; familiar with basic statistics; not necessarily a data scientist
- Organization: Enterprise (manufacturing, aerospace, logistics, ride-sharing)

**Current Behaviors & Workflows:**
- Spends hours in spreadsheets building pricing models
- Manually adjusts prices based on intuition and historical patterns
- Struggles to justify recommendations to leadership
- Relies on IT/data science teams for any ML-based analysis

**Specific Needs & Pain Points:**
- Needs to respond quickly to "what should we charge?" questions
- Wants to explore scenarios without rebuilding models
- Requires explainable outputs for stakeholder buy-in
- Must ensure recommendations comply with business policies

**Goals:**
- Increase profit contribution from pricing decisions
- Reduce time-to-recommendation from days to minutes
- Build confidence in pricing recommendations through transparency
- Demonstrate strategic value beyond "number crunching"

### Secondary User Segment: Executive (CEO/VP/CFO)

**Profile:**
- Role: C-suite, VP of Pricing, VP of Commercial Operations
- Interaction: Periodic (weekly/monthly reviews), not daily
- Technical comfort: Low tolerance for technical jargon; needs business narratives

**Current Behaviors:**
- Reviews pricing decisions at aggregate level
- Asks "how much profit did we gain/lose?" and "what are the risks?"
- Approves or challenges analyst recommendations

**Specific Needs:**
- High-level KPIs: profit uplift, demand impact, guardrail adherence
- Visual summaries, not detailed tables
- Confidence that recommendations are defensible

**Goals:**
- Ensure pricing strategy drives profitability
- Minimize risk of pricing controversies (gouging, compliance)
- Trust the system enough to delegate tactical decisions

---

## Goals & Success Metrics

### Business Objectives

- **Demonstrate profit uplift:** Show ≥10% profit improvement vs. baseline static pricing across test scenarios
- **Achieve explainability:** Every recommendation includes a decision trace and feature importance visualization
- **Enable scenario exploration:** Analysts can run ≥5 what-if scenarios in under 2 minutes each
- **Map to Honeywell context:** Provide explicit mapping from ride-sharing constructs to Honeywell catalog pricing

### User Success Metrics

- **Time-to-insight:** Analyst receives a price recommendation within 5 seconds of submitting context
- **Exploration depth:** Analyst can drill into feature importance, demand curves, and sensitivity analysis without leaving the UI
- **Confidence score:** Analyst can articulate "why this price" to a stakeholder using system-provided explanations
- **Executive clarity:** Executive Summary view conveys key metrics in ≤30 seconds of viewing

### Key Performance Indicators (KPIs)

| KPI | Definition | Target |
|-----|------------|--------|
| Profit Uplift % | (Optimized profit - Baseline profit) / Baseline profit | ≥10% |
| Recommendation Latency | Time from context submission to price recommendation | <5 seconds |
| Explainability Coverage | % of recommendations with full decision trace | 100% |
| Scenario Throughput | What-if scenarios explorable per session | ≥10 |
| Business Rule Compliance | % of recommendations passing all constraints | 100% |

---

## MVP Scope

### Core Features (Must Have)

- **Context Ingestion & Segmentation:** Accept market context inputs, assign to K-Means cluster/segment
- **Demand Simulation:** Behavioral simulator generating demand labels based on price sensitivity, reference pricing, and context features
- **ML Model Training:** Train Linear Regression, Decision Tree, and Random Forest on synthetic demand data
- **Price Optimization Loop:** Search for profit-maximizing price using trained demand model
- **Business Rules Layer:** Apply caps, hierarchies, and fairness constraints to model-optimal price
- **FastAPI Backend:** REST endpoints for `/optimize_price`, `/explain_decision`, `/sensitivity_analysis`, `/eda_summary`, `/evidence`, `/honeywell_mapping`
- **LangChain Agent:** Orchestrate tool calls and generate natural language responses
- **Next.js Frontend:** Three-tab UI (Analyst Workspace, Executive Summary, Evidence & Methods) with integrated chat
- **Explainability Outputs:** Feature importance charts, decision traces, model cards, data cards

### Out of Scope for MVP

- Real-time external data integration (weather, events, fuel indices)
- User authentication and multi-tenancy
- Model retraining pipeline (models are trained once for demo)
- Advanced ML models (XGBoost, neural networks)
- SHAP deep-dive (optional stretch goal)
- Mobile-responsive design
- Internationalization/localization
- Production deployment infrastructure (CI/CD, monitoring)

### MVP Success Criteria

The MVP is successful when:

1. A user can submit a market context via chat and receive a recommended price with explanation in <5 seconds
2. The Analyst Workspace displays price-profit curves, feature importance, and segment information
3. The Executive Summary shows profit uplift vs. baseline across segments
4. The Evidence & Methods view provides full decision trace and model/data cards
5. Sensitivity analysis demonstrates recommendation robustness across elasticity scenarios
6. Honeywell mapping is accessible and clearly explains the ride-sharing → catalog pricing translation

---

## Post-MVP Vision

### Phase 2 Features

- **Real External Data:** Integrate live fuel prices, weather APIs, event calendars
- **Model Retraining:** Automated pipeline to retrain models on new data
- **A/B Testing Framework:** Compare pricing strategies in controlled experiments
- **Advanced Explainability:** Full SHAP integration for local explanations
- **User Feedback Loop:** Analysts can flag recommendations, improving future models

### Long-term Vision (1-2 Years)

- **Production Deployment:** Enterprise-grade infrastructure with authentication, audit logging, and SLAs
- **Multi-Domain Support:** Extend beyond ride-sharing and Honeywell to other industries (retail, hospitality, SaaS)
- **Causal Inference:** Move from correlation-based ML to causal models for more robust recommendations
- **Autonomous Pricing:** Option for system to auto-execute approved recommendations within guardrails
- **Competitive Intelligence:** Integrate competitor pricing signals into optimization

### Expansion Opportunities

- **Honeywell Production Pilot:** Deploy PrismIQ for a subset of Honeywell's catalog pricing decisions
- **SaaS Product:** Package PrismIQ as a standalone pricing optimization platform
- **Consulting Accelerator:** Use PrismIQ as a tool for pricing consulting engagements
- **Academic Partnership:** Collaborate with universities on pricing research using the platform

---

## Technical Considerations

### Platform Requirements

- **Target Platforms:** Web application (desktop browsers)
- **Browser Support:** Chrome, Firefox, Safari, Edge (latest versions)
- **Performance Requirements:** Price recommendation <5 seconds; UI renders <2 seconds

### Technology Preferences

- **Frontend:** Next.js (React), TypeScript, Tailwind CSS, Recharts
- **Backend:** FastAPI (Python), Uvicorn
- **ML/Data:** pandas, NumPy, scikit-learn (K-Means, Linear Regression, Decision Tree, Random Forest, GridSearchCV)
- **Agentic Layer:** LangChain for tool orchestration and chat interaction
- **Optional:** SHAP for deep explainability

### Architecture Considerations

- **Repository Structure:** Monorepo with `/backend` (Python/FastAPI), `/frontend` (Next.js), `/data` (datasets, models), `/docs` (documentation)
- **Service Architecture:** Single backend service exposing REST APIs; frontend consumes APIs and renders UI
- **Integration Requirements:** LangChain agent calls FastAPI endpoints as tools; frontend calls agent endpoint for chat
- **Security/Compliance:** No PII in demo dataset; business rules encode compliance constraints (FAR, contract caps)

---

## Constraints & Assumptions

### Constraints

- **Budget:** Hackathon context—no budget for external services or infrastructure
- **Timeline:** Must be demo-ready within hackathon timeframe
- **Resources:** Small team; no dedicated DevOps or QA
- **Technical:** Must use provided `dynamic_pricing.xlsx` dataset; no access to real booking/price data

### Key Assumptions

- The provided dataset is representative of realistic market contexts
- Behavioral simulation parameters (elasticity, sensitivity) are reasonable approximations
- Analysts will interact primarily via chat, with dashboards as supporting views
- Executives will consume summary views, not detailed workspaces
- Honeywell mapping is conceptual—demonstrating transferability, not production integration

---

## Risks & Open Questions

### Key Risks

- **Simulation Validity:** Synthetic demand labels may not reflect real-world price-demand relationships. *Mitigation:* Sensitivity analysis across elasticity scenarios; clear documentation of assumptions.
- **Model Overfitting:** Random Forest may overfit to simulator patterns. *Mitigation:* Train/test split; compare against Linear Regression baseline.
- **UI Complexity:** Three-tab interface may overwhelm users. *Mitigation:* Prioritize Analyst Workspace; simplify Executive Summary.
- **Agent Reliability:** LangChain agent may produce inconsistent responses. *Mitigation:* Constrain tool outputs; test common query patterns.
- **Demo Stability:** Live demo may encounter edge cases. *Mitigation:* Pre-test with representative scenarios; have fallback static examples.

### Open Questions

- How should we handle contexts that fall outside the training data distribution?
- What is the optimal number of clusters (k) for segmentation?
- Should the chat interface support multi-turn conversations or single-turn Q&A?
- How detailed should the Honeywell mapping be for the hackathon presentation?

### Areas Needing Further Research

- Optimal hyperparameters for Random Forest on this specific dataset
- User testing of chat interaction patterns (what questions do analysts actually ask?)
- Executive Summary content—what KPIs matter most to leadership?
- SHAP integration feasibility within hackathon timeline

---

## Appendices

### A. Research Summary

**Dataset Analysis:**
- 1,000 rows × 10 columns representing market context snapshots
- Key features: riders, drivers, location, time, vehicle type, loyalty, cost, duration
- No historical prices or bookings—necessitating behavioral simulation

**Technical Feasibility:**
- scikit-learn provides all required ML algorithms
- FastAPI + LangChain integration is well-documented
- Next.js + Recharts can render required visualizations
- Timeline is aggressive but achievable with focused scope

### B. Stakeholder Input

- **Hackathon Sponsors (Honeywell):** Interested in catalog pricing applicability; want to see explicit mapping
- **Judges:** Will evaluate technical rigor, business impact, and presentation quality
- **Team:** Aligned on scope; Python/ML expertise available; frontend experience present

### C. References

- `dynamic_pricing.xlsx` — provided hackathon dataset
- `PrismIQ_README.md` — detailed technical specification (source for this brief)
- LangChain documentation — agent orchestration patterns
- scikit-learn documentation — ML model APIs
- FastAPI documentation — REST API development
- Next.js documentation — frontend framework

---

## Next Steps

### Immediate Actions

1. **Set up repository structure:** Create monorepo with `/backend`, `/frontend`, `/data`, `/docs` directories
2. **Implement data pipeline:** Load `dynamic_pricing.xlsx`, perform EDA, engineer features, run clustering
3. **Build behavioral simulator:** Implement demand function with configurable elasticity parameters
4. **Train ML models:** Generate synthetic training data, train Linear/Tree/RF models, evaluate
5. **Develop FastAPI endpoints:** Implement all six core endpoints
6. **Integrate LangChain agent:** Connect agent to tools, test query patterns
7. **Build Next.js UI:** Implement three-tab interface with chat integration
8. **Prepare demo scenarios:** Pre-test representative contexts for live demonstration

### PM Handoff

This Project Brief provides the full context for **PrismIQ**. Please start in 'PRD Generation Mode', review the brief thoroughly to work with the user to create the PRD section by section as the template indicates, asking for any necessary clarification or suggesting improvements.

