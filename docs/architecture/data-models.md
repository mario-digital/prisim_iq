# 4. Data Models

## 4.1 MarketContext

**Purpose:** Represents the input context for a pricing request—all the factors that influence optimal price.

```typescript
// packages/shared/src/types/market.ts

export type LocationType = 'Urban' | 'Suburban' | 'Rural';
export type VehicleType = 'Economy' | 'Premium';
export type TimeOfDay = 'Morning' | 'Afternoon' | 'Evening' | 'Night';

export interface MarketContext {
  // Geographic
  location: LocationType;
  
  // Temporal
  timestamp: string;  // ISO 8601
  timeOfDay: TimeOfDay;
  
  // Supply & Demand
  riders: number;     // Current demand (10-100)
  drivers: number;    // Current supply (5-80)
  supplyDemandRatio: number;  // Calculated
  
  // Customer Profile
  customerSegment: string;
  loyaltyTier: 'Bronze' | 'Silver' | 'Gold' | 'Platinum';
  customerLifetimeValue?: number;
  
  // Vehicle
  vehicleType: VehicleType;
  
  // External Factors
  weatherCondition?: string;
  trafficLevel?: number;  // 0-1 scale
  competitorPrices?: number[];
  
  // Event Context
  isSpecialEvent?: boolean;
  eventType?: string;
}
```

## 4.2 PricingResult

**Purpose:** The output of a price optimization request, including the recommended price and all supporting data.

```typescript
// packages/shared/src/types/pricing.ts

export interface PricingResult {
  // Core Output
  recommendedPrice: number;
  basePrice: number;
  multiplier: number;
  
  // Confidence
  confidence: number;  // 0-1
  confidenceInterval: {
    lower: number;
    upper: number;
  };
  
  // Business Metrics
  expectedConversion: number;  // 0-1 probability
  expectedRevenue: number;
  demandAtPrice: number;
  
  // Constraints Applied
  rulesApplied: RuleApplication[];
  priceAdjustments: PriceAdjustment[];
  
  // Explainability
  explanation: PriceExplanation;
  
  // Metadata
  modelVersion: string;
  processingTimeMs: number;
  timestamp: string;
}

export interface RuleApplication {
  ruleId: string;
  ruleName: string;
  triggered: boolean;
  impact: number;  // Price delta
  reason: string;
}

export interface PriceAdjustment {
  factor: string;
  direction: 'increase' | 'decrease';
  magnitude: number;
  reason: string;
}

export interface PriceExplanation {
  narrative: string;  // Human-readable summary
  topFactors: FeatureContribution[];
  demandCurve: DemandPoint[];
  segmentInsights: string[];
}

export interface FeatureContribution {
  feature: string;
  value: number | string;
  impact: number;  // SHAP value
  direction: 'positive' | 'negative';
}

export interface DemandPoint {
  price: number;
  demand: number;
  revenue: number;
}
```

## 4.3 ChatMessage

**Purpose:** Represents a message in the chat conversation, supporting both user and assistant messages with optional tool results.

```typescript
// packages/shared/src/types/chat.ts

export type MessageRole = 'user' | 'assistant' | 'system';

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: string;
  
  // Optional structured data
  toolResults?: ToolResult[];
  visualizations?: VisualizationType[];
  context?: MarketContext;
  pricing?: PricingResult;
}

export interface ToolResult {
  toolName: string;
  success: boolean;
  result: unknown;
  executionTimeMs: number;
}

export type VisualizationType = 
  | 'demand_curve'
  | 'feature_importance'
  | 'price_comparison'
  | 'segment_analysis'
  | 'scenario_comparison';
```

## 4.4 Scenario

**Purpose:** Represents a saved scenario for comparison and analysis.

```typescript
// packages/shared/src/types/scenario.ts

export interface Scenario {
  id: string;
  name: string;
  description?: string;
  createdAt: string;
  updatedAt: string;
  
  // Input
  context: MarketContext;
  
  // Output
  result: PricingResult;
  
  // Metadata
  tags: string[];
  isFavorite: boolean;
}

export interface ScenarioComparison {
  scenarios: Scenario[];
  comparisonMetrics: ComparisonMetric[];
  insights: string[];
}

export interface ComparisonMetric {
  metric: string;
  values: { scenarioId: string; value: number }[];
  winner: string;  // scenarioId with best value
  difference: number;  // Percentage difference
}
```

---
