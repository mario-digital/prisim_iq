/**
 * Tests for Header, Brand, PipelineStatus, SystemStatus, HoneywellToggle components.
 */
import { describe, test, expect, beforeEach } from 'bun:test';
import { useStatusStore, PIPELINE_STAGES, type HealthStatus } from '@/stores/statusStore';

describe('Status Store', () => {
  beforeEach(() => {
    // Reset store to initial state before each test
    useStatusStore.setState({
      health: 'healthy',
      lastHealthCheck: null,
      currentStage: -1,
      isProcessing: false,
      completedStages: [],
      currentSegment: null,
      modelsReady: 3,
      totalModels: 3,
      lastResponseTime: null,
      honeywellOverlayVisible: false,
    });
  });

  test('should have correct initial state', () => {
    const state = useStatusStore.getState();
    expect(state.health).toBe('healthy');
    expect(state.currentStage).toBe(-1);
    expect(state.isProcessing).toBe(false);
    expect(state.completedStages).toEqual([]);
    expect(state.currentSegment).toBeNull();
    expect(state.modelsReady).toBe(3);
    expect(state.lastResponseTime).toBeNull();
    expect(state.honeywellOverlayVisible).toBe(false);
  });

  test('should set health status', () => {
    const { setHealth } = useStatusStore.getState();
    
    setHealth('degraded');
    expect(useStatusStore.getState().health).toBe('degraded');
    
    setHealth('unhealthy');
    expect(useStatusStore.getState().health).toBe('unhealthy');
    
    setHealth('healthy');
    expect(useStatusStore.getState().health).toBe('healthy');
  });

  test('should set health check with timestamp', () => {
    const { setHealthCheck } = useStatusStore.getState();
    const beforeCheck = new Date();
    
    setHealthCheck('degraded');
    
    const state = useStatusStore.getState();
    expect(state.health).toBe('degraded');
    expect(state.lastHealthCheck).not.toBeNull();
    expect(state.lastHealthCheck!.getTime()).toBeGreaterThanOrEqual(beforeCheck.getTime());
  });

  test('should start processing pipeline', () => {
    const { startProcessing } = useStatusStore.getState();
    
    startProcessing();
    
    const state = useStatusStore.getState();
    expect(state.isProcessing).toBe(true);
    expect(state.currentStage).toBe(0);
    expect(state.completedStages).toEqual([]);
  });

  test('should advance pipeline stages', () => {
    const { startProcessing, advanceStage } = useStatusStore.getState();
    
    startProcessing();
    expect(useStatusStore.getState().currentStage).toBe(0);
    
    advanceStage();
    expect(useStatusStore.getState().currentStage).toBe(1);
    expect(useStatusStore.getState().completedStages).toEqual([0]);
    
    advanceStage();
    expect(useStatusStore.getState().currentStage).toBe(2);
    expect(useStatusStore.getState().completedStages).toEqual([0, 1]);
    
    advanceStage();
    expect(useStatusStore.getState().currentStage).toBe(3);
    expect(useStatusStore.getState().completedStages).toEqual([0, 1, 2]);
  });

  test('should complete processing with response time', () => {
    const { startProcessing, advanceStage, completeProcessing } = useStatusStore.getState();
    
    startProcessing();
    advanceStage();
    advanceStage();
    
    completeProcessing(2.5);
    
    const state = useStatusStore.getState();
    expect(state.isProcessing).toBe(false);
    expect(state.currentStage).toBe(-1);
    expect(state.lastResponseTime).toBe(2.5);
  });

  test('should reset pipeline', () => {
    const { startProcessing, advanceStage, resetPipeline } = useStatusStore.getState();
    
    startProcessing();
    advanceStage();
    
    resetPipeline();
    
    const state = useStatusStore.getState();
    expect(state.isProcessing).toBe(false);
    expect(state.currentStage).toBe(-1);
    expect(state.completedStages).toEqual([]);
  });

  test('should set segment', () => {
    const { setSegment } = useStatusStore.getState();
    
    setSegment('Premium');
    expect(useStatusStore.getState().currentSegment).toBe('Premium');
    
    setSegment(null);
    expect(useStatusStore.getState().currentSegment).toBeNull();
  });

  test('should set models ready count', () => {
    const { setModelsReady } = useStatusStore.getState();
    
    setModelsReady(2, 3);
    
    const state = useStatusStore.getState();
    expect(state.modelsReady).toBe(2);
    expect(state.totalModels).toBe(3);
  });

  test('should toggle Honeywell overlay', () => {
    const { toggleHoneywellOverlay } = useStatusStore.getState();
    
    expect(useStatusStore.getState().honeywellOverlayVisible).toBe(false);
    
    toggleHoneywellOverlay();
    expect(useStatusStore.getState().honeywellOverlayVisible).toBe(true);
    
    toggleHoneywellOverlay();
    expect(useStatusStore.getState().honeywellOverlayVisible).toBe(false);
  });

  test('should set Honeywell overlay directly', () => {
    const { setHoneywellOverlay } = useStatusStore.getState();
    
    setHoneywellOverlay(true);
    expect(useStatusStore.getState().honeywellOverlayVisible).toBe(true);
    
    setHoneywellOverlay(false);
    expect(useStatusStore.getState().honeywellOverlayVisible).toBe(false);
  });
});

describe('Pipeline Stages', () => {
  test('should have correct stage names', () => {
    expect(PIPELINE_STAGES).toEqual(['Context', 'ML', 'Optimize', 'Price']);
    expect(PIPELINE_STAGES.length).toBe(4);
  });

  test('should have stages as readonly array', () => {
    // TypeScript enforces this, but we can verify the values
    expect(PIPELINE_STAGES[0]).toBe('Context');
    expect(PIPELINE_STAGES[1]).toBe('ML');
    expect(PIPELINE_STAGES[2]).toBe('Optimize');
    expect(PIPELINE_STAGES[3]).toBe('Price');
  });
});

describe('Health Status Types', () => {
  test('should accept valid health statuses', () => {
    const validStatuses: HealthStatus[] = ['healthy', 'degraded', 'unhealthy'];
    const { setHealth } = useStatusStore.getState();
    
    validStatuses.forEach((status) => {
      setHealth(status);
      expect(useStatusStore.getState().health).toBe(status);
    });
  });
});

