# Frontend Zod Schema Validation Plan

> **Document Purpose**: Technical specification for adding runtime validation with Zod to the PrismIQ frontend, ensuring type-safe alignment between backend Pydantic schemas and frontend TypeScript.

---

## Executive Summary

The PrismIQ backend uses **Pydantic v2** for request/response validation across 12 schema files containing 30+ models. The frontend currently has **no runtime validation** of API responses—only static TypeScript types that are duplicated across multiple locations and in some cases **don't match** the actual backend schemas.

This plan outlines the implementation of **Zod schemas** on the frontend that mirror backend Pydantic models, providing:
- Runtime validation of all API responses
- Type inference from schemas (single source of truth)
- Early detection of API contract drift
- Improved developer experience with autocomplete and error messages

---

## Current State Analysis

### Backend Schema Inventory (Pydantic)

| File | Schemas | Used By API Endpoint |
|------|---------|---------------------|
| `market.py` | `MarketContext` | All endpoints (input) |
| `chat.py` | `ChatRequest`, `ChatResponse`, `ChatStreamEvent` | `/api/v1/chat`, `/api/v1/chat/stream` |
| `data.py` | `PriceRange`, `DataSummaryResponse`, `ErrorResponse` | `/api/v1/data/summary` |
| `evidence.py` | `ModelCard`, `DataCard`, `MethodologyDoc`, `EvidenceResponse`, `HoneywellMapping`, `HoneywellMappingResponse` | `/api/v1/evidence`, `/api/v1/honeywell_mapping` |
| `explainability.py` | `FeatureContribution`, `FeatureImportanceResult` | `/api/v1/explain-decision` |
| `explanation.py` | `ExplainRequest`, `PriceExplanation` | `/api/v1/explain-decision` |
| `health.py` | `HealthResponse` | `/api/v1/health` |
| `optimization.py` | `PriceDemandPoint`, `OptimizationResult` | `/api/v1/optimize-price` |
| `pricing.py` | `PricingResult` | `/api/v1/optimize-price` |
| `segment.py` | `SegmentResult`, `SegmentDetails` | `/api/v1/segment` |
| `sensitivity.py` | `ScenarioResult`, `ConfidenceBand`, `SensitivityResult`, `SensitivityPoint`, `SensitivityResponse` | `/api/v1/sensitivity` |
| `rules/engine.py` | `AppliedRule`, `RulesResult` | (embedded in PricingResult) |

**Total: ~35 Pydantic models to convert**

### Frontend Current State

| Location | Types Defined | Issue |
|----------|---------------|-------|
| `packages/shared/src/types/market.ts` | `MarketContext` | ❌ **COMPLETELY DIFFERENT** from backend - wrong field names |
| `packages/shared/src/types/pricing.ts` | `PricingResult`, `PricingFactor` | ❌ **Doesn't match** backend PricingResult |
| `packages/shared/src/types/chat.ts` | `ChatMessage`, `ChatRequest` | ⚠️ Partial match, missing streaming types |
| `frontend/src/stores/contextStore.ts` | `MarketContext` | ✅ **Correct** - matches backend |
| `frontend/src/components/evidence/types.ts` | `ModelCard`, `DataCard`, `EvidenceResponse` | ⚠️ Partial match, some fields differ |
| `frontend/src/components/visualizations/types.ts` | `PriceExplanation`, `FeatureContribution`, etc. | ⚠️ Partial match, structure differs |
| `frontend/src/services/chatService.ts` | `ChatRequest`, `ChatResponse` | ❌ Inline types, doesn't match backend |

### Critical Issues

1. **No Runtime Validation**: API responses cast with `as Type` without validation
2. **Type Duplication**: Same types defined in 3-4 places
3. **Schema Mismatch**: `@prismiq/shared` has incorrect types that don't match backend
4. **No Type Sync**: Backend schema changes won't be detected until runtime failures

---

