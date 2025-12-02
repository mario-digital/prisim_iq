# Epic 4: Frontend & Agent Integration

## Epic Goal

Build the complete Next.js UI with all tabs and panels, integrate the LangChain agent for chat orchestration, and deliver the demo-ready MVP with polished interactions and visualizations.

## Epic Context

**PRD Reference:** PrismIQ Dynamic Pricing Copilot  
**Priority:** P0 - User-Facing Delivery  
**Dependencies:** Epic 1, Epic 2, Epic 3 (all backend APIs)  
**Estimated Effort:** Sprint 4

---

## Stories

### Story 4.1: Next.js Project Setup & Layout Shell

**As a** frontend developer,  
**I want** the base application with master layout structure,  
**so that** all UI work builds on a consistent foundation.

#### Acceptance Criteria

1. Next.js 15+ App Router with TypeScript strict mode configured
2. Tailwind CSS 4.0 configured with custom design tokens
3. Master layout implemented with: Header, 3-panel body (left/center/right), Footer
4. Panel collapse/expand functionality working with smooth animations
5. Tab navigation working: Analyst Workspace, Executive Summary, Evidence & Methods
6. Loading states (skeleton loaders) and error boundaries implemented
7. Environment variables configured for `NEXT_PUBLIC_API_URL`

#### Technical Notes

- **Component Library:** shadcn/ui components installed and configured
- **State:** Zustand stores initialized per `docs/architecture/frontend-architecture.md`
- **Routing:** App Router structure per Section 10.3

---

### Story 4.2: Analyst Workspace - Left Panel (Context)

**As a** pricing analyst,  
**I want** to see and modify market context,  
**so that** I can explore different pricing scenarios.

#### Acceptance Criteria

1. Left panel displays all context sections: Location, Time, Supply/Demand, Customer, Vehicle
2. All context values editable via appropriate inputs (dropdowns, sliders, number inputs)
3. "Apply Changes" button triggers price recalculation
4. Scenario Controls section with quick-adjust sliders
5. Saved Scenarios list with save/load/delete functionality
6. Panel collapse functionality (chevron toggle)
7. State persisted in localStorage across sessions

#### Technical Notes

- **Components:** `frontend/src/components/context/` directory
- **Store:** `contextStore.ts` manages market context state
- **Validation:** Client-side validation matching backend Pydantic schemas

---

### Story 4.3: Analyst Workspace - Center Panel (Chat)

**As a** pricing analyst,  
**I want** a conversational chat interface,  
**so that** I can ask questions in natural language.

#### Acceptance Criteria

1. Chat message area displays conversation history with scroll
2. Messages styled distinctly for user (right-aligned) vs AI (left-aligned)
3. AI responses render Markdown, include confidence badges, show timestamps
4. Chat input with send button and Enter key support
5. Loading state with animated typing indicator during API call
6. Auto-scroll to latest message on new response
7. Welcome message displayed on initial load

#### Technical Notes

- **Components:** `frontend/src/components/chat/` directory
- **Store:** `chatStore.ts` with message persistence
- **API:** POST to `/api/v1/chat` with message and context
- **Streaming:** Support SSE streaming for long responses (optional enhancement)

---

### Story 4.4: Analyst Workspace - Right Panel (Explainability)

**As a** pricing analyst,  
**I want** explainability visualizations alongside chat,  
**so that** I can understand recommendations in depth.

#### Acceptance Criteria

1. **Recommendation Card:** Shows recommended price, confidence, profit uplift prominently
2. **Feature Importance:** Horizontal bar chart showing top factors (Recharts)
3. **Decision Trace:** Collapsible accordion showing pipeline steps
4. **Demand Curve:** Line chart showing price vs. demand relationship
5. **Profit Curve:** Line chart with area fill showing price vs. profit
6. **Sensitivity Analysis:** Expandable section with confidence bands
7. **Business Rules:** List of rules applied with impact indicators
8. Panel collapse functionality

#### Technical Notes

