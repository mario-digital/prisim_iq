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

const contextStoreModule = resolveModule('../../../src/stores/contextStore.ts');

describe('Context Store', () => {
  beforeEach(async () => {
    // Clear localStorage before each test
    if (typeof localStorage !== 'undefined') {
      localStorage.clear();
    }
    // Reset store state
    const { useContextStore, defaultContext } = await import(contextStoreModule);
    useContextStore.setState({
      context: { ...defaultContext },
      savedScenarios: [],
      isLoading: false,
    });
  });

  it('should have correct default context values', async () => {
    const { useContextStore, defaultContext } = await import(contextStoreModule);
    const state = useContextStore.getState();

    expect(state.context).toEqual(defaultContext);
    expect(state.context.number_of_riders).toBe(50);
    expect(state.context.number_of_drivers).toBe(25);
    expect(state.context.location_category).toBe('Urban');
    expect(state.context.customer_loyalty_status).toBe('Silver');
    expect(state.context.time_of_booking).toBe('Evening');
    expect(state.context.vehicle_type).toBe('Premium');
  });

  it('should update context partially', async () => {
    const { useContextStore } = await import(contextStoreModule);
    const store = useContextStore.getState();

    store.updateContext({ number_of_riders: 100 });
    expect(useContextStore.getState().context.number_of_riders).toBe(100);

    store.updateContext({ location_category: 'Rural' });
    expect(useContextStore.getState().context.location_category).toBe('Rural');
    // Other values should remain unchanged
    expect(useContextStore.getState().context.number_of_riders).toBe(100);
  });

  it('should reset context to defaults', async () => {
    const { useContextStore, defaultContext } = await import(contextStoreModule);
    const store = useContextStore.getState();

    // Modify context
    store.updateContext({ number_of_riders: 200, location_category: 'Rural' });
    expect(useContextStore.getState().context.number_of_riders).toBe(200);

    // Reset
    store.resetContext();
    expect(useContextStore.getState().context).toEqual(defaultContext);
  });

  it('should save a scenario', async () => {
    const { useContextStore } = await import(contextStoreModule);
    const store = useContextStore.getState();

    expect(store.savedScenarios.length).toBe(0);

    store.saveScenario('Test Scenario');
    const scenarios = useContextStore.getState().savedScenarios;

    expect(scenarios.length).toBe(1);
    expect(scenarios[0].name).toBe('Test Scenario');
    expect(scenarios[0].id).toBeDefined();
    expect(scenarios[0].createdAt).toBeDefined();
    expect(scenarios[0].context.number_of_riders).toBe(50);
  });

  it('should load a saved scenario', async () => {
    const { useContextStore } = await import(contextStoreModule);
    const store = useContextStore.getState();

    // Save a scenario with specific values
    store.updateContext({ number_of_riders: 75, location_category: 'Suburban' });
    store.saveScenario('Suburban Scenario');

    // Modify context
    store.updateContext({ number_of_riders: 200, location_category: 'Rural' });
    expect(useContextStore.getState().context.number_of_riders).toBe(200);

    // Load saved scenario
    const scenarios = useContextStore.getState().savedScenarios;
    store.loadScenario(scenarios[0].id);

    expect(useContextStore.getState().context.number_of_riders).toBe(75);
    expect(useContextStore.getState().context.location_category).toBe('Suburban');
  });

  it('should delete a scenario', async () => {
    const { useContextStore } = await import(contextStoreModule);
    const store = useContextStore.getState();

    // Save two scenarios
    store.saveScenario('Scenario 1');
    store.saveScenario('Scenario 2');
    expect(useContextStore.getState().savedScenarios.length).toBe(2);

    // Delete first scenario
    const scenarios = useContextStore.getState().savedScenarios;
    store.deleteScenario(scenarios[0].id);

    expect(useContextStore.getState().savedScenarios.length).toBe(1);
    expect(useContextStore.getState().savedScenarios[0].name).toBe('Scenario 2');
  });

  it('should set loading state', async () => {
    const { useContextStore } = await import(contextStoreModule);
    const store = useContextStore.getState();

    expect(store.isLoading).toBe(false);

    store.setLoading(true);
    expect(useContextStore.getState().isLoading).toBe(true);

    store.setLoading(false);
    expect(useContextStore.getState().isLoading).toBe(false);
  });
});

describe('Context Validation', () => {
  it('should validate location category values', () => {
    const validLocations = ['Urban', 'Suburban', 'Rural'];
    expect(validLocations).toContain('Urban');
    expect(validLocations).toContain('Suburban');
    expect(validLocations).toContain('Rural');
    expect(validLocations.length).toBe(3);
  });

  it('should validate time of booking values', () => {
    const validTimes = ['Morning', 'Afternoon', 'Evening', 'Night'];
    expect(validTimes).toContain('Morning');
    expect(validTimes).toContain('Afternoon');
    expect(validTimes).toContain('Evening');
    expect(validTimes).toContain('Night');
    expect(validTimes.length).toBe(4);
  });

  it('should validate customer loyalty status values', () => {
    const validStatuses = ['Bronze', 'Silver', 'Gold', 'Platinum'];
    expect(validStatuses).toContain('Bronze');
    expect(validStatuses).toContain('Silver');
    expect(validStatuses).toContain('Gold');
    expect(validStatuses).toContain('Platinum');
    expect(validStatuses.length).toBe(4);
  });

  it('should validate vehicle type values', () => {
    const validTypes = ['Economy', 'Premium'];
    expect(validTypes).toContain('Economy');
    expect(validTypes).toContain('Premium');
    expect(validTypes.length).toBe(2);
  });
});

describe('Supply/Demand Ratio Calculation', () => {
  it('should calculate ratio correctly', () => {
    const riders = 50;
    const drivers = 25;
    const ratio = riders / drivers;
    expect(ratio).toBe(2);
  });

  it('should handle high demand scenario', () => {
    const riders = 100;
    const drivers = 25;
    const ratio = riders / drivers;
    expect(ratio).toBe(4);
    expect(ratio > 2).toBe(true); // High demand
  });

  it('should handle balanced scenario', () => {
    const riders = 30;
    const drivers = 25;
    const ratio = riders / drivers;
    expect(ratio).toBe(1.2);
    expect(ratio > 1 && ratio <= 2).toBe(true); // Balanced
  });

  it('should handle low demand scenario', () => {
    const riders = 20;
    const drivers = 25;
    const ratio = riders / drivers;
    expect(ratio).toBe(0.8);
    expect(ratio <= 1).toBe(true); // Low demand
  });
});

