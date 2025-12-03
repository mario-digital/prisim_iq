import { describe, it, expect } from 'bun:test';
import {
  ModelCardSchema,
  DataCardSchema,
  EvidenceResponseSchema,
  HoneywellMappingSchema,
  HoneywellMappingResponseSchema,
  DocSectionSchema,
  MethodologyDocSchema,
} from '../evidence';

describe('ModelCardSchema', () => {
  const validModelCard = {
    model_name: 'XGBoost Demand Predictor',
    model_version: '1.0.0',
    generated_at: '2024-12-01T10:00:00Z',
    model_details: {
      architecture: 'XGBoost Gradient Boosting Regressor',
      hyperparameters: { learning_rate: 0.1, max_depth: 7 },
      training_date: '2024-12-01',
      framework: 'XGBoost 2.1',
      input_features: ['price', 'segment'],
      output: 'Demand probability',
    },
    intended_use: {
      primary_use: 'Predict demand',
      users: ['Data Scientists'],
      out_of_scope: ['Real-time pricing'],
    },
    training_data: {
      dataset_name: 'Synthetic Data',
      dataset_size: 8000,
      features_used: ['price'],
      target_variable: 'demand',
      train_test_split: '80/20',
    },
    metrics: {
      r2_score: 0.9859,
      mae: 0.013,
      rmse: 0.025,
      test_set_size: 2000,
    },
    ethical_considerations: {
      fairness_considerations: ['Monitor across segments'],
      privacy_considerations: ['No PII'],
      transparency_notes: ['SHAP available'],
    },
    limitations: ['Synthetic data only'],
  };

  it('validates correct input', () => {
    expect(() => ModelCardSchema.parse(validModelCard)).not.toThrow();
  });

  it('accepts optional feature_importance', () => {
    const withImportance = {
      ...validModelCard,
      feature_importance: { price: 0.22, segment: 0.41 },
    };
    expect(() => ModelCardSchema.parse(withImportance)).not.toThrow();
  });

  it('accepts optional coefficients', () => {
    const withCoefficients = {
      ...validModelCard,
      coefficients: { price: -0.5, intercept: 1.0 },
    };
    expect(() => ModelCardSchema.parse(withCoefficients)).not.toThrow();
  });

  it('accepts null feature_importance', () => {
    const withNull = {
      ...validModelCard,
      feature_importance: null,
    };
    expect(() => ModelCardSchema.parse(withNull)).not.toThrow();
  });

  it('rejects invalid timestamp', () => {
    const invalid = { ...validModelCard, generated_at: 'not-a-date' };
    expect(() => ModelCardSchema.parse(invalid)).toThrow();
  });
});

describe('DataCardSchema', () => {
  const validDataCard = {
    dataset_name: 'Dynamic Pricing Dataset',
    version: '1.0.0',
    generated_at: '2024-12-01T10:00:00Z',
    source: {
      origin: 'Kaggle',
      collection_date: '2024',
      preprocessing_steps: ['Loaded from Excel'],
    },
    features: [
      {
        name: 'price',
        dtype: 'float64',
        description: 'Price in dollars',
        range_or_values: '10-100',
        distribution: 'continuous',
      },
    ],
    statistics: {
      row_count: 1000,
      column_count: 11,
      missing_values: 0,
      numeric_features: 7,
      categorical_features: 4,
    },
    known_biases: ['Synthetic data'],
    limitations: ['Small sample'],
    intended_use: 'Training models',
  };

  it('validates correct input', () => {
    expect(() => DataCardSchema.parse(validDataCard)).not.toThrow();
  });

  it('validates feature distribution enum', () => {
    const withCategorical = {
      ...validDataCard,
      features: [
        {
          name: 'vehicle_type',
          dtype: 'category',
          description: 'Vehicle type',
          range_or_values: 'Economy, Premium',
          distribution: 'categorical',
        },
      ],
    };
    expect(() => DataCardSchema.parse(withCategorical)).not.toThrow();
  });

  it('rejects invalid distribution type', () => {
    const invalid = {
      ...validDataCard,
      features: [
        {
          name: 'price',
          dtype: 'float64',
          description: 'Price',
          range_or_values: '10-100',
          distribution: 'normal', // Invalid - should be continuous or categorical
        },
      ],
    };
    expect(() => DataCardSchema.parse(invalid)).toThrow();
  });
});

describe('DocSectionSchema', () => {
  it('validates simple section', () => {
    const section = {
      heading: 'Overview',
      content: '# Introduction\n\nThis is the overview.',
    };
    expect(() => DocSectionSchema.parse(section)).not.toThrow();
  });

  it('validates section with subsections', () => {
    const section = {
      heading: 'Methodology',
      content: 'Main content here.',
      subsections: [
        { heading: 'Approach', content: 'Approach details.' },
        { heading: 'Results', content: 'Results details.' },
      ],
    };
    expect(() => DocSectionSchema.parse(section)).not.toThrow();
  });

  it('validates deeply nested subsections', () => {
    const section = {
      heading: 'Level 1',
      content: 'Content 1',
      subsections: [
        {
          heading: 'Level 2',
          content: 'Content 2',
          subsections: [{ heading: 'Level 3', content: 'Content 3' }],
        },
      ],
    };
    expect(() => DocSectionSchema.parse(section)).not.toThrow();
  });

  it('accepts null subsections', () => {
    const section = {
      heading: 'Simple',
      content: 'Content',
      subsections: null,
    };
    expect(() => DocSectionSchema.parse(section)).not.toThrow();
  });
});