## Proposed Solution

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Backend (Python)                         │
│   Pydantic Models: backend/src/schemas/*.py                      │
│   - Source of truth for API contracts                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ HTTP JSON
┌─────────────────────────────────────────────────────────────────┐
│                   Frontend (TypeScript)                          │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │           packages/shared/src/schemas/                   │   │
│  │                                                          │   │
│  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │   │
│  │   │ market.ts   │  │ pricing.ts  │  │  chat.ts    │     │   │
│  │   │ (Zod)       │  │ (Zod)       │  │  (Zod)      │     │   │
│  │   └─────────────┘  └─────────────┘  └─────────────┘     │   │
│  │                                                          │   │
│  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │   │
│  │   │ evidence.ts │  │sensitivity.ts│ │explainability│    │   │
│  │   │ (Zod)       │  │ (Zod)       │  │   (Zod)     │     │   │
│  │   └─────────────┘  └─────────────┘  └─────────────┘     │   │
│  │                                                          │   │
│  │   export inferred types: type X = z.infer<typeof XSchema>│   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              frontend/src/services/api.ts                │   │
│  │   - Uses Zod schemas for response validation             │   │
│  │   - Throws typed errors on validation failure            │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Components & Stores                    │   │
│  │   - Import types from @prismiq/shared                    │   │
│  │   - Full type safety with validated data                 │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### File Structure

```
packages/shared/src/
├── schemas/                          # NEW: Zod schemas directory
│   ├── index.ts                      # Re-exports all schemas and types
│   ├── common.ts                     # ErrorResponse, shared primitives
│   ├── market.ts                     # MarketContext schema
│   ├── segment.ts                    # SegmentResult, SegmentDetails
│   ├── pricing.ts                    # PricingResult, PriceDemandPoint, AppliedRule
│   ├── optimization.ts               # OptimizationResult
│   ├── chat.ts                       # ChatRequest, ChatResponse, ChatStreamEvent
│   ├── evidence.ts                   # ModelCard, DataCard, EvidenceResponse, HoneywellMapping
│   ├── explainability.ts             # FeatureContribution, FeatureImportanceResult
│   ├── explanation.ts                # ExplainRequest, PriceExplanation, DecisionTrace
│   ├── sensitivity.ts                # SensitivityResult, SensitivityResponse
│   └── health.ts                     # HealthResponse
├── types/                            # DEPRECATED: Will re-export from schemas
│   └── index.ts                      # Re-exports types for backwards compat
├── constants/
│   └── index.ts
└── index.ts
```

---

## Schema Mapping Specification

### Mapping Rules: Pydantic → Zod

| Pydantic | Zod Equivalent |
|----------|----------------|
| `str` | `z.string()` |
| `int` | `z.number().int()` |
| `float` | `z.number()` |
| `bool` | `z.boolean()` |
| `datetime` | `z.string().datetime()` or `z.coerce.date()` |
| `list[T]` | `z.array(TSchema)` |
| `dict[str, T]` | `z.record(z.string(), TSchema)` |
| `T \| None` | `TSchema.nullable()` |
| `Field(default=X)` | `.default(X)` |
| `Field(ge=X, le=Y)` | `.min(X).max(Y)` |
| `Field(min_length=X)` | `.min(X)` |
| `Literal["a", "b"]` | `z.enum(["a", "b"])` |
| `BaseModel` (nested) | Compose schemas |

### Example Conversion

**Backend Pydantic (market.py):**
```python
class MarketContext(BaseModel):
    number_of_riders: int = Field(..., ge=1, le=100)
    number_of_drivers: int = Field(..., ge=1, le=100)
    location_category: Literal["Urban", "Suburban", "Rural"]
    customer_loyalty_status: Literal["Bronze", "Silver", "Gold", "Platinum"]
    number_of_past_rides: int = Field(..., ge=0)
    average_ratings: float = Field(..., ge=1.0, le=5.0)
    time_of_booking: Literal["Morning", "Afternoon", "Evening", "Night"]
    vehicle_type: Literal["Economy", "Premium"]
    expected_ride_duration: int = Field(..., ge=1)
    historical_cost_of_ride: float = Field(..., ge=0)
    tier_prices: dict[str, float] | None = Field(default=None)
```

**Frontend Zod (schemas/market.ts):**
```typescript
import { z } from 'zod';

export const LocationCategory = z.enum(['Urban', 'Suburban', 'Rural']);
export const CustomerLoyaltyStatus = z.enum(['Bronze', 'Silver', 'Gold', 'Platinum']);
export const TimeOfBooking = z.enum(['Morning', 'Afternoon', 'Evening', 'Night']);
export const VehicleType = z.enum(['Economy', 'Premium']);

export const MarketContextSchema = z.object({
  number_of_riders: z.number().int().min(1).max(100),
  number_of_drivers: z.number().int().min(1).max(100),
  location_category: LocationCategory,
  customer_loyalty_status: CustomerLoyaltyStatus,
  number_of_past_rides: z.number().int().min(0),
  average_ratings: z.number().min(1.0).max(5.0),
  time_of_booking: TimeOfBooking,
  vehicle_type: VehicleType,
  expected_ride_duration: z.number().int().min(1),
  historical_cost_of_ride: z.number().min(0),
  tier_prices: z.record(z.string(), z.number()).nullable().optional(),
});

// Infer TypeScript type from schema
export type MarketContext = z.infer<typeof MarketContextSchema>;

// Computed field (client-side only, matches backend @computed_field)
export function getSupplyDemandRatio(context: MarketContext): number {
  return context.number_of_drivers / context.number_of_riders;
}
```

---

## Complete Schema List with Priority

### Priority 1: Core Schemas (Required for basic functionality)

| Schema | Backend Location | Dependencies |
|--------|-----------------|--------------|
| `MarketContext` | `schemas/market.py` | None |
| `ErrorResponse` | `schemas/data.py` | None |
| `SegmentDetails` | `schemas/segment.py` | None |
| `AppliedRule` | `rules/engine.py` | None |
| `PriceDemandPoint` | `schemas/optimization.py` | None |
| `PricingResult` | `schemas/pricing.py` | SegmentDetails, AppliedRule, PriceDemandPoint |
| `ChatRequest` | `schemas/chat.py` | MarketContext |
| `ChatResponse` | `schemas/chat.py` | None |
| `ChatStreamEvent` | `schemas/chat.py` | None |

### Priority 2: Explainability Schemas

| Schema | Backend Location | Dependencies |
|--------|-----------------|--------------|
| `FeatureContribution` | `schemas/explainability.py` | None |
| `FeatureImportanceResult` | `schemas/explainability.py` | FeatureContribution |
| `TraceStep` | `explainability/decision_trace.py` | None |
| `ModelAgreement` | `explainability/decision_trace.py` | None |
| `DecisionTrace` | `explainability/decision_trace.py` | TraceStep, ModelAgreement |
| `PriceExplanation` | `schemas/explanation.py` | PricingResult, FeatureContribution, DecisionTrace, ModelAgreement |

### Priority 3: Evidence Schemas

| Schema | Backend Location | Dependencies |
|--------|-----------------|--------------|
| `ModelHyperparameters` | `schemas/evidence.py` | None |
| `ModelDetails` | `schemas/evidence.py` | ModelHyperparameters |
| `IntendedUse` | `schemas/evidence.py` | None |
| `TrainingData` | `schemas/evidence.py` | None |
| `ModelMetrics` | `schemas/evidence.py` | None |
| `EthicalConsiderations` | `schemas/evidence.py` | None |
| `ModelCard` | `schemas/evidence.py` | ModelDetails, IntendedUse, TrainingData, ModelMetrics, EthicalConsiderations |
| `DataFeature` | `schemas/evidence.py` | None |
| `DataSource` | `schemas/evidence.py` | None |
| `DataStatistics` | `schemas/evidence.py` | None |
| `DataCard` | `schemas/evidence.py` | DataFeature, DataSource, DataStatistics |
| `DocSection` | `schemas/evidence.py` | None (recursive) |
| `MethodologyDoc` | `schemas/evidence.py` | DocSection |
| `EvidenceResponse` | `schemas/evidence.py` | ModelCard, DataCard, MethodologyDoc |
| `HoneywellMapping` | `schemas/evidence.py` | None |
| `HoneywellMappingResponse` | `schemas/evidence.py` | HoneywellMapping |

### Priority 4: Sensitivity Schemas

| Schema | Backend Location | Dependencies |
|--------|-----------------|--------------|
| `ScenarioResult` | `schemas/sensitivity.py` | None |
| `ConfidenceBand` | `schemas/sensitivity.py` | None |
| `SensitivityPoint` | `schemas/sensitivity.py` | None |
| `MarketContextSummary` | `schemas/sensitivity.py` | None |
| `ScenarioSummary` | `schemas/sensitivity.py` | None |
| `SensitivityResult` | `schemas/sensitivity.py` | ScenarioResult, ConfidenceBand |
| `SensitivityResponse` | `schemas/sensitivity.py` | SensitivityPoint, ConfidenceBand, ScenarioSummary, MarketContextSummary |

### Priority 5: Utility Schemas

| Schema | Backend Location | Dependencies |
|--------|-----------------|--------------|
| `HealthResponse` | `schemas/health.py` | None |
| `DataSummaryResponse` | `schemas/data.py` | PriceRange |
| `PriceRange` | `schemas/data.py` | None |

---

## Implementation Tasks

### Task 1: Install Zod and Setup

**File: `packages/shared/package.json`**
```json
{
  "dependencies": {
    "zod": "^3.23.0"
  }
}
```

**Create: `packages/shared/src/schemas/index.ts`**
- Central export file for all schemas and types

### Task 2: Create Core Schemas (Priority 1)

Create the following files with Zod schemas:

1. `packages/shared/src/schemas/common.ts`
   - `ErrorResponseSchema`

2. `packages/shared/src/schemas/market.ts`
   - `MarketContextSchema`
   - Enum schemas for literals

3. `packages/shared/src/schemas/segment.ts`
   - `SegmentResultSchema`
   - `SegmentDetailsSchema`

4. `packages/shared/src/schemas/rules.ts`
   - `AppliedRuleSchema`
   - `RulesResultSchema`

5. `packages/shared/src/schemas/optimization.ts`
   - `PriceDemandPointSchema`
   - `OptimizationResultSchema`

6. `packages/shared/src/schemas/pricing.ts`
   - `PricingResultSchema`

7. `packages/shared/src/schemas/chat.ts`
   - `ChatRequestSchema`
   - `ChatResponseSchema`
   - `ChatStreamEventSchema`

### Task 3: Create Explainability Schemas (Priority 2)

1. `packages/shared/src/schemas/explainability.ts`
   - `FeatureContributionSchema`
   - `FeatureImportanceResultSchema`

2. `packages/shared/src/schemas/decision-trace.ts`
   - `TraceStepSchema`
   - `ModelAgreementSchema`
   - `DecisionTraceSchema`

3. `packages/shared/src/schemas/explanation.ts`
   - `ExplainRequestSchema`
   - `PriceExplanationSchema`

### Task 4: Create Evidence Schemas (Priority 3)

1. `packages/shared/src/schemas/evidence.ts`
   - All ModelCard related schemas
   - All DataCard related schemas
   - `MethodologyDocSchema`
   - `EvidenceResponseSchema`
   - `HoneywellMappingSchema`
   - `HoneywellMappingResponseSchema`

### Task 5: Create Sensitivity Schemas (Priority 4)

1. `packages/shared/src/schemas/sensitivity.ts`
   - All sensitivity-related schemas

### Task 6: Create Utility Schemas (Priority 5)

1. `packages/shared/src/schemas/health.ts`
   - `HealthResponseSchema`

2. `packages/shared/src/schemas/data.ts`
   - `PriceRangeSchema`
   - `DataSummaryResponseSchema`

### Task 7: Create Validated API Client

**File: `frontend/src/lib/api-client.ts`**

```typescript
import ky from 'ky';
import { z } from 'zod';
import { ErrorResponseSchema } from '@prismiq/shared/schemas';

const api = ky.create({
  prefixUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 30000,
});

/**
 * Generic validated fetch function
 */
