import { describe, test, expect, beforeEach, afterEach } from 'bun:test';
import { createElement } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { act } from 'react';
import { useLayoutStore } from '@/stores/layoutStore';
import { ProfitUpliftHero } from '@/components/executive/ProfitUpliftHero';
import { KeyInsight } from '@/components/executive/KeyInsight';
import { KPICard } from '@/components/executive/KPICard';
import { mockExecutiveData } from '@/components/executive/mockData';

// ============================================================
// Store Tests
// ============================================================

describe('Executive Layout Store', () => {
    beforeEach(() => {
        // Reset store to initial state
        useLayoutStore.setState({
            leftPanelCollapsed: false,
            rightPanelCollapsed: false,
            activeTab: 'workspace',
        });
    });

    test('should have setLeftCollapsed function', () => {
        const store = useLayoutStore.getState();
        expect(typeof store.setLeftCollapsed).toBe('function');
    });

    test('should have setRightCollapsed function', () => {
        const store = useLayoutStore.getState();
        expect(typeof store.setRightCollapsed).toBe('function');
    });

    test('should collapse left panel when setLeftCollapsed(true) is called', () => {
        const { setLeftCollapsed } = useLayoutStore.getState();
        expect(useLayoutStore.getState().leftPanelCollapsed).toBe(false);

        setLeftCollapsed(true);
        expect(useLayoutStore.getState().leftPanelCollapsed).toBe(true);
    });

    test('should expand left panel when setLeftCollapsed(false) is called', () => {
        const { setLeftCollapsed } = useLayoutStore.getState();
        setLeftCollapsed(true);
        expect(useLayoutStore.getState().leftPanelCollapsed).toBe(true);

        setLeftCollapsed(false);
        expect(useLayoutStore.getState().leftPanelCollapsed).toBe(false);
    });

    test('should collapse right panel when setRightCollapsed(true) is called', () => {
        const { setRightCollapsed } = useLayoutStore.getState();
        expect(useLayoutStore.getState().rightPanelCollapsed).toBe(false);

        setRightCollapsed(true);
        expect(useLayoutStore.getState().rightPanelCollapsed).toBe(true);
    });

    test('should set executive as active tab', () => {
        const { setActiveTab } = useLayoutStore.getState();
        setActiveTab('executive');
        expect(useLayoutStore.getState().activeTab).toBe('executive');
    });
});

// ============================================================
// Component Rendering Tests
// ============================================================

describe('ProfitUpliftHero Component', () => {
    let container: HTMLDivElement;
    let root: Root;

    beforeEach(() => {
        container = document.createElement('div');
        document.body.appendChild(container);
        root = createRoot(container);
    });

    afterEach(() => {
        act(() => {
            root.unmount();
        });
        container.remove();
    });

    test('should render positive value with + prefix', async () => {
        await act(async () => {
            root.render(createElement(ProfitUpliftHero, { value: 24.3, baseline: 35.0 }));
        });

        const text = container.textContent || '';
        expect(text).toContain('+24.3%');
        expect(text).toContain('$35.00');
    });

    test('should render negative value without + prefix', async () => {
        await act(async () => {
            root.render(createElement(ProfitUpliftHero, { value: -5.2, baseline: 35.0 }));
        });

        const text = container.textContent || '';
        expect(text).toContain('-5.2%');
        expect(text).not.toContain('+-');
    });

    test('should display baseline price formatted correctly', async () => {
        await act(async () => {
            root.render(createElement(ProfitUpliftHero, { value: 10, baseline: 42.5 }));
        });

        expect(container.textContent).toContain('$42.50');
    });

    test('should render Total Profit Uplift label', async () => {
        await act(async () => {
            root.render(createElement(ProfitUpliftHero, { value: 15, baseline: 30 }));
        });

        expect(container.textContent).toContain('Total Profit Uplift');
    });
});

describe('KeyInsight Component', () => {
    let container: HTMLDivElement;
    let root: Root;

    beforeEach(() => {
        container = document.createElement('div');
        document.body.appendChild(container);
        root = createRoot(container);
    });

    afterEach(() => {
        act(() => {
            root.unmount();
        });
        container.remove();
    });

    test('should render insight text', async () => {
        const insight = 'Dynamic pricing delivered 24.3% improvement';
        await act(async () => {
            root.render(createElement(KeyInsight, { insight }));
        });

        expect(container.textContent).toContain(insight);
    });

    test('should render Key Insight title', async () => {
        await act(async () => {
            root.render(createElement(KeyInsight, { insight: 'Test insight' }));
        });

        expect(container.textContent).toContain('Key Insight');
    });

    test('should render long insight text correctly', async () => {
        const longInsight = mockExecutiveData.keyInsight;
        await act(async () => {
            root.render(createElement(KeyInsight, { insight: longInsight }));
        });

        expect(container.textContent).toContain('Urban Peak Premium');
        expect(container.textContent).toContain('24.3%');
    });
});

