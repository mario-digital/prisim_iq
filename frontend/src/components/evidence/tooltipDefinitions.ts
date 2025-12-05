/**
 * Tooltip definitions for the Evidence & Methods tab.
 * Provides human-readable explanations for metrics, terms, and concepts.
 */

// ============================================================================
// Model Metrics
// ============================================================================

export const modelMetricTooltips = {
  // R² Score
  r2_score: {
    metric: 'R² Score (Coefficient of Determination)',
    description:
      'Measures how well the model explains variance in demand. A score of 0.98 means the model explains 98% of demand variation. Higher is better, with 1.0 being perfect.',
  },
  // MAE
  mae: {
    metric: 'Mean Absolute Error',
    description:
      'Average prediction error in the same units as demand. Lower values mean more accurate predictions. An MAE of 0.013 means predictions are off by about 1.3% on average.',
  },
  // RMSE
  rmse: {
    metric: 'Root Mean Square Error',
    description:
      'Measures prediction accuracy, penalizing larger errors more heavily. Lower is better. Useful for catching outlier predictions that could impact pricing decisions.',
  },
  // Model Version
  version: {
    metric: 'Model Version',
    description:
      'The current deployed version of this model. Version numbers help track model updates and ensure reproducibility of pricing decisions.',
  },
  // Architecture
  architecture: {
    metric: 'Model Architecture',
    description:
      'The underlying algorithm type. XGBoost uses gradient boosting, Random Forest uses ensemble decision trees, and Linear Regression uses statistical regression.',
  },
};

// ============================================================================
// Dataset Metrics
// ============================================================================

export const datasetMetricTooltips = {
  dataset_name: {
    metric: 'Dataset Name',
    description:
      'The name of the training dataset used to build and validate our pricing models.',
  },
  version: {
    metric: 'Dataset Version',
    description:
      'Version identifier for the training data. New versions indicate updated or expanded training data.',
  },
  row_count: {
    metric: 'Row Count',
    description:
      'Total number of historical pricing records used for training. More data generally leads to better model performance.',
  },
  column_count: {
    metric: 'Column Count',
    description:
      'Total features (variables) available in the dataset, including both inputs and targets.',
  },
  numeric_features: {
    metric: 'Numeric Features',
    description:
      'Count of numerical variables like price, distance, duration, and demand metrics that the model uses for predictions.',
  },
  categorical_features: {
    metric: 'Categorical Features',
    description:
      'Count of category-based variables like vehicle type, location category, and customer segment used for segmentation.',
  },
};

// ============================================================================
// Quick Reference Cards
// ============================================================================

export const cardTooltips = {
  model_card: {
    title: 'Model Card',
    description:
      'A standardized documentation format for ML models. Contains performance metrics, intended use cases, limitations, and ethical considerations. Helps stakeholders understand model capabilities and constraints.',
  },
  data_card: {
    title: 'Data Card',
    description:
      'Documentation of the training dataset including its source, composition, quality, and any preprocessing applied. Essential for understanding what the models learned from.',
  },
  xgboost: {
    title: 'XGBoost Model',
    description:
      'Our primary demand prediction model using gradient boosting. Known for high accuracy on tabular data. Used as the main predictor with other models providing validation.',
  },
  random_forest: {
    title: 'Random Forest Model',
    description:
      'An ensemble model that combines multiple decision trees. Provides robust predictions and helps validate XGBoost results. Good at handling non-linear relationships.',
  },
  linear_regression: {
    title: 'Linear Regression Model',
    description:
      'A simple, interpretable baseline model. While less accurate for complex patterns, it provides explainable predictions and serves as a sanity check for other models.',
  },
};

// ============================================================================
// Documentation Table Values
// ============================================================================

export const getValueTooltip = (
  metricKey: string,
  value: number | string
): string => {
  const numValue = typeof value === 'string' ? parseFloat(value) : value;

  switch (metricKey) {
    case 'r2_score':
      if (numValue >= 0.95)
        return 'Excellent fit - model captures nearly all variance';
      if (numValue >= 0.85) return 'Good fit - model is highly predictive';
      if (numValue >= 0.7) return 'Moderate fit - acceptable for most use cases';
      return 'Lower fit - model may need improvement';

    case 'mae':
      if (numValue <= 0.02)
        return 'Very low error - predictions are highly accurate';
      if (numValue <= 0.05)
        return 'Low error - predictions are reliable for pricing';
      return 'Higher error - consider with other factors';

    case 'rmse':
      if (numValue <= 0.03)
        return 'Very low RMSE - minimal prediction variance';
      if (numValue <= 0.08)
        return 'Low RMSE - predictions are consistent';
      return 'Higher RMSE - some predictions may vary';

    case 'row_count':
      if (numValue >= 100000)
        return 'Large dataset - supports complex pattern learning';
      if (numValue >= 10000)
        return 'Adequate dataset size for reliable predictions';
      return 'Smaller dataset - may limit model complexity';

    default:
      return `Current value: ${value}`;
  }
};

// ============================================================================
// Helper to get metric tooltip
// ============================================================================

export const getMetricTooltip = (
  key: string
): { metric: string; description: string } | undefined => {
  return (
    modelMetricTooltips[key as keyof typeof modelMetricTooltips] ||
    datasetMetricTooltips[key as keyof typeof datasetMetricTooltips]
  );
};

