/**
 * Evidence service for fetching documentation and model/data cards.
 */
import ky from 'ky';
import { API_BASE_URL } from '@/lib/api';
import type {
  EvidenceResponse,
  HoneywellMappingResponse,
  ModelCard,
  DataCard,
} from '@/components/evidence/types';

const api = ky.create({
  prefixUrl: API_BASE_URL,
  timeout: 30000,
});

// Cache for evidence data
let cachedEvidence: EvidenceResponse | null = null;
let cachedHoneywellMapping: HoneywellMappingResponse | null = null;

// Fallback markdown content for when API is unavailable
const fallbackContent: Record<string, string> = {
  xgboost: `# XGBoost Demand Predictor

**Version:** 1.0.0

---

## Model Details

- **Architecture:** XGBoost Gradient Boosting Regressor
- **Framework:** XGBoost 2.1 / scikit-learn 1.5
- **Output:** Demand probability [0.0, 1.0]

### Performance Metrics

| Metric | Value |
|--------|-------|
| R² Score | 0.9859 |
| MAE | 0.0130 |
| RMSE | 0.0250 |

---

## Intended Use

Predict customer demand probability for dynamic ride pricing optimization.

## Limitations

- Trained on synthetic demand data
- Performance may degrade for extreme price points
- Limited to Economy and Premium vehicle types
`,
  decision_tree: `# Decision Tree Model

**Version:** 1.0.0

---

## Model Details

- **Architecture:** Decision Tree Regressor
- **Framework:** scikit-learn 1.5
- **Purpose:** Interpretable baseline model for demand prediction

### Key Characteristics

- High interpretability
- Fast inference
- Lower accuracy than XGBoost but more explainable
`,
  linear_regression: `# Linear Regression Model

**Version:** 1.0.0

---

## Model Details

- **Architecture:** Linear Regression
- **Framework:** scikit-learn 1.5
- **Purpose:** Simple baseline for comparison

### Coefficients

Shows the linear relationship between features and demand.
`,
  data_card: `# Dynamic Pricing Dataset

**Version:** 1.0.0

---

## Dataset Overview

- **Source:** Kaggle Dynamic Pricing Dataset (synthetic)
- **Size:** 1,000 samples
- **Features:** 11 columns

### Feature Categories

| Type | Count |
|------|-------|
| Numeric | 7 |
| Categorical | 4 |

---

## Known Biases

- Synthetic data may not reflect real-world patterns
- Premium vehicles slightly overrepresented
- Time of booking is bucketed, not continuous
`,
  feature_definitions: `# Feature Definitions

This document describes all features used in the PrismIQ models.

---

## Numerical Features

| Feature | Description | Range |
|---------|-------------|-------|
| Number_of_Riders | Customers requesting rides | 20-100 |
| Number_of_Drivers | Available drivers | 5-89 |
| Number_of_Past_Rides | Customer ride history | 0-100 |
| Average_Ratings | Customer rating | 3.5-5.0 |
| Expected_Ride_Duration | Trip duration (min) | 10-180 |
| Historical_Cost_of_Ride | Historical average cost | $25.99-$836.12 |
| supply_demand_ratio | Drivers/Riders ratio | 0.06-0.90 |

## Categorical Features

| Feature | Values |
|---------|--------|
| Location_Category | Urban, Suburban, Rural |
| Customer_Loyalty_Status | Regular, Silver, Gold |
| Time_of_Booking | Morning, Afternoon, Evening, Night |
| Vehicle_Type | Economy, Premium |
`,
  pricing_algorithm: `# Pricing Algorithm

The PrismIQ pricing algorithm optimizes ride prices using machine learning and business rules.

---

## Algorithm Flow

1. **Segment Classification** - K-Means clustering identifies market segment
2. **Demand Prediction** - XGBoost predicts demand at various price points
3. **Price Optimization** - Finds optimal price maximizing expected revenue
4. **Rule Application** - Business rules apply constraints and adjustments

## Optimization Objective

\`\`\`
Maximize: Price × Demand(Price)
Subject to: Business Rules Constraints
\`\`\`
`,
  demand_modeling: `# Demand Modeling Methodology

## Approach

Demand is modeled as a probability of ride acceptance given:
- Market conditions (supply/demand ratio)
- Customer profile (loyalty, history)
- Ride characteristics (duration, vehicle type)
- Proposed price

## Model Selection

XGBoost was selected as the primary model due to:
- High accuracy on tabular data
- Feature importance for explainability
- Fast inference for real-time pricing
`,
  rules_engine: `# Business Rules Engine

The rules engine applies domain constraints to ML predictions.

---

## Rule Categories

### Price Guards
- Minimum price floor: $10
- Maximum price ceiling: 3x historical cost
- Maximum surge multiplier: 2.5x

### Fairness Rules
- No discrimination by protected attributes
- Loyalty discount: Gold (10%), Silver (5%)

### Market Rules
- High demand surge: +20% when ratio < 0.3
- Low demand discount: -10% when ratio > 1.5
`,
  audit_trail: `# Audit Trail

All pricing decisions are logged for compliance and analysis.

---

## Logged Information

- Timestamp
- Market context (full input features)
- Model predictions
- Applied rules
- Final price
- Decision explanation

## Retention Policy

Logs retained for 7 years per regulatory requirements.
`,
  honeywell_mapping: `# Honeywell Compliance Mapping

This document maps PrismIQ capabilities to Honeywell's AI governance requirements.

---

## Transparency Requirements

| Requirement | PrismIQ Implementation |
|-------------|----------------------|
| Model documentation | Model Cards (JSON + Markdown) |
| Data documentation | Data Card with feature definitions |
| Decision explanation | SHAP values + decision traces |

## Fairness Requirements

| Requirement | PrismIQ Implementation |
|-------------|----------------------|
| Bias monitoring | Segment-based performance tracking |
| Protected attributes | Not used as features |
| Fairness audits | Documented in model cards |
`,
};

