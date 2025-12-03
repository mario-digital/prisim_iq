/**
 * Tests for Footer component behavior via statusStore.
 */
import { describe, test, expect, beforeEach } from 'bun:test';
import { useStatusStore } from '@/stores/statusStore';

describe('Footer Store Integration', () => {
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

  test('should display initial segment as null', () => {
    const { currentSegment } = useStatusStore.getState();
    expect(currentSegment).toBeNull();
  });

  test('should update segment after recommendation', () => {
    const { setSegment } = useStatusStore.getState();
    
    setSegment('Budget-Conscious');
    expect(useStatusStore.getState().currentSegment).toBe('Budget-Conscious');
  });

  test('should display initial models as 3/3 ready', () => {
    const { modelsReady, totalModels } = useStatusStore.getState();
    expect(modelsReady).toBe(3);
    expect(totalModels).toBe(3);
  });

  test('should update models status when degraded', () => {
    const { setModelsReady } = useStatusStore.getState();
    
    setModelsReady(2, 3);
    
    const state = useStatusStore.getState();
    expect(state.modelsReady).toBe(2);
    expect(state.totalModels).toBe(3);
  });

  test('should display initial response time as null', () => {
    const { lastResponseTime } = useStatusStore.getState();
    expect(lastResponseTime).toBeNull();
  });

  test('should update response time after processing completes', () => {
    const { startProcessing, completeProcessing } = useStatusStore.getState();
    
    startProcessing();
    completeProcessing(2.3);
    
    expect(useStatusStore.getState().lastResponseTime).toBe(2.3);
  });

  test('should handle sub-second response times', () => {
    const { startProcessing, completeProcessing } = useStatusStore.getState();
    
    startProcessing();
    completeProcessing(0.5);
    
    expect(useStatusStore.getState().lastResponseTime).toBe(0.5);
  });

  test('should handle long response times', () => {
    const { startProcessing, completeProcessing } = useStatusStore.getState();
    
    startProcessing();
    completeProcessing(15.7);
    
    expect(useStatusStore.getState().lastResponseTime).toBe(15.7);
  });

  test('should update all footer stats together during flow', () => {
    const { setSegment, setModelsReady, startProcessing, completeProcessing } = useStatusStore.getState();
    
    // Simulate a full recommendation flow
    setSegment('Premium');
    setModelsReady(3, 3);
    startProcessing();
    completeProcessing(1.8);
    
    const state = useStatusStore.getState();
    expect(state.currentSegment).toBe('Premium');
    expect(state.modelsReady).toBe(3);
    expect(state.totalModels).toBe(3);
    expect(state.lastResponseTime).toBe(1.8);
  });
});

describe('Footer Segment Display Scenarios', () => {
  beforeEach(() => {
    useStatusStore.setState({
      currentSegment: null,
      modelsReady: 3,
      totalModels: 3,
      lastResponseTime: null,
    });
  });

  test('should handle various segment names', () => {
    const { setSegment } = useStatusStore.getState();
    const segments = [
      'Budget-Conscious',
      'Premium',
      'Value-Seekers',
      'Enterprise',
      'Small Business',
    ];

    segments.forEach((segment) => {
      setSegment(segment);
      expect(useStatusStore.getState().currentSegment).toBe(segment);
    });
  });

  test('should clear segment when set to null', () => {
    const { setSegment } = useStatusStore.getState();
    
    setSegment('Premium');
    expect(useStatusStore.getState().currentSegment).toBe('Premium');
    
    setSegment(null);
    expect(useStatusStore.getState().currentSegment).toBeNull();
  });
});

