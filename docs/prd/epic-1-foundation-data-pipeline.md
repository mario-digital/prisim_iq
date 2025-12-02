# Epic 1: Foundation & Data Pipeline

## Epic Goal

Establish the complete project infrastructure including monorepo structure, development environment, and CI basics. Load and analyze the `dynamic_pricing.xlsx` dataset, implement K-Means clustering for market segmentation, and expose initial FastAPI endpoints for data exploration and health verification.

## Epic Context

**PRD Reference:** PrismIQ Dynamic Pricing Copilot  
**Priority:** P0 - Critical Foundation  
**Dependencies:** None (foundational epic)  
**Estimated Effort:** Sprint 1

---

## Stories

### Story 1.1: Project Setup & Monorepo Structure

**As a** developer,  
**I want** a properly structured monorepo with backend, frontend, data, and docs directories,  
**so that** all team members can contribute to a well-organized codebase from day one.

#### Acceptance Criteria

1. Monorepo created with `/backend`, `/frontend`, `/data`, `/docs` directories
2. Backend initialized with Python 3.12+ virtual environment and `pyproject.toml` + `requirements.lock`
3. Frontend initialized with Next.js 15+, TypeScript, Tailwind CSS 4, Recharts
4. Shared types package created at `/packages/shared/` with TypeScript configuration
5. `.gitignore` properly configured for Python, Node, and IDE files
6. Basic `README.md` with setup instructions for both frontend and backend
7. Backend runs with `uvicorn src.main:app --reload` returning health at `/health`
8. Frontend runs with `bun run dev` displaying placeholder page at localhost:3000

#### Technical Notes

- **Package Managers:** Bun for frontend (enforced via `.npmrc`), uv for backend
- **Python Version:** 3.12+ (specified in `.python-version`)
- **Node Version:** 22+ (for Bun compatibility)
- **Refer to:** `docs/architecture/unified-project-structure.md`, `docs/architecture/coding-standards.md`

---

### Story 1.2: Data Loading & Exploratory Data Analysis

**As a** data scientist,  
**I want** the `dynamic_pricing.xlsx` dataset loaded and analyzed,  
**so that** I understand the data distribution before building models.

#### Acceptance Criteria

1. Dataset placed in `/backend/data/dynamic_pricing.xlsx`
2. Data loading utility created in `backend/src/ml/preprocessor.py`
3. EDA documents generated: row count, column types, missing values, descriptive statistics
4. Feature distributions analyzed (histograms for numeric, value counts for categorical)
5. Supply/demand ratio calculated as derived feature: `drivers / riders`
6. EDA summary exportable as JSON via utility function
7. Data quality issues documented in code comments or separate markdown

#### Technical Notes

- **Data Schema:** See `docs/architecture/database-schema.md` Section 9.1
- **Libraries:** pandas 2.2, numpy
- **Output Format:** JSON-serializable dictionary for API consumption

---

### Story 1.3: K-Means Market Segmentation

**As a** pricing analyst,  
**I want** market contexts automatically segmented into distinct clusters,  
**so that** I can understand different pricing contexts.

#### Acceptance Criteria

1. K-Means clustering implemented in `backend/src/ml/segmenter.py` using scikit-learn
2. Optimal k determined using elbow method or silhouette score (document choice)
3. Features selected and scaled appropriately (StandardScaler)
4. Each cluster labeled with descriptive name (e.g., "Urban_Peak_Premium")
5. Cluster centroids stored for assignment of new contexts
6. Function `classify(context: MarketContext) -> SegmentResult` to assign new contexts
7. Segment distribution visualized and saved as reference data

#### Technical Notes

- **Model Persistence:** Save to `backend/data/models/segmenter.joblib`
- **Expected Segments:** ~6 segments based on Location × Vehicle Type combinations
- **Refer to:** `docs/architecture/components.md` Section 6.1 (ML Pipeline)

---

### Story 1.4: FastAPI Foundation & Initial Endpoints

**As a** frontend developer,  
**I want** REST API endpoints for health check and EDA summary,  
**so that** I can verify the backend is operational.

#### Acceptance Criteria

1. FastAPI app structured with routers in `backend/src/api/routers/`
2. `/health` GET endpoint returns `{ status: "healthy", version: "1.0.0", timestamp: "..." }`
3. `/api/v1/data/summary` GET endpoint returns dataset statistics (row count, segments, price range)
4. CORS configured for `http://localhost:3000` (frontend origin)
5. Request/response models defined with Pydantic in `backend/src/schemas/`
6. Basic error handling with appropriate HTTP status codes
7. Swagger documentation auto-generated at `/docs`

#### Technical Notes

- **API Specification:** See `docs/architecture/api-specification.md`
- **Dependency Injection:** Use `backend/src/api/dependencies.py` pattern
- **Middleware:** CORS, logging, timing (see `docs/architecture/backend-architecture.md`)

---

### Story 1.5: Segment Assignment Endpoint

**As a** pricing analyst,  
**I want** to submit a market context and receive its segment assignment,  
**so that** I can understand which pricing cluster applies.

#### Acceptance Criteria

1. `POST /api/v1/data/segment` endpoint accepts MarketContext in request body
2. Returns: segment name, cluster ID, segment characteristics, centroid distance (confidence)
3. Returns distance to centroid as confidence indicator (lower = more confident)
4. Validates input with Pydantic, returns 422 with field errors for invalid data
5. Includes human-readable segment description in response
6. Response time < 100ms for segment classification

#### Technical Notes

- **Request Schema:** `MarketContext` from `docs/architecture/data-models.md`
- **Response Schema:** `SegmentDetails` from `docs/architecture/api-specification.md`
- **Integration:** Uses `Segmenter` from Story 1.3

---

## Epic Definition of Done

- [ ] All 5 stories completed with acceptance criteria met
- [ ] Monorepo structure matches `docs/architecture/unified-project-structure.md`
- [ ] Backend and frontend run independently
- [ ] All endpoints documented in Swagger
- [ ] Unit tests for data loading and segmentation (>80% coverage for ML module)
- [ ] No linting errors (ruff for Python, ESLint for TypeScript)
- [ ] README updated with complete setup instructions

## Technical References

| Document | Purpose |
|----------|---------|
| `docs/architecture/unified-project-structure.md` | Directory structure |
| `docs/architecture/backend-architecture.md` | Backend patterns |
| `docs/architecture/api-specification.md` | API contracts |
| `docs/architecture/database-schema.md` | Data schemas |
| `docs/architecture/coding-standards.md` | Code style rules |
| `docs/architecture/tech-stack.md` | Technology choices |

