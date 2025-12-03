/**
 * Types for Evidence & Methods components.
 */

export interface DocTreeItem {
  id: string;
  label: string;
}

export interface DocTreeCategory {
  category: string;
  items: DocTreeItem[];
}

/**
 * All valid document IDs used in the evidence navigation tree.
 * This is the single source of truth for document identifiers.
 */
export const DOC_IDS = [
  'xgboost',
  'decision_tree',
  'linear_regression',
  'data_card',
  'feature_definitions',
  'pricing_algorithm',
  'demand_modeling',
  'rules_engine',
  'audit_trail',
  'honeywell_mapping',
] as const;

/** Union type of all valid document IDs for type safety */
export type DocId = (typeof DOC_IDS)[number];

/**
 * Centralized document tree structure.
 * Single source of truth for navigation - imported by components and tests.
 * 
 * @remarks
 * All item.id values MUST be unique across the entire tree.
 * This is enforced at compile-time via the DocId type and
 * validated at runtime in tests.
 */
export const DOC_TREE: DocTreeCategory[] = [
  {
    category: 'Model Documentation',
    items: [
      { id: 'xgboost', label: 'XGBoost Model Card' },
      { id: 'decision_tree', label: 'Decision Tree Model Card' },
      { id: 'linear_regression', label: 'Linear Regression Model Card' },
    ],
  },
  {
    category: 'Data Documentation',
    items: [
      { id: 'data_card', label: 'Dataset Card' },
      { id: 'feature_definitions', label: 'Feature Definitions' },
    ],
  },
  {
    category: 'Methodology',
    items: [
      { id: 'pricing_algorithm', label: 'Pricing Algorithm' },
      { id: 'demand_modeling', label: 'Demand Modeling' },
      { id: 'rules_engine', label: 'Business Rules' },
    ],
  },
  {
    category: 'Compliance',
    items: [
      { id: 'audit_trail', label: 'Audit Trail' },
      { id: 'honeywell_mapping', label: 'Honeywell Mapping' },
    ],
  },
];

/**
 * Helper to get all document IDs from the tree.
 * Useful for validation and iteration.
 */
export function getAllDocIds(): string[] {
  return DOC_TREE.flatMap((category) => category.items.map((item) => item.id));
}

/**
 * Validates that all IDs in DOC_TREE are unique.
 * Call this in tests to ensure tree integrity.
 */
export function validateDocTreeUniqueness(): { valid: boolean; duplicates: string[] } {
  const ids = getAllDocIds();
  const seen = new Set<string>();
  const duplicates: string[] = [];
  
  for (const id of ids) {
    if (seen.has(id)) {
      duplicates.push(id);
    }
    seen.add(id);
  }
  
  return { valid: duplicates.length === 0, duplicates };
}

export interface ModelCardMetrics {
  r2_score: number;
  mae: number;
  rmse: number;
  test_set_size: number;
}

export interface ModelCard {
  model_name: string;
  model_version: string;
  generated_at: string;
  model_details: {
    architecture: string;
    hyperparameters: Record<string, number | string>;
    training_date: string;
    framework: string;
    input_features: string[];
    output: string;
  };
  intended_use: {
    primary_use: string;
    users: string[];
    out_of_scope: string[];
  };
  training_data: {
    dataset_name: string;
    dataset_size: number;
    features_used: string[];
    target_variable: string;
    train_test_split: string;
  };
  metrics: ModelCardMetrics;
  ethical_considerations: {
    fairness_considerations: string[];
    privacy_considerations: string[];
    transparency_notes: string[];
  };
  limitations: string[];
  feature_importance: Record<string, number>;
  coefficients: Record<string, number> | null;
}

export interface DataCardFeature {
  name: string;
  dtype: string;
  description: string;
  range_or_values: string;
  distribution: string;
}

export interface DataCard {
  dataset_name: string;
  version: string;
  generated_at: string;
  source: {
    origin: string;
    collection_date: string;
    preprocessing_steps: string[];
  };
  features: DataCardFeature[];
  statistics: {
    row_count: number;
    column_count: number;
    missing_values: number;
    numeric_features: number;
    categorical_features: number;
  };
  known_biases: string[];
  limitations: string[];
  intended_use: string;
}

export interface EvidenceResponse {
  model_cards: ModelCard[];
  data_card: DataCard;
  methodology: Record<string, string>;
  markdown_content: Record<string, string>;
}

export interface HoneywellMappingResponse {
  mapping: Record<string, string>;
  compliance_notes: string[];
}