// Fallback model cards data
const fallbackModelCards: ModelCard[] = [
  {
    model_name: 'XGBoost Demand Predictor',
    model_version: '1.0.0',
    generated_at: new Date().toISOString(),
    model_details: {
      architecture: 'XGBoost Gradient Boosting Regressor',
      hyperparameters: { learning_rate: 0.1, max_depth: 7, n_estimators: 200 },
      training_date: '2024-12-01',
      framework: 'XGBoost 2.1 / scikit-learn 1.5',
      input_features: ['price', 'supply_demand_ratio', 'segment'],
      output: 'Demand probability [0.0, 1.0]',
    },
    intended_use: {
      primary_use: 'Predict customer demand probability',
      users: ['Pricing Analysts', 'Data Scientists'],
      out_of_scope: ['Real-time surge pricing without oversight'],
    },
    training_data: {
      dataset_name: 'PrismIQ Synthetic Training Data',
      dataset_size: 8000,
      features_used: ['price', 'supply_demand_ratio'],
      target_variable: 'demand',
      train_test_split: '80/20',
    },
    metrics: { r2_score: 0.9859, mae: 0.013, rmse: 0.025, test_set_size: 2000 },
    ethical_considerations: {
      fairness_considerations: ['Monitor performance across segments'],
      privacy_considerations: ['No PII used'],
      transparency_notes: ['SHAP values available'],
    },
    limitations: ['Trained on synthetic data'],
    feature_importance: { price: 0.22, historical_cost: 0.41 },
    coefficients: null,
  },
  {
    model_name: 'Decision Tree',
    model_version: '1.0.0',
    generated_at: new Date().toISOString(),
    model_details: {
      architecture: 'Decision Tree Regressor',
      hyperparameters: { max_depth: 10 },
      training_date: '2024-12-01',
      framework: 'scikit-learn 1.5',
      input_features: ['price', 'supply_demand_ratio'],
      output: 'Demand probability',
    },
    intended_use: {
      primary_use: 'Interpretable baseline model',
      users: ['Auditors'],
      out_of_scope: [],
    },
    training_data: {
      dataset_name: 'PrismIQ Synthetic Training Data',
      dataset_size: 8000,
      features_used: ['price'],
      target_variable: 'demand',
      train_test_split: '80/20',
    },
    metrics: { r2_score: 0.85, mae: 0.05, rmse: 0.08, test_set_size: 2000 },
    ethical_considerations: {
      fairness_considerations: [],
      privacy_considerations: [],
      transparency_notes: ['Fully interpretable'],
    },
    limitations: ['Lower accuracy'],
    feature_importance: { price: 0.3 },
    coefficients: null,
  },
  {
    model_name: 'Linear Regression',
    model_version: '1.0.0',
    generated_at: new Date().toISOString(),
    model_details: {
      architecture: 'Linear Regression',
      hyperparameters: {},
      training_date: '2024-12-01',
      framework: 'scikit-learn 1.5',
      input_features: ['price'],
      output: 'Demand probability',
    },
    intended_use: {
      primary_use: 'Simple baseline',
      users: ['Analysts'],
      out_of_scope: [],
    },
    training_data: {
      dataset_name: 'PrismIQ Synthetic Training Data',
      dataset_size: 8000,
      features_used: ['price'],
      target_variable: 'demand',
      train_test_split: '80/20',
    },
    metrics: { r2_score: 0.75, mae: 0.08, rmse: 0.12, test_set_size: 2000 },
    ethical_considerations: {
      fairness_considerations: [],
      privacy_considerations: [],
      transparency_notes: ['Coefficients available'],
    },
    limitations: ['Linear assumption'],
    feature_importance: {},
    coefficients: { price: -0.5, intercept: 1.0 },
  },
];