export async function fetchValidated<T>(
  endpoint: string,
  schema: z.ZodType<T>,
  options?: Parameters<typeof api.get>[1]
): Promise<T> {
  const response = await api.get(endpoint, options).json();
  const result = schema.safeParse(response);
  
  if (!result.success) {
    console.error('API Response Validation Failed:', result.error.issues);
    throw new ValidationError(endpoint, result.error);
  }
  
  return result.data;
}

/**
 * Generic validated POST function
 */
export async function postValidated<T, B>(
  endpoint: string,
  body: B,
  responseSchema: z.ZodType<T>,
  requestSchema?: z.ZodType<B>
): Promise<T> {
  // Validate request body if schema provided
  if (requestSchema) {
    const bodyResult = requestSchema.safeParse(body);
    if (!bodyResult.success) {
      throw new ValidationError('request', bodyResult.error);
    }
  }
  
  const response = await api.post(endpoint, { json: body }).json();
  const result = responseSchema.safeParse(response);
  
  if (!result.success) {
    console.error('API Response Validation Failed:', result.error.issues);
    throw new ValidationError(endpoint, result.error);
  }
  
  return result.data;
}

class ValidationError extends Error {
  constructor(
    public endpoint: string,
    public zodError: z.ZodError
  ) {
    super(`Validation failed for ${endpoint}: ${zodError.message}`);
    this.name = 'ValidationError';
  }
}
```

### Task 8: Migrate Services to Use Validated Client

**Update: `frontend/src/services/chatService.ts`**

```typescript
import { postValidated } from '@/lib/api-client';
import { 
  ChatRequestSchema, 
  ChatResponseSchema,
  type ChatRequest,
  type ChatResponse 
} from '@prismiq/shared/schemas';