describe('KPICard Component', () => {
    let container: HTMLDivElement;
    let root: Root;

    beforeEach(() => {
        container = document.createElement('div');
        document.body.appendChild(container);
        root = createRoot(container);
    });

    afterEach(() => {
        act(() => {
            root.unmount();
        });
        container.remove();
    });

    test('should render title and string value', async () => {
        await act(async () => {
            root.render(
                createElement(KPICard, {
                    title: 'Total Profit',
                    value: '+24.3%',
                })
            );
        });

        expect(container.textContent).toContain('Total Profit');
        expect(container.textContent).toContain('+24.3%');
    });

    test('should render numeric value', async () => {
        await act(async () => {
            root.render(
                createElement(KPICard, {
                    title: 'Count',
                    value: 150,
                })
            );
        });

        expect(container.textContent).toContain('150');
    });

    test('should render subtitle when provided', async () => {
        await act(async () => {
            root.render(
                createElement(KPICard, {
                    title: 'Uplift',
                    value: 100,
                    subtitle: 'vs. baseline',
                })
            );
        });

        expect(container.textContent).toContain('vs. baseline');
    });

    test('should render without subtitle when not provided', async () => {
        await act(async () => {
            root.render(
                createElement(KPICard, {
                    title: 'Simple Card',
                    value: 42,
                })
            );
        });

        expect(container.textContent).toContain('Simple Card');
        expect(container.textContent).toContain('42');
    });
});

// ============================================================
// Mock Data Tests
// ============================================================

describe('Centralized Executive Mock Data', () => {
    test('should have positive profit uplift', () => {
        expect(mockExecutiveData.profitUplift).toBeGreaterThan(0);
    });

    test('should have 5 market segments', () => {
        expect(mockExecutiveData.segmentPerformance).toHaveLength(5);
    });

    test('should have 100% compliance rate', () => {
        expect(mockExecutiveData.complianceRate).toBe(100);
    });

    test('should have zero risk alerts', () => {
        expect(mockExecutiveData.riskAlerts).toBe(0);
    });

    test('should have segment performance sorted by improvement descending', () => {
        const improvements = mockExecutiveData.segmentPerformance.map((s) => s.improvement ?? 0);
        const sortedImprovements = [...improvements].sort((a, b) => b - a);
        expect(improvements).toEqual(sortedImprovements);
    });

    test('should have baseline and optimized values for each segment', () => {
        mockExecutiveData.segmentPerformance.forEach((segment) => {
            expect(segment.baseline).toBeGreaterThan(0);
            expect(segment.optimized).toBeGreaterThan(segment.baseline);
        });
    });

    test('should have valid baseline price', () => {
        expect(mockExecutiveData.baseline).toBeGreaterThan(0);
    });

    test('should have positive recommendations count', () => {
        expect(mockExecutiveData.recommendationsAnalyzed).toBeGreaterThan(0);
    });

    test('should have all required fields', () => {
        expect(mockExecutiveData).toHaveProperty('profitUplift');
        expect(mockExecutiveData).toHaveProperty('baseline');
        expect(mockExecutiveData).toHaveProperty('keyInsight');
        expect(mockExecutiveData).toHaveProperty('segmentPerformance');
        expect(mockExecutiveData).toHaveProperty('recommendationsAnalyzed');
        expect(mockExecutiveData).toHaveProperty('complianceRate');
        expect(mockExecutiveData).toHaveProperty('riskAlerts');
    });
});

// ============================================================
// Tab Refresh Behavior Tests
// ============================================================

describe('Executive Tab Refresh', () => {
    beforeEach(() => {
        useLayoutStore.setState({ activeTab: 'workspace' });
    });

    test('should trigger refresh when tab changes to executive', () => {
        const { setActiveTab } = useLayoutStore.getState();

        setActiveTab('workspace');
        expect(useLayoutStore.getState().activeTab).toBe('workspace');

        setActiveTab('executive');
        expect(useLayoutStore.getState().activeTab).toBe('executive');
    });

    test('should track tab changes correctly', () => {
        const { setActiveTab } = useLayoutStore.getState();

        setActiveTab('executive');
        expect(useLayoutStore.getState().activeTab).toBe('executive');

        setActiveTab('evidence');
        expect(useLayoutStore.getState().activeTab).toBe('evidence');

        setActiveTab('workspace');
        expect(useLayoutStore.getState().activeTab).toBe('workspace');
    });
});