- **Components:** `frontend/src/components/visualizations/` directory
- **Charts:** Recharts 2.14 with responsive containers
- **Data:** Populated from `PricingResult.explanation` API response

---

### Story 4.5: Executive Summary Tab

**As an** executive,  
**I want** a simplified dashboard view,  
**so that** I can understand key metrics in under 30 seconds.

#### Acceptance Criteria

1. Left panel collapsed by default (can expand if needed)
2. Center panel: Summary Dashboard (NOT chat interface)
   - Profit Uplift headline metric (large, prominent)
   - Key Insight narrative paragraph
   - Segment Performance comparison chart
3. Right panel: KPI Cards
   - Total Profit Uplift percentage
   - Recommendations analyzed count
   - Compliance rate (100%)
   - Risk Alerts (if any)
4. Share Report and Download PDF buttons (can be mock for hackathon)
5. Data refreshes automatically on tab switch

#### Technical Notes

- **Layout:** Single-panel focus with collapsed sidebars
- **Data Source:** Aggregate from recent pricing requests or demo data
- **Styling:** Clean, executive-friendly aesthetic

---

### Story 4.6: Evidence & Methods Tab

**As an** auditor,  
**I want** access to methodology documentation,  
**so that** I can verify the system's reliability.

#### Acceptance Criteria

1. Left panel: Documentation navigation tree (Model Cards, Data Card, Methodology, Audit Trail, Downloads)
2. Center panel: Documentation Viewer rendering selected document (Markdown → HTML)
3. Right panel: Quick reference cards for models and data, Quick Actions
4. "Questions? Open Chat" button navigates to Analyst Workspace with context
5. "Email to Executives" button (mock or mailto link)
6. "Download All" button exports documentation as ZIP

#### Technical Notes

- **Content:** Fetched from `/api/v1/evidence` endpoint
- **Rendering:** Use react-markdown for Markdown display
- **Navigation:** Tree structure or tab-based sub-navigation

---

### Story 4.7: Header & Footer Implementation

**As a** user,  
**I want** header and footer showing system status,  
**so that** I know the system is operational and responsive.

#### Acceptance Criteria

1. **Header contains:**
   - Brand: 🔷 PrismIQ logo + "Dynamic Pricing Copilot" tagline
   - Pipeline Status: Visual progress indicator (Context → ML → Optimize → Price)
   - System Status: [READY] 🟢 indicator (or degraded/error states)
   - Tab Navigation: Three main tabs
   - Honeywell Toggle: 💡 button for mapping overlay
2. Pipeline status animates during processing
3. **Footer contains:**
   - Current Segment name
   - Model Status: "3/3 Ready"
   - Last Response Time: "2.3s"
4. Footer updates after each recommendation
5. Graceful handling when backend API unavailable

#### Technical Notes

- **Components:** `frontend/src/components/layout/Header.tsx`, `Footer.tsx`
- **Status Polling:** Health check on mount, update on errors

---

### Story 4.8: Honeywell Mapping Overlay

**As a** hackathon judge,  
**I want** to see the ride-sharing to Honeywell mapping,  
**so that** I understand the business applicability.

#### Acceptance Criteria

1. 💡 toggle button in header opens modal overlay
2. Overlay displays mapping table: Ride-Sharing Concept → Honeywell Equivalent → Rationale
3. Close button (X) and Escape key dismiss the overlay
4. "Download PDF" button exports mapping document
5. Overlay accessible from any tab (persists across navigation)
6. Modal has proper accessibility (focus trap, aria labels)

#### Technical Notes

- **Content:** Static or from `/api/v1/honeywell_mapping` endpoint
- **Component:** Generic Modal component from shadcn/ui
- **Trigger:** Global state or context for overlay visibility

---

### Story 4.9: LangChain Agent Integration

**As a** pricing analyst,  
**I want** chat powered by an intelligent agent,  
**so that** my questions are routed to the right backend tools.

#### Acceptance Criteria