// Fallback data card
const fallbackDataCard: DataCard = {
  dataset_name: 'Dynamic Pricing Dataset',
  version: '1.0.0',
  generated_at: new Date().toISOString(),
  source: {
    origin: 'Kaggle Dynamic Pricing Dataset (synthetic)',
    collection_date: '2024',
    preprocessing_steps: ['Loaded from Excel', 'Computed supply_demand_ratio'],
  },
  features: [],
  statistics: {
    row_count: 1000,
    column_count: 11,
    missing_values: 0,
    numeric_features: 7,
    categorical_features: 4,
  },
  known_biases: ['Synthetic data'],
  limitations: ['Sample size of 1,000 rows'],
  intended_use: 'Training and evaluation of demand prediction models',
};

/**
 * Fetch evidence data (model cards, data card, methodology).
 * Uses caching to avoid repeated API calls.
 */
export async function getEvidence(): Promise<EvidenceResponse> {
  if (cachedEvidence) return cachedEvidence;

  try {
    cachedEvidence = await api.get('api/v1/evidence').json<EvidenceResponse>();
    return cachedEvidence;
  } catch (error) {
    console.warn('Failed to fetch evidence from API, using fallback:', error);
    // Return fallback data when API is unavailable
    cachedEvidence = {
      model_cards: fallbackModelCards,
      data_card: fallbackDataCard,
      methodology: {},
      markdown_content: fallbackContent,
    };
    return cachedEvidence;
  }
}

/**
 * Fetch Honeywell compliance mapping.
 */
export async function getHoneywellMapping(): Promise<HoneywellMappingResponse> {
  if (cachedHoneywellMapping) return cachedHoneywellMapping;

  try {
    cachedHoneywellMapping = await api
      .get('api/v1/honeywell_mapping')
      .json<HoneywellMappingResponse>();
    return cachedHoneywellMapping;
  } catch (error) {
    console.warn('Failed to fetch Honeywell mapping, using fallback:', error);
    cachedHoneywellMapping = {
      mapping: {},
      compliance_notes: ['Fallback data - API unavailable'],
    };
    return cachedHoneywellMapping;
  }
}

/**
 * Get markdown content for a specific document.
 * First tries API, then falls back to local content.
 */
export async function getDocContent(docId: string): Promise<string> {
  try {
    // Try to get from cached evidence first
    const evidence = await getEvidence();
    if (evidence.markdown_content?.[docId]) {
      return evidence.markdown_content[docId];
    }

    // Try API endpoint for specific document
    const response = await api.get(`api/v1/evidence/docs/${docId}`).text();
    return response;
  } catch (error) {
    console.warn(`Failed to fetch doc ${docId} from API, using fallback:`, error);
    // Return fallback content
    return (
      fallbackContent[docId] ||
      `# ${docId.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}\n\nDocumentation coming soon.`
    );
  }
}

/**
 * Clear the evidence cache (useful for testing or forced refresh).
 */
export function clearEvidenceCache(): void {
  cachedEvidence = null;
  cachedHoneywellMapping = null;
}