export async function sendMessage(request: ChatRequest): Promise<ChatResponse> {
  return postValidated(
    'api/v1/chat',
    request,
    ChatResponseSchema,
    ChatRequestSchema
  );
}
```

### Task 9: Update Stores to Use Validated Types

**Update: `frontend/src/stores/contextStore.ts`**

```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { 
  MarketContextSchema, 
  type MarketContext 
} from '@prismiq/shared/schemas';

// Use Zod for default value validation
const defaultContext = MarketContextSchema.parse({
  number_of_riders: 50,
  number_of_drivers: 25,
  location_category: 'Urban',
  customer_loyalty_status: 'Silver',
  // ... rest of defaults
});

// ... rest of store
```

### Task 10: Remove Duplicate Type Definitions

After migration is complete:

1. **Remove** `packages/shared/src/types/market.ts` (incorrect types)
2. **Remove** `packages/shared/src/types/pricing.ts` (incorrect types)
3. **Update** `packages/shared/src/types/index.ts` to re-export from schemas
4. **Remove** inline types from `frontend/src/components/evidence/types.ts`
5. **Remove** inline types from `frontend/src/components/visualizations/types.ts`
6. **Remove** inline types from `frontend/src/services/*.ts`

---

## Testing Strategy

### Unit Tests for Schemas

```typescript
// packages/shared/src/schemas/__tests__/market.test.ts
import { describe, it, expect } from 'bun:test';
import { MarketContextSchema } from '../market';

describe('MarketContextSchema', () => {
  it('validates correct input', () => {
    const valid = {
      number_of_riders: 50,
      number_of_drivers: 25,
      location_category: 'Urban',
      customer_loyalty_status: 'Gold',
      number_of_past_rides: 10,
      average_ratings: 4.5,
      time_of_booking: 'Evening',
      vehicle_type: 'Premium',
      expected_ride_duration: 30,
      historical_cost_of_ride: 35.0,
    };
    
    expect(() => MarketContextSchema.parse(valid)).not.toThrow();
  });

  it('rejects invalid number_of_riders', () => {
    const invalid = { ...validContext, number_of_riders: 200 };
    expect(() => MarketContextSchema.parse(invalid)).toThrow();
  });

  it('rejects invalid location_category', () => {
    const invalid = { ...validContext, location_category: 'Downtown' };
    expect(() => MarketContextSchema.parse(invalid)).toThrow();
  });
});
```

### Integration Tests

```typescript
// frontend/tests/integration/api-validation.test.ts
describe('API Response Validation', () => {
  it('validates real pricing response', async () => {
    const response = await fetchValidated(
      'api/v1/optimize-price',
      PricingResultSchema
    );
    
    // If we get here, validation passed
    expect(response.recommended_price).toBeGreaterThan(0);
  });
});
```

---

## Migration Checklist

### Phase 1: Foundation
- [ ] Install Zod in `packages/shared`
- [ ] Create `schemas/` directory structure
- [ ] Create `common.ts` with ErrorResponse
- [ ] Create `market.ts` with MarketContext

### Phase 2: Core Schemas
- [ ] Create `segment.ts`
- [ ] Create `rules.ts`
- [ ] Create `optimization.ts`
- [ ] Create `pricing.ts`
- [ ] Create `chat.ts`

### Phase 3: Explainability Schemas
- [ ] Create `explainability.ts`
- [ ] Create `decision-trace.ts`
- [ ] Create `explanation.ts`

### Phase 4: Evidence Schemas
- [ ] Create `evidence.ts` (large file, may split)

### Phase 5: Remaining Schemas
- [ ] Create `sensitivity.ts`
- [ ] Create `health.ts`
- [ ] Create `data.ts`

### Phase 6: Integration
- [ ] Create `api-client.ts` with validated fetch
- [ ] Update `chatService.ts`
- [ ] Update `evidenceService.ts`
- [ ] Update `contextStore.ts`
- [ ] Update `pricingStore.ts`

### Phase 7: Cleanup
- [ ] Remove old `types/*.ts` files
- [ ] Update all imports across frontend
- [ ] Remove inline type definitions
- [ ] Update component props to use schema types

### Phase 8: Testing
- [ ] Add schema unit tests
- [ ] Add integration tests
- [ ] Test all API endpoints with validation

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Schema drift from backend | Medium | High | Add CI check comparing Pydantic/Zod schemas |
| Breaking existing components | Medium | Medium | Incremental migration, types should be compatible |
| Bundle size increase | Low | Low | Zod is ~2KB gzipped, negligible |
| Validation overhead | Low | Low | Zod is fast, <1ms per validation |

---

## Success Criteria

1. **All API responses validated** at runtime using Zod
2. **Single source of truth** for types (Zod schemas, types inferred)
3. **No duplicate type definitions** across frontend
4. **Type alignment** with backend Pydantic models verified
5. **Unit test coverage** for all schemas
6. **Documentation** of any intentional schema differences

---

## Notes for Scrum Master

### Story Breakdown Suggestion

This work can be broken into **3-5 stories**:

1. **Story: Foundation & Core Schemas** (Priority 1)
   - Install Zod, create directory structure
   - Implement MarketContext, PricingResult, Chat schemas
   - Create validated API client utility
   - **Estimate: 3-5 points**

2. **Story: Explainability Schemas** (Priority 2)
   - Implement all explainability-related schemas
   - Includes DecisionTrace, PriceExplanation
   - **Estimate: 2-3 points**

3. **Story: Evidence Schemas** (Priority 3)
   - Implement ModelCard, DataCard, EvidenceResponse
   - Complex nested schemas
   - **Estimate: 3-4 points**

4. **Story: Service Migration** (Priority 2)
   - Migrate all services to use validated client
   - Update stores to use schema types
   - **Estimate: 2-3 points**

5. **Story: Cleanup & Testing** (Priority 3)
   - Remove duplicate types
   - Add comprehensive tests
   - Document any schema differences
   - **Estimate: 2-3 points**

### Dependencies

- Stories 2-4 depend on Story 1 (Foundation)
- Story 5 depends on Stories 2-4
- Can parallelize Stories 2 and 3

### Acceptance Criteria (Epic Level)

- [ ] All ~35 backend Pydantic schemas have corresponding Zod schemas
- [ ] Frontend services use validated API client
- [ ] No duplicate type definitions exist
- [ ] All existing tests continue to pass
- [ ] New schema unit tests added with >80% coverage
- [ ] Bundle size increase documented

---

*Document created: December 3, 2025*  
*Author: Winston (Architect Agent)*  
*Version: 1.0*