1. LangChain agent implemented in `backend/src/agent/agent.py`
2. **Tools registered:**
   - `optimize_price`: Get optimal price for context
   - `explain_decision`: Get full explanation
   - `sensitivity_analysis`: Get sensitivity data
   - `get_segment`: Get segment classification
   - `get_eda_summary`: Get dataset statistics
   - `get_external_context`: Get current external factors
   - `get_evidence`: Get documentation
   - `get_honeywell_mapping`: Get mapping documentation
3. Agent correctly routes natural language queries to appropriate tools
4. Agent generates natural language responses incorporating tool results
5. Agent maintains conversation context (memory) within session
6. `POST /api/v1/chat` endpoint invokes agent and returns structured response
7. Error handling for edge cases (ambiguous queries, tool failures)

#### Technical Notes

- **Framework:** LangChain 0.3 with OpenAI GPT-4o
- **Prompts:** System prompt in `backend/src/agent/prompts/system.py`
- **Memory:** ConversationBufferMemory or similar
- **Refer to:** `docs/architecture/components.md` Section 6.1 (LangChain Agent)

---

### Story 4.10: Visualizations & Charts

**As a** pricing analyst,  
**I want** interactive, professional charts,  
**so that** I can visually understand pricing dynamics.

#### Acceptance Criteria

1. Recharts library integrated and configured with custom theme
2. **Feature Importance:** Horizontal bar chart with sorted bars, value labels
3. **Demand Curve:** Line chart with optimal price point marker
4. **Profit Curve:** Line chart with area fill under curve, max profit marker
5. **Segment Performance:** Grouped bar chart comparing segments
6. **Sensitivity Band:** Area chart showing confidence intervals
7. All charts responsive (resize with container)
8. Consistent color palette across all visualizations

#### Technical Notes

- **Components:** `frontend/src/components/visualizations/`
- **Theming:** Match Tailwind design tokens
- **Tooltips:** Custom tooltips with detailed information
- **Animations:** Subtle entry animations for polish

---

### Story 4.11: Final Integration & Demo Polish

**As the** team,  
**I want** the complete system tested end-to-end with demo scenarios,  
**so that** we deliver a polished hackathon presentation.

#### Acceptance Criteria

1. End-to-end flow tested: Context input → Chat query → Price recommendation → Visualizations
2. All three tabs functional and navigable
3. Honeywell overlay working from all tabs
4. Chat flows naturally for pre-defined demo scenarios:
   - "What's the optimal price for downtown rush hour?"
   - "Why is surge pricing recommended?"
   - "How sensitive is this to demand changes?"
   - "Compare urban vs suburban pricing"
5. Error states handled gracefully with user-friendly messages
6. Performance acceptable (< 5s for recommendations, < 2s for navigation)
7. Demo script prepared with talking points for each feature
8. Fallback examples available if live demo fails

#### Technical Notes

- **Demo Scenarios:** Pre-tested contexts saved in localStorage
- **Fallback:** Static JSON responses if backend unavailable
- **Polish:** Focus on the "happy path" for demo reliability

---

## Epic Definition of Done

- [ ] All 11 stories completed with acceptance criteria met
- [ ] Three-panel layout responsive and functional
- [ ] Chat interface connected to LangChain agent
- [ ] All visualizations rendering with real data
- [ ] Tab navigation smooth and state-preserving
- [ ] Honeywell overlay accessible and informative
- [ ] End-to-end demo flow tested and reliable
- [ ] Performance targets met (see `docs/architecture/security-and-performance.md`)
- [ ] Accessibility: Keyboard navigation, focus management
- [ ] No console errors in production build

## Technical References

| Document | Purpose |
|----------|---------|
| `docs/architecture/frontend-architecture.md` | Component organization, state management |
| `docs/architecture/components.md` | Frontend component specs |
| `docs/architecture/api-specification.md` | API contracts for frontend integration |
| `docs/architecture/core-workflows.md` | Chat and pricing workflows |
| `docs/architecture/coding-standards.md` | Frontend coding standards |
| `docs/architecture/security-and-performance.md` | Performance targets |
| `docs/prd.md` | UI Design Goals section |