describe('MethodologyDocSchema', () => {
  it('validates correct input', () => {
    const doc = {
      title: 'PrismIQ Methodology',
      sections: [
        { heading: 'Overview', content: 'Overview content.' },
        { heading: 'Approach', content: 'Approach content.' },
      ],
    };
    expect(() => MethodologyDocSchema.parse(doc)).not.toThrow();
  });

  it('accepts empty sections', () => {
    const doc = {
      title: 'Empty Doc',
      sections: [],
    };
    expect(() => MethodologyDocSchema.parse(doc)).not.toThrow();
  });
});

describe('HoneywellMappingSchema', () => {
  it('validates correct input', () => {
    const mapping = {
      ride_sharing_concept: 'Number of Riders',
      honeywell_equivalent: 'Product Demand Forecast',
      category: 'demand',
      rationale: 'Both represent demand signals',
      applicability: 'Any product with variable demand',
    };
    expect(() => HoneywellMappingSchema.parse(mapping)).not.toThrow();
  });

  it('validates all category values', () => {
    const categories = ['pricing', 'demand', 'supply', 'customer'];
    for (const category of categories) {
      const mapping = {
        ride_sharing_concept: 'Concept',
        honeywell_equivalent: 'Equivalent',
        category,
        rationale: 'Rationale',
        applicability: 'Applicability',
      };
      expect(() => HoneywellMappingSchema.parse(mapping)).not.toThrow();
    }
  });

  it('rejects invalid category', () => {
    const mapping = {
      ride_sharing_concept: 'Concept',
      honeywell_equivalent: 'Equivalent',
      category: 'invalid',
      rationale: 'Rationale',
      applicability: 'Applicability',
    };
    expect(() => HoneywellMappingSchema.parse(mapping)).toThrow();
  });
});

describe('HoneywellMappingResponseSchema', () => {
  it('validates correct input', () => {
    const response = {
      title: 'Ride-Sharing to Honeywell Mapping',
      description: 'How concepts translate',
      mappings: [
        {
          ride_sharing_concept: 'Riders',
          honeywell_equivalent: 'Demand',
          category: 'demand',
          rationale: 'Both are demand',
          applicability: 'Universal',
        },
      ],
      business_context: 'ML-driven pricing applies to enterprise',
    };
    expect(() => HoneywellMappingResponseSchema.parse(response)).not.toThrow();
  });

  it('accepts optional rendered_markdown', () => {
    const response = {
      title: 'Title',
      description: 'Description',
      mappings: [],
      business_context: 'Context',
      rendered_markdown: '# Markdown Content',
    };
    const result = HoneywellMappingResponseSchema.parse(response);
    expect(result.rendered_markdown).toBe('# Markdown Content');
  });

  it('accepts null rendered_markdown', () => {
    const response = {
      title: 'Title',
      description: 'Description',
      mappings: [],
      business_context: 'Context',
      rendered_markdown: null,
    };
    expect(() => HoneywellMappingResponseSchema.parse(response)).not.toThrow();
  });
});

describe('EvidenceResponseSchema', () => {
  const validModelCard = {
    model_name: 'XGBoost',
    model_version: '1.0.0',
    generated_at: '2024-12-01T10:00:00Z',
    model_details: {
      architecture: 'XGBoost',
      hyperparameters: {},
      training_date: '2024',
      framework: 'XGBoost',
      input_features: ['price'],
      output: 'demand',
    },
    intended_use: {
      primary_use: 'Prediction',
      users: [],
      out_of_scope: [],
    },
    training_data: {
      dataset_name: 'Data',
      dataset_size: 1000,
      features_used: [],
      target_variable: 'demand',
      train_test_split: '80/20',
    },
    metrics: { r2_score: 0.9, mae: 0.1, rmse: 0.15, test_set_size: 200 },
    ethical_considerations: {
      fairness_considerations: [],
      privacy_considerations: [],
      transparency_notes: [],
    },
    limitations: [],
  };

  const validDataCard = {
    dataset_name: 'Dataset',
    version: '1.0.0',
    generated_at: '2024-12-01T10:00:00Z',
    source: { origin: 'Test', collection_date: '2024', preprocessing_steps: [] },
    features: [],
    statistics: {
      row_count: 1000,
      column_count: 10,
      missing_values: 0,
      numeric_features: 7,
      categorical_features: 3,
    },
    known_biases: [],
    limitations: [],
    intended_use: 'Training',
  };

  it('validates correct input', () => {
    const response = {
      model_cards: [validModelCard],
      data_card: validDataCard,
      methodology: { title: 'Methodology', sections: [] },
      generated_at: '2024-12-01T10:00:00Z',
    };
    expect(() => EvidenceResponseSchema.parse(response)).not.toThrow();
  });

  it('defaults cache_ttl_seconds to 86400', () => {
    const response = {
      model_cards: [],
      data_card: validDataCard,
      methodology: { title: 'Methodology', sections: [] },
      generated_at: '2024-12-01T10:00:00Z',
    };
    const result = EvidenceResponseSchema.parse(response);
    expect(result.cache_ttl_seconds).toBe(86400);
  });

  it('accepts custom cache_ttl_seconds', () => {
    const response = {
      model_cards: [],
      data_card: validDataCard,
      methodology: { title: 'Methodology', sections: [] },
      generated_at: '2024-12-01T10:00:00Z',
      cache_ttl_seconds: 3600,
    };
    const result = EvidenceResponseSchema.parse(response);
    expect(result.cache_ttl_seconds).toBe(3600);
  });
});

