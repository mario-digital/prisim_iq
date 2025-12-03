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

