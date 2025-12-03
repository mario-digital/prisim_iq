import { describe, it, expect, beforeEach } from 'bun:test';
import { createElement } from 'react';
import { renderToString } from 'react-dom/server';
import { usePricingStore } from '@/stores/pricingStore';
import { useLayoutStore } from '@/stores/layoutStore';
import type { PriceExplanation } from '@/components/visualizations/types';
import { RecommendationCard } from '@/components/visualizations/RecommendationCard';
import { FeatureImportanceChart } from '@/components/visualizations/FeatureImportanceChart';
import { DecisionTrace } from '@/components/visualizations/DecisionTrace';
import { BusinessRulesList } from '@/components/visualizations/BusinessRulesList';

/**
 * Mock explanation data for testing.
 */
const mockExplanation: PriceExplanation = {
  result: {
    recommendedPrice: 99.99,
    basePrice: 89.99,
    priceAdjustment: 11.1,
    confidence: 'high',
    confidenceScore: 0.85,
    segment: 'value_seeker',
    factors: [
      { name: 'demand', impact: 5.0, description: 'High demand', weight: 0.3 },
    ],
    expectedDemand: 150,
    expectedRevenue: 14998.5,
    explanation: 'Price optimized based on market conditions',
    timestamp: new Date().toISOString(),
  },
  featureContributions: [
    {
      name: 'demand_level',
      displayName: 'Demand Level',
      importance: 0.35,
      direction: 'positive',
      currentValue: 0.8,
    },
    {
      name: 'competitor_price',
      displayName: 'Competitor Price',
      importance: 0.25,
      direction: 'negative',
      currentValue: 95.0,
    },
    {
      name: 'inventory',
      displayName: 'Inventory Level',
      importance: 0.2,
      direction: 'positive',
      currentValue: 500,
    },
  ],
  decisionTrace: [
    {
      id: 'step-1',
      name: 'Data Loading',
      description: 'Load market context data',
      durationMs: 12,
      status: 'success',
      inputs: { segment: 'value_seeker' },
      outputs: { loaded: true },
    },
    {
      id: 'step-2',
      name: 'Model Prediction',
      description: 'Run price optimization model',
      durationMs: 45,
      status: 'success',
      inputs: { basePrice: 89.99 },
      outputs: { predictedPrice: 99.99 },
    },
  ],
  demandCurve: [
    { price: 79.99, value: 200 },
    { price: 89.99, value: 175 },
    { price: 99.99, value: 150 },
    { price: 109.99, value: 120 },
    { price: 119.99, value: 90 },
  ],
  profitCurve: [
    { price: 79.99, value: 1500 },
    { price: 89.99, value: 2000 },
    { price: 99.99, value: 2200 },
    { price: 109.99, value: 2100 },
    { price: 119.99, value: 1800 },
  ],
  sensitivity: {
    basePrice: 99.99,
    lowerBound: 94.99,
    upperBound: 104.99,
    robustnessScore: 0.82,
    pricePoints: [
      { price: 94.99, value: 2100 },
      { price: 99.99, value: 2200 },
      { price: 104.99, value: 2150 },
    ],
    confidenceLevel: 95,
  },
  businessRules: [
    {
      id: 'rule-1',
      name: 'Minimum Margin',
      description: 'Ensure 20% minimum profit margin',
      triggered: true,
      priceBefore: 95.99,
      priceAfter: 99.99,
      impact: 4.0,
      type: 'margin',
    },
    {
      id: 'rule-2',
      name: 'Price Ceiling',
      description: 'Maximum price cap at $150',
      triggered: false,
      priceBefore: 99.99,
      priceAfter: 99.99,
      impact: 0,
      type: 'ceiling',
    },
  ],
  optimalPrice: 99.99,
  expectedProfit: 2200,
  profitUpliftPercent: 15.5,
};

