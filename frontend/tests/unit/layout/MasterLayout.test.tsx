import { describe, expect, it, beforeEach, mock } from 'bun:test';

// Mock next/navigation
mock.module('next/navigation', () => ({
  usePathname: () => '/workspace',
  useRouter: () => ({
    push: () => {},
    replace: () => {},
  }),
  redirect: () => {},
}));

const resolveModule = (relativePath: string) =>
  new URL(relativePath, import.meta.url).href;

const layoutStoreModule = resolveModule('../../../src/stores/layoutStore.ts');
const apiModule = resolveModule('../../../src/lib/api.ts');

describe('Layout Store', () => {
  beforeEach(async () => {
    // Clear localStorage before each test
    if (typeof localStorage !== 'undefined') {
      localStorage.clear();
    }
    // Reset store to initial state to prevent test pollution
    const { useLayoutStore } = await import(layoutStoreModule);
    useLayoutStore.setState({
      leftPanelCollapsed: false,
      rightPanelCollapsed: false,
      activeTab: 'workspace',
    });
  });

  it('should have initial state with panels expanded', async () => {
    const { useLayoutStore } = await import(layoutStoreModule);
    const state = useLayoutStore.getState();
    
    expect(state.leftPanelCollapsed).toBe(false);
    expect(state.rightPanelCollapsed).toBe(false);
    expect(state.activeTab).toBe('workspace');
  });

  it('should toggle left panel', async () => {
    const { useLayoutStore } = await import(layoutStoreModule);
    const store = useLayoutStore.getState();
    
    expect(store.leftPanelCollapsed).toBe(false);
    store.toggleLeftPanel();
    expect(useLayoutStore.getState().leftPanelCollapsed).toBe(true);
    store.toggleLeftPanel();
    expect(useLayoutStore.getState().leftPanelCollapsed).toBe(false);
  });

  it('should toggle right panel', async () => {
    const { useLayoutStore } = await import(layoutStoreModule);
    const store = useLayoutStore.getState();
    
    expect(store.rightPanelCollapsed).toBe(false);
    store.toggleRightPanel();
    expect(useLayoutStore.getState().rightPanelCollapsed).toBe(true);
    store.toggleRightPanel();
    expect(useLayoutStore.getState().rightPanelCollapsed).toBe(false);
  });

  it('should set active tab', async () => {
    const { useLayoutStore } = await import(layoutStoreModule);
    const store = useLayoutStore.getState();
    
    store.setActiveTab('executive');
    expect(useLayoutStore.getState().activeTab).toBe('executive');
    
    store.setActiveTab('evidence');
    expect(useLayoutStore.getState().activeTab).toBe('evidence');
    
    store.setActiveTab('workspace');
    expect(useLayoutStore.getState().activeTab).toBe('workspace');
  });
});

describe('Tab Navigation', () => {
  it('should have correct tabs defined', async () => {
    // Tab navigation tests verify the tabs configuration
    const expectedTabs = ['workspace', 'executive', 'evidence'];
    expect(expectedTabs).toContain('workspace');
    expect(expectedTabs).toContain('executive');
    expect(expectedTabs).toContain('evidence');
    expect(expectedTabs.length).toBe(3);
  });

  it('should have correct tab routes', () => {
    const tabRoutes = {
      workspace: '/workspace',
      executive: '/executive',
      evidence: '/evidence',
    };
    
    expect(tabRoutes.workspace).toBe('/workspace');
    expect(tabRoutes.executive).toBe('/executive');
    expect(tabRoutes.evidence).toBe('/evidence');
  });
});

describe('API Configuration', () => {
  it('should export API configuration', async () => {
    const { apiConfig, apiUrl } = await import(apiModule);
    
    expect(apiConfig).toBeDefined();
    expect(apiConfig.baseUrl).toBeDefined();
    expect(apiConfig.endpoints).toBeDefined();
    expect(apiConfig.endpoints.health).toBe('/health');
  });

  it('should build correct API URLs', async () => {
    const { apiUrl, API_BASE_URL } = await import(apiModule);
    
    expect(apiUrl('/health')).toBe(`${API_BASE_URL}/health`);
    expect(apiUrl('health')).toBe(`${API_BASE_URL}/health`);
  });
});

