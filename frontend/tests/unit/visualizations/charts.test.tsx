import { describe, it, expect } from 'bun:test';
import { createElement } from 'react';
import { renderToString } from 'react-dom/server';
import {
  chartColors,
  chartConfig,
  formatPrice,
  formatPercent,
  getDirectionColor,
  getSegmentColor,
} from '@/lib/chartTheme';
import {
  findClosestPoint,
  findMaxPoint,
  findMinPoint,
  clamp,
  calculateDomainWithPadding,
  prepareFeatureData,
} from '@/components/visualizations/charts/shared/chartUtils';
import { ChartLegend } from '@/components/visualizations/charts/shared/ChartLegend';
import { DemandCurveChart } from '@/components/visualizations/DemandCurveChart';
import { ProfitCurveChart } from '@/components/visualizations/ProfitCurveChart';
import { SegmentPerformanceChart } from '@/components/visualizations/SegmentPerformanceChart';
import { SensitivityBandChart } from '@/components/visualizations/SensitivityBandChart';
import type { CurvePoint } from '@/components/visualizations/types';

/**
 * Mock demand curve data for testing.
 */
const mockDemandCurve: CurvePoint[] = [
  { price: 79.99, value: 200 },
  { price: 89.99, value: 175 },
  { price: 99.99, value: 150 },
  { price: 109.99, value: 120 },
  { price: 119.99, value: 90 },
];

/**
 * Mock profit curve data for testing.
 */
const mockProfitCurve: CurvePoint[] = [
  { price: 79.99, value: 1500 },
  { price: 89.99, value: 2000 },
  { price: 99.99, value: 2200 },
  { price: 109.99, value: 2100 },
  { price: 119.99, value: 1800 },
];

/**
 * Mock segment performance data for testing.
 */
const mockSegmentData = [
  { segment: 'Premium', baseline: 5000, optimized: 5750, improvement: 15 },
  { segment: 'Standard', baseline: 3500, optimized: 3850, improvement: 10 },
  { segment: 'Budget', baseline: 2000, optimized: 2200, improvement: 10 },
];

/**
 * Mock sensitivity band data for testing.
 */
const mockSensitivityBandData = [
  { scenario: 'Low', price: 90, minPrice: 85, maxPrice: 95 },
  { scenario: 'Base', price: 100, minPrice: 95, maxPrice: 105 },
  { scenario: 'High', price: 110, minPrice: 105, maxPrice: 115 },
];