describe('Pricing Store', () => {
  beforeEach(() => {
    // Reset store state before each test
    usePricingStore.getState().clear();
  });

  it('should start with null explanation', () => {
    const { explanation } = usePricingStore.getState();
    expect(explanation).toBeNull();
  });

  it('should start with loading false', () => {
    const { isLoading } = usePricingStore.getState();
    expect(isLoading).toBe(false);
  });

  it('should set explanation data', () => {
    const { setExplanation } = usePricingStore.getState();

    setExplanation(mockExplanation);

    const { explanation, isLoading, error } = usePricingStore.getState();
    expect(explanation).not.toBeNull();
    expect(explanation?.result.recommendedPrice).toBe(99.99);
    expect(isLoading).toBe(false);
    expect(error).toBeNull();
  });

  it('should set loading state', () => {
    const { setLoading } = usePricingStore.getState();

    setLoading(true);
    expect(usePricingStore.getState().isLoading).toBe(true);

    setLoading(false);
    expect(usePricingStore.getState().isLoading).toBe(false);
  });

  it('should set error state', () => {
    const { setError } = usePricingStore.getState();

    setError('Failed to optimize price');

    const { error, isLoading } = usePricingStore.getState();
    expect(error).toBe('Failed to optimize price');
    expect(isLoading).toBe(false);
  });

  it('should clear all data', () => {
    const { setExplanation, clear } = usePricingStore.getState();

    setExplanation(mockExplanation);
    expect(usePricingStore.getState().explanation).not.toBeNull();

    clear();

    const { explanation, isLoading, error } = usePricingStore.getState();
    expect(explanation).toBeNull();
    expect(isLoading).toBe(false);
    expect(error).toBeNull();
  });

  it('should clear error when setting loading true', () => {
    const { setError, setLoading } = usePricingStore.getState();

    setError('Some error');
    expect(usePricingStore.getState().error).toBe('Some error');

    setLoading(true);
    expect(usePricingStore.getState().error).toBeNull();
  });

  it('should clear loading and error when setting explanation', () => {
    const { setLoading, setError, setExplanation } = usePricingStore.getState();

    setLoading(true);
    setError('Some error');

    setExplanation(mockExplanation);

    const { isLoading, error } = usePricingStore.getState();
    expect(isLoading).toBe(false);
    expect(error).toBeNull();
  });
});

describe('Mock Explanation Data', () => {
  it('should have valid feature contributions', () => {
    expect(mockExplanation.featureContributions.length).toBeGreaterThan(0);

    mockExplanation.featureContributions.forEach((feature) => {
      expect(feature.importance).toBeGreaterThanOrEqual(0);
      expect(feature.importance).toBeLessThanOrEqual(1);
      expect(['positive', 'negative', 'neutral']).toContain(feature.direction);
    });
  });

  it('should have valid decision trace steps', () => {
    expect(mockExplanation.decisionTrace.length).toBeGreaterThan(0);

    mockExplanation.decisionTrace.forEach((step) => {
      expect(step.durationMs).toBeGreaterThanOrEqual(0);
      expect(['success', 'warning', 'error']).toContain(step.status);
    });
  });

  it('should have valid demand curve data', () => {
    expect(mockExplanation.demandCurve.length).toBeGreaterThan(0);

    // Demand should decrease as price increases
    for (let i = 1; i < mockExplanation.demandCurve.length; i++) {
      expect(mockExplanation.demandCurve[i].price).toBeGreaterThan(
        mockExplanation.demandCurve[i - 1].price
      );
      expect(mockExplanation.demandCurve[i].value).toBeLessThan(
        mockExplanation.demandCurve[i - 1].value
      );
    }
  });

  it('should have valid profit curve data', () => {
    expect(mockExplanation.profitCurve.length).toBeGreaterThan(0);

    // Find max profit point
    const maxProfit = Math.max(...mockExplanation.profitCurve.map((p) => p.value));
    expect(maxProfit).toBeGreaterThan(0);
  });

  it('should have valid sensitivity data', () => {
    const { sensitivity } = mockExplanation;

    expect(sensitivity.lowerBound).toBeLessThan(sensitivity.basePrice);
    expect(sensitivity.upperBound).toBeGreaterThan(sensitivity.basePrice);
    expect(sensitivity.robustnessScore).toBeGreaterThanOrEqual(0);
    expect(sensitivity.robustnessScore).toBeLessThanOrEqual(1);
    expect(sensitivity.confidenceLevel).toBeGreaterThan(0);
    expect(sensitivity.confidenceLevel).toBeLessThanOrEqual(100);
  });

  it('should have valid business rules', () => {
    expect(mockExplanation.businessRules.length).toBeGreaterThan(0);

    const triggeredRules = mockExplanation.businessRules.filter((r) => r.triggered);
    expect(triggeredRules.length).toBeGreaterThan(0);

    mockExplanation.businessRules.forEach((rule) => {
      expect(['floor', 'ceiling', 'margin', 'competitive', 'promotional']).toContain(
        rule.type
      );
    });
  });

  it('should have consistent optimal price', () => {
    expect(mockExplanation.optimalPrice).toBe(mockExplanation.result.recommendedPrice);
  });

  it('should have positive profit uplift', () => {
    expect(mockExplanation.profitUpliftPercent).toBeGreaterThan(0);
  });
});

