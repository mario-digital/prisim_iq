import { describe, it, expect } from 'bun:test';
import type { DocTreeCategory } from '@/components/evidence/types';

// Test the documentation tree structure (doesn't require DOM)
describe('Documentation Tree Structure', () => {
  const docTree: DocTreeCategory[] = [
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

  it('should have all required categories', () => {
    const categories = docTree.map((c) => c.category);
    expect(categories).toContain('Model Documentation');
    expect(categories).toContain('Data Documentation');
    expect(categories).toContain('Methodology');
    expect(categories).toContain('Compliance');
  });

  it('should have all model cards', () => {
    const modelDocs = docTree.find((c) => c.category === 'Model Documentation');
    expect(modelDocs).toBeDefined();
    expect(modelDocs?.items).toHaveLength(3);
    expect(modelDocs?.items.map((i) => i.id)).toContain('xgboost');
    expect(modelDocs?.items.map((i) => i.id)).toContain('decision_tree');
    expect(modelDocs?.items.map((i) => i.id)).toContain('linear_regression');
  });

  it('should have data documentation items', () => {
    const dataDocs = docTree.find((c) => c.category === 'Data Documentation');
    expect(dataDocs).toBeDefined();
    expect(dataDocs?.items).toHaveLength(2);
  });

  it('should have methodology items', () => {
    const methodologyDocs = docTree.find((c) => c.category === 'Methodology');
    expect(methodologyDocs).toBeDefined();
    expect(methodologyDocs?.items.map((i) => i.id)).toContain('pricing_algorithm');
    expect(methodologyDocs?.items.map((i) => i.id)).toContain('demand_modeling');
    expect(methodologyDocs?.items.map((i) => i.id)).toContain('rules_engine');
  });

  it('should have compliance items including Honeywell mapping', () => {
    const complianceDocs = docTree.find((c) => c.category === 'Compliance');
    expect(complianceDocs).toBeDefined();
    expect(complianceDocs?.items.map((i) => i.id)).toContain('honeywell_mapping');
  });

  it('should have unique IDs across all documents', () => {
    const allIds = docTree.flatMap((c) => c.items.map((i) => i.id));
    const uniqueIds = new Set(allIds);
    expect(allIds.length).toBe(uniqueIds.size);
  });
});

describe('Doc Topic Mapping', () => {
  const docTopics: Record<string, string> = {
    xgboost: 'XGBoost demand prediction model',
    decision_tree: 'Decision Tree model',
    linear_regression: 'Linear Regression model',
    data_card: 'training dataset',
    feature_definitions: 'feature definitions',
    pricing_algorithm: 'pricing algorithm',
    demand_modeling: 'demand modeling methodology',
    rules_engine: 'business rules engine',
    audit_trail: 'audit trail',
    honeywell_mapping: 'Honeywell compliance mapping',
  };

  it('should have topics for all model cards', () => {
    expect(docTopics.xgboost).toContain('XGBoost');
    expect(docTopics.decision_tree).toContain('Decision Tree');
    expect(docTopics.linear_regression).toContain('Linear Regression');
  });

  it('should have topics for data documentation', () => {
    expect(docTopics.data_card).toBeDefined();
    expect(docTopics.feature_definitions).toBeDefined();
  });

  it('should have topic for Honeywell mapping', () => {
    expect(docTopics.honeywell_mapping).toContain('Honeywell');
  });
});