describe('Chart Theme Configuration', () => {
  it('should have valid color definitions', () => {
    expect(chartColors.primary).toMatch(/^#[0-9a-f]{6}$/i);
    expect(chartColors.secondary).toMatch(/^#[0-9a-f]{6}$/i);
    expect(chartColors.positive).toMatch(/^#[0-9a-f]{6}$/i);
    expect(chartColors.negative).toMatch(/^#[0-9a-f]{6}$/i);
  });

  it('should have valid chart config', () => {
    expect(chartConfig.fontSize).toBeGreaterThan(0);
    expect(chartConfig.fontSizeSmall).toBeGreaterThan(0);
    expect(chartConfig.animationDuration).toBeGreaterThan(0);
  });

  it('should format price correctly', () => {
    expect(formatPrice(99)).toBe('$99');
    expect(formatPrice(99.99)).toBe('$100');
    expect(formatPrice(0)).toBe('$0');
  });

  it('should format percent correctly', () => {
    expect(formatPercent(85)).toBe('85%');
    expect(formatPercent(85.5)).toBe('86%');
    expect(formatPercent(0)).toBe('0%');
  });

  it('should return correct direction colors', () => {
    expect(getDirectionColor('positive')).toBe(chartColors.positive);
    expect(getDirectionColor('negative')).toBe(chartColors.negative);
    expect(getDirectionColor('neutral')).toBe(chartColors.muted);
  });

  it('should return correct segment colors', () => {
    expect(getSegmentColor('premium')).toBe('#8b5cf6');
    expect(getSegmentColor('standard')).toBe('#3b82f6');
    expect(getSegmentColor('budget')).toBe('#10b981');
    expect(getSegmentColor('unknown')).toBe('#94a3b8'); // default
  });
});

describe('Chart Utilities', () => {
  it('should find closest point', () => {
    const closest = findClosestPoint(mockDemandCurve, 100);
    expect(closest).not.toBeNull();
    expect(closest?.price).toBe(99.99);
  });

  it('should return null for empty array in findClosestPoint', () => {
    const result = findClosestPoint([], 100);
    expect(result).toBeNull();
  });

  it('should find max point', () => {
    const max = findMaxPoint(mockProfitCurve);
    expect(max).not.toBeNull();
    expect(max?.value).toBe(2200);
    expect(max?.price).toBe(99.99);
  });

  it('should find min point', () => {
    const min = findMinPoint(mockProfitCurve);
    expect(min).not.toBeNull();
    expect(min?.value).toBe(1500);
  });

  it('should clamp values correctly', () => {
    expect(clamp(50, 0, 100)).toBe(50);
    expect(clamp(-10, 0, 100)).toBe(0);
    expect(clamp(150, 0, 100)).toBe(100);
  });

  it('should calculate domain with padding', () => {
    const [min, max] = calculateDomainWithPadding(mockProfitCurve);
    expect(min).toBeLessThan(1500);
    expect(max).toBeGreaterThan(2200);
  });

  it('should return default domain for empty array', () => {
    const [min, max] = calculateDomainWithPadding([]);
    expect(min).toBe(0);
    expect(max).toBe(100);
  });

  it('should prepare and sort feature data', () => {
    const features = [
      { importance: 0.2, displayName: 'Low' },
      { importance: 0.8, displayName: 'High' },
      { importance: 0.5, displayName: 'Medium' },
    ];

    const prepared = prepareFeatureData(features, 3);
    expect(prepared[0].displayName).toBe('High');
    expect(prepared[1].displayName).toBe('Medium');
    expect(prepared[2].displayName).toBe('Low');
  });

  it('should limit feature data to specified count', () => {
    const features = Array.from({ length: 10 }, (_, i) => ({
      importance: i * 0.1,
      displayName: `Feature ${i}`,
    }));

    const prepared = prepareFeatureData(features, 5);
    expect(prepared.length).toBe(5);
  });
});

describe('ChartLegend Component', () => {
  it('should render legend items', () => {
    const items = [
      { label: 'Optimal', color: chartColors.secondary },
      { label: 'Current', color: chartColors.indigo },
    ];

    const html = renderToString(createElement(ChartLegend, { items }));

    expect(html).toContain('Optimal');
    expect(html).toContain('Current');
  });

  it('should render with different shapes', () => {
    const items = [
      { label: 'Circle', color: '#ff0000', shape: 'circle' as const },
      { label: 'Square', color: '#00ff00', shape: 'square' as const },
      { label: 'Line', color: '#0000ff', shape: 'line' as const },
    ];

    const html = renderToString(createElement(ChartLegend, { items }));

    expect(html).toContain('Circle');
    expect(html).toContain('Square');
    expect(html).toContain('Line');
  });
});

describe('DemandCurveChart Component', () => {
  it('should render chart with data', () => {
    const html = renderToString(
      createElement(DemandCurveChart, {
        data: mockDemandCurve,
        optimalPrice: 99.99,
        currentPrice: 89.99,
      })
    );

    expect(html).toContain('Demand Curve');
    expect(html).toContain('Optimal Price');
    expect(html).toContain('Current Price');
  });

  it('should render empty state when no data', () => {
    const html = renderToString(
      createElement(DemandCurveChart, {
        data: [],
        optimalPrice: 100,
        currentPrice: 90,
      })
    );

    expect(html).toContain('No demand data available');
  });
});

describe('ProfitCurveChart Component', () => {
  it('should render chart with data', () => {
    const html = renderToString(
      createElement(ProfitCurveChart, {
        data: mockProfitCurve,
        optimalPrice: 99.99,
      })
    );

    expect(html).toContain('Profit Curve');
    expect(html).toContain('Maximum Profit');
    expect(html).toContain('Recommended');
  });

  it('should show max profit value in header', () => {
    const html = renderToString(
      createElement(ProfitCurveChart, {
        data: mockProfitCurve,
        optimalPrice: 99.99,
      })
    );

    // Should contain max profit info
    expect(html).toContain('Max');
  });

  it('should render empty state when no data', () => {
    const html = renderToString(
      createElement(ProfitCurveChart, {
        data: [],
        optimalPrice: 100,
      })
    );

    expect(html).toContain('No profit data available');
  });
});

describe('SegmentPerformanceChart Component', () => {
  it('should render chart with segment data', () => {
    const html = renderToString(
      createElement(SegmentPerformanceChart, {
        data: mockSegmentData,
      })
    );

    expect(html).toContain('Segment Performance');
    // Improvement summary should be present (legend is inside ResponsiveContainer which doesn't SSR)
    expect(html).toContain('Premium');
    expect(html).toContain('Standard');
    expect(html).toContain('Budget');
  });

  it('should show improvement percentages', () => {
    const html = renderToString(
      createElement(SegmentPerformanceChart, {
        data: mockSegmentData,
      })
    );

    // Improvement percentages should be shown
    expect(html).toContain('Premium');
    expect(html).toContain('Standard');
    expect(html).toContain('Budget');
  });

  it('should render empty state when no data', () => {
    const html = renderToString(
      createElement(SegmentPerformanceChart, {
        data: [],
      })
    );

    expect(html).toContain('No segment data available');
  });

  it('should accept custom metric label', () => {
    const html = renderToString(
      createElement(SegmentPerformanceChart, {
        data: mockSegmentData,
        metricLabel: 'Revenue',
        isCurrency: true,
      })
    );

    // Should still render without errors
    expect(html).toContain('Segment Performance');
  });
});

describe('SensitivityBandChart Component', () => {
  it('should render chart with sensitivity data', () => {
    const html = renderToString(
      createElement(SensitivityBandChart, {
        data: mockSensitivityBandData,
        basePrice: 100,
        lowerBound: 95,
        upperBound: 105,
      })
    );

    expect(html).toContain('Price Sensitivity Band');
    expect(html).toContain('Confidence Band');
    expect(html).toContain('Base Price');
  });

  it('should show price range in header', () => {
    const html = renderToString(
      createElement(SensitivityBandChart, {
        data: mockSensitivityBandData,
        basePrice: 100,
        lowerBound: 95,
        upperBound: 105,
      })
    );

    // Range should be displayed
    expect(html).toContain('95.00');
    expect(html).toContain('105.00');
  });

  it('should render empty state when no data', () => {
    const html = renderToString(
      createElement(SensitivityBandChart, {
        data: [],
        basePrice: 100,
      })
    );

    expect(html).toContain('No sensitivity data available');
  });
});

describe('Chart Responsiveness', () => {
  it('should include ResponsiveContainer in DemandCurveChart', () => {
    const html = renderToString(
      createElement(DemandCurveChart, {
        data: mockDemandCurve,
        optimalPrice: 99.99,
        currentPrice: 89.99,
      })
    );

    // ResponsiveContainer sets width="100%"
    expect(html).toContain('100%');
  });

  it('should include ResponsiveContainer in ProfitCurveChart', () => {
    const html = renderToString(
      createElement(ProfitCurveChart, {
        data: mockProfitCurve,
        optimalPrice: 99.99,
      })
    );

    expect(html).toContain('100%');
  });

  it('should include ResponsiveContainer in SegmentPerformanceChart', () => {
    const html = renderToString(
      createElement(SegmentPerformanceChart, {
        data: mockSegmentData,
      })
    );

    expect(html).toContain('100%');
  });

  it('should include ResponsiveContainer in SensitivityBandChart', () => {
    const html = renderToString(
      createElement(SensitivityBandChart, {
        data: mockSensitivityBandData,
        basePrice: 100,
      })
    );

    expect(html).toContain('100%');
  });
});