describe('Component Rendering', () => {
  it('should render RecommendationCard with pricing data', () => {
    const html = renderToString(
      createElement(RecommendationCard, {
        result: mockExplanation.result,
        profitUpliftPercent: mockExplanation.profitUpliftPercent,
      })
    );

    // Check that key pricing information is rendered
    expect(html).toContain('99.99'); // recommended price
    expect(html).toContain('89.99'); // base price
    expect(html).toContain('15.5'); // profit uplift
    expect(html).toContain('85%'); // confidence score
    expect(html).toContain('value seeker'); // segment
  });

  it('should render FeatureImportanceChart with feature data', () => {
    const html = renderToString(
      createElement(FeatureImportanceChart, {
        data: mockExplanation.featureContributions,
      })
    );

    // Check component renders with chart container
    expect(html).toContain('Feature Importance');
    expect(html).toContain('Increases price'); // legend
    expect(html).toContain('Decreases price'); // legend
  });

  it('should render FeatureImportanceChart empty state', () => {
    const html = renderToString(
      createElement(FeatureImportanceChart, {
        data: [],
      })
    );

    expect(html).toContain('No feature data available');
  });

  it('should render DecisionTrace with step data', () => {
    const html = renderToString(
      createElement(DecisionTrace, {
        steps: mockExplanation.decisionTrace,
      })
    );

    // Check component renders with steps
    expect(html).toContain('Decision Trace');
    expect(html).toContain('Data Loading');
    expect(html).toContain('Model Prediction');
    // React SSR renders numbers with comment delimiters
    expect(html).toMatch(/57.*ms/); // total duration (12 + 45)
  });

  it('should render DecisionTrace empty state', () => {
    const html = renderToString(
      createElement(DecisionTrace, {
        steps: [],
      })
    );

    expect(html).toContain('No decision trace available');
  });

  it('should render BusinessRulesList with rule data', () => {
    const html = renderToString(
      createElement(BusinessRulesList, {
        rules: mockExplanation.businessRules,
      })
    );

    // Check component renders with rules
    expect(html).toContain('Business Rules');
    // React SSR renders numbers with comment delimiters
    expect(html).toMatch(/1.*applied/); // triggered rules count
    expect(html).toContain('Minimum Margin');
    expect(html).toContain('margin'); // rule type
  });

  it('should render BusinessRulesList empty state', () => {
    const html = renderToString(
      createElement(BusinessRulesList, {
        rules: [],
      })
    );

    expect(html).toContain('No business rules configured');
  });

  it('should include aria-labels for accessibility', () => {
    const html = renderToString(
      createElement(DecisionTrace, {
        steps: mockExplanation.decisionTrace,
      })
    );

    // Check aria-label is present on expand buttons
    expect(html).toContain('aria-label');
    expect(html).toContain('aria-expanded');
  });
});

describe('Panel Integration', () => {
  beforeEach(() => {
    // Reset stores
    usePricingStore.getState().clear();
    useLayoutStore.setState({ rightPanelCollapsed: false });
  });

  it('should update panel visibility state correctly', () => {
    const { toggleRightPanel } = useLayoutStore.getState();
    
    // Initially not collapsed
    expect(useLayoutStore.getState().rightPanelCollapsed).toBe(false);
    
    // Toggle to collapsed
    toggleRightPanel();
    expect(useLayoutStore.getState().rightPanelCollapsed).toBe(true);
    
    // Toggle back to expanded
    toggleRightPanel();
    expect(useLayoutStore.getState().rightPanelCollapsed).toBe(false);
  });

  it('should synchronize pricing store with panel visibility', () => {
    const { setExplanation, clear } = usePricingStore.getState();
    const { toggleRightPanel } = useLayoutStore.getState();

    // Set explanation data
    setExplanation(mockExplanation);
    expect(usePricingStore.getState().explanation).not.toBeNull();

    // Panel can be collapsed while data exists
    toggleRightPanel();
    expect(useLayoutStore.getState().rightPanelCollapsed).toBe(true);
    expect(usePricingStore.getState().explanation).not.toBeNull();

    // Clear data doesn't affect panel state
    clear();
    expect(usePricingStore.getState().explanation).toBeNull();
    expect(useLayoutStore.getState().rightPanelCollapsed).toBe(true);
  });

  it('should maintain data integrity during panel toggles', () => {
    const { setExplanation } = usePricingStore.getState();
    const { toggleRightPanel } = useLayoutStore.getState();

    setExplanation(mockExplanation);
    
    // Toggle multiple times
    toggleRightPanel();
    toggleRightPanel();
    toggleRightPanel();

    // Data should remain intact
    const { explanation } = usePricingStore.getState();
    expect(explanation?.result.recommendedPrice).toBe(99.99);
    expect(explanation?.featureContributions.length).toBe(3);
    expect(explanation?.decisionTrace.length).toBe(2);
  });
});

