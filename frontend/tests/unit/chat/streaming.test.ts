import { describe, it, expect, beforeEach, mock, afterEach } from 'bun:test';
import { useChatStore } from '@/stores/chatStore';

// Helper to create a mock SSE stream
const encoder = new TextEncoder();

function makeSSEStream(chunks: string[]): ReadableStream<Uint8Array> {
  let index = 0;
  return new ReadableStream<Uint8Array>({
    pull(controller) {
      if (index < chunks.length) {
        controller.enqueue(encoder.encode(chunks[index]));
        index++;
      } else {
        controller.close();
      }
    },
  });
}

// Mock fetch for SSE tests
function mockFetchSSE(frames: string[]) {
  return mock(() =>
    Promise.resolve({
      ok: true,
      status: 200,
      statusText: 'OK',
      body: makeSSEStream(frames),
    } as unknown as Response)
  );
}

describe('Chat Store Streaming State', () => {
  beforeEach(() => {
    // Reset store state before each test
    useChatStore.getState().clearChat();
    useChatStore.setState({
      isLoading: false,
      streamingContent: null,
      currentToolCall: null,
      streamError: null,
    });
  });

  it('should start streaming mode correctly', () => {
    const { startStreaming } = useChatStore.getState();

    startStreaming();

    const state = useChatStore.getState();
    expect(state.isLoading).toBe(true);
    expect(state.streamingContent).toBe('');
    expect(state.currentToolCall).toBe(null);
    expect(state.streamError).toBe(null);
  });

  it('should append tokens to streaming content', () => {
    const { startStreaming, appendToken } = useChatStore.getState();

    startStreaming();
    appendToken('Hello ');
    appendToken('world!');

    const { streamingContent } = useChatStore.getState();
    expect(streamingContent).toBe('Hello world!');
  });

  it('should set current tool call', () => {
    const { startStreaming, setToolCall } = useChatStore.getState();

    startStreaming();
    setToolCall('optimize_price');

    expect(useChatStore.getState().currentToolCall).toBe('optimize_price');

    setToolCall(null);
    expect(useChatStore.getState().currentToolCall).toBe(null);
  });

  it('should finalize stream and add message', () => {
    const { startStreaming, appendToken, finalizeStream } = useChatStore.getState();

    startStreaming();
    appendToken('The optimal price is $24.50');

    finalizeStream({
      role: 'assistant',
      content: 'The optimal price is $24.50',
      confidence: 0.95,
      toolsUsed: ['optimize_price'],
    });

    const state = useChatStore.getState();
    expect(state.streamingContent).toBe(null);
    expect(state.currentToolCall).toBe(null);
    expect(state.isLoading).toBe(false);
    expect(state.messages).toHaveLength(1);
    expect(state.messages[0].content).toBe('The optimal price is $24.50');
    expect(state.messages[0].confidence).toBe(0.95);
    expect(state.messages[0].toolsUsed).toEqual(['optimize_price']);
  });

  it('should handle stream error', () => {
    const { startStreaming, setStreamError } = useChatStore.getState();

    startStreaming();
    setStreamError('Connection lost');

    const state = useChatStore.getState();
    expect(state.streamError).toBe('Connection lost');
    expect(state.isLoading).toBe(false);
  });

  it('should cancel stream and reset state', () => {
    const { startStreaming, appendToken, setToolCall, cancelStream } = useChatStore.getState();

    startStreaming();
    appendToken('Partial content');
    setToolCall('explain_decision');

    cancelStream();

    const state = useChatStore.getState();
    expect(state.streamingContent).toBe(null);
    expect(state.currentToolCall).toBe(null);
    expect(state.isLoading).toBe(false);
  });

  it('should clear chat including streaming state', () => {
    const { startStreaming, appendToken, setStreamError, clearChat } =
      useChatStore.getState();

    startStreaming();
    appendToken('Test content');
    setStreamError('Test error');

    clearChat();

    const state = useChatStore.getState();
    expect(state.messages).toHaveLength(0);
    expect(state.streamingContent).toBe(null);
    expect(state.currentToolCall).toBe(null);
    expect(state.streamError).toBe(null);
  });
});

describe('SSE Parsing', () => {
  let originalFetch: typeof global.fetch;

  beforeEach(() => {
    originalFetch = global.fetch;
  });

  afterEach(() => {
    global.fetch = originalFetch;
  });

  it('should parse token events correctly', async () => {
    const frames = [
      'data: {"token": "Hello ", "done": false}\n\n',
      'data: {"token": "world!", "done": false}\n\n',
      'data: {"message": "Hello world!", "done": true}\n\n',
    ];

    global.fetch = mockFetchSSE(frames);

    // Import dynamically to use mocked fetch
    const { streamMessage } = await import('@/services/chatService');

    const events: Array<Record<string, unknown>> = [];
    for await (const evt of streamMessage('test', {
      number_of_riders: 50,
      number_of_drivers: 25,
      location_category: 'Urban',
      customer_loyalty_status: 'Gold',
      number_of_past_rides: 20,
      average_ratings: 4.5,
      time_of_booking: 'Evening',
      vehicle_type: 'Premium',
      expected_ride_duration: 30,
      historical_cost_of_ride: 35.0,
    })) {
      events.push(evt as Record<string, unknown>);
    }

    expect(events.some((e) => e.token === 'Hello ')).toBe(true);
    expect(events.some((e) => e.token === 'world!')).toBe(true);

    const lastEvent = events.at(-1);
    expect(lastEvent?.done).toBe(true);
    expect(lastEvent?.message).toBe('Hello world!');
  });

  it('should handle tool_call events', async () => {
    const frames = [
      'data: {"tool_call": "optimize_price", "done": false}\n\n',
      'data: {"token": "The price is ", "done": false}\n\n',
      'data: {"message": "The price is $24.50", "tools_used": ["optimize_price"], "done": true}\n\n',
    ];

    global.fetch = mockFetchSSE(frames);

    const { streamMessage } = await import('@/services/chatService');

    const events: Array<Record<string, unknown>> = [];
    for await (const evt of streamMessage('test', {
      number_of_riders: 50,
      number_of_drivers: 25,
      location_category: 'Urban',
      customer_loyalty_status: 'Gold',
      number_of_past_rides: 20,
      average_ratings: 4.5,
      time_of_booking: 'Evening',
      vehicle_type: 'Premium',
      expected_ride_duration: 30,
      historical_cost_of_ride: 35.0,
    })) {
      events.push(evt as Record<string, unknown>);
    }

    expect(events.some((e) => e.tool_call === 'optimize_price')).toBe(true);

    const lastEvent = events.at(-1);
    expect(lastEvent?.tools_used).toEqual(['optimize_price']);
  });

  it('should ignore keepalive comment lines', async () => {
    const frames = [
      'data: {"token": "Start ", "done": false}\n\n',
      ': keepalive\n\n',
      'data: {"token": "end", "done": false}\n\n',
      'data: {"message": "Start end", "done": true}\n\n',
    ];

    global.fetch = mockFetchSSE(frames);

    const { streamMessage } = await import('@/services/chatService');

    const events: Array<Record<string, unknown>> = [];
    for await (const evt of streamMessage('test', {
      number_of_riders: 50,
      number_of_drivers: 25,
      location_category: 'Urban',
      customer_loyalty_status: 'Gold',
      number_of_past_rides: 20,
      average_ratings: 4.5,
      time_of_booking: 'Evening',
      vehicle_type: 'Premium',
      expected_ride_duration: 30,
      historical_cost_of_ride: 35.0,
    })) {
      events.push(evt as Record<string, unknown>);
    }

    // Should not contain any keepalive events
    expect(events.every((e) => Object.keys(e).length > 0)).toBe(true);
    expect(events).toHaveLength(3); // 2 tokens + 1 final
  });

  it('should ignore empty keepalive payloads', async () => {
    const frames = [
      'data: {"token": "Hello", "done": false}\n\n',
      'data: {}\n\n', // Empty keepalive
      'data: {"message": "Hello", "done": true}\n\n',
    ];

    global.fetch = mockFetchSSE(frames);

    const { streamMessage } = await import('@/services/chatService');

    const events: Array<Record<string, unknown>> = [];
    for await (const evt of streamMessage('test', {
      number_of_riders: 50,
      number_of_drivers: 25,
      location_category: 'Urban',
      customer_loyalty_status: 'Gold',
      number_of_past_rides: 20,
      average_ratings: 4.5,
      time_of_booking: 'Evening',
      vehicle_type: 'Premium',
      expected_ride_duration: 30,
      historical_cost_of_ride: 35.0,
    })) {
      events.push(evt as Record<string, unknown>);
    }

    // Should not include empty object
    expect(events).toHaveLength(2); // token + final
    expect(events.every((e) => Object.keys(e).length > 0)).toBe(true);
  });

  it('should handle error events', async () => {
    const frames = ['data: {"error": "Model unavailable", "done": true}\n\n'];

    global.fetch = mockFetchSSE(frames);

    const { streamMessage } = await import('@/services/chatService');

    const events: Array<Record<string, unknown>> = [];
    for await (const evt of streamMessage('test', {
      number_of_riders: 50,
      number_of_drivers: 25,
      location_category: 'Urban',
      customer_loyalty_status: 'Gold',
      number_of_past_rides: 20,
      average_ratings: 4.5,
      time_of_booking: 'Evening',
      vehicle_type: 'Premium',
      expected_ride_duration: 30,
      historical_cost_of_ride: 35.0,
    })) {
      events.push(evt as Record<string, unknown>);
    }

    expect(events).toHaveLength(1);
    expect(events[0].error).toBe('Model unavailable');
    expect(events[0].done).toBe(true);
  });

  it('should handle [DONE] marker', async () => {
    const frames = [
      'data: {"token": "Test", "done": false}\n\n',
      'data: [DONE]\n\n',
    ];

    global.fetch = mockFetchSSE(frames);

    const { streamMessage } = await import('@/services/chatService');

    const events: Array<Record<string, unknown>> = [];
    for await (const evt of streamMessage('test', {
      number_of_riders: 50,
      number_of_drivers: 25,
      location_category: 'Urban',
      customer_loyalty_status: 'Gold',
      number_of_past_rides: 20,
      average_ratings: 4.5,
      time_of_booking: 'Evening',
      vehicle_type: 'Premium',
      expected_ride_duration: 30,
      historical_cost_of_ride: 35.0,
    })) {
      events.push(evt as Record<string, unknown>);
    }

    // Should stop at [DONE]
    expect(events).toHaveLength(1);
    expect(events[0].token).toBe('Test');
  });
});

describe('SSE Error Handling', () => {
  let originalFetch: typeof global.fetch;

  beforeEach(() => {
    originalFetch = global.fetch;
  });

  afterEach(() => {
    global.fetch = originalFetch;
  });

  it('should throw on non-OK response', async () => {
    global.fetch = mock(() =>
      Promise.resolve({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        body: null,
      } as Response)
    );

    const { streamMessage } = await import('@/services/chatService');

    let error: Error | null = null;
    try {
      for await (const _ of streamMessage('test', {
        number_of_riders: 50,
        number_of_drivers: 25,
        location_category: 'Urban',
        customer_loyalty_status: 'Gold',
        number_of_past_rides: 20,
        average_ratings: 4.5,
        time_of_booking: 'Evening',
        vehicle_type: 'Premium',
        expected_ride_duration: 30,
        historical_cost_of_ride: 35.0,
      })) {
        // Should not get here
      }
    } catch (e) {
      error = e as Error;
    }

    expect(error).not.toBe(null);
    expect(error?.message).toContain('500');
  });

  it('should throw on missing response body', async () => {
    global.fetch = mock(() =>
      Promise.resolve({
        ok: true,
        status: 200,
        statusText: 'OK',
        body: null,
      } as unknown as Response)
    );

    const { streamMessage } = await import('@/services/chatService');

    let error: Error | null = null;
    try {
      for await (const _ of streamMessage('test', {
        number_of_riders: 50,
        number_of_drivers: 25,
        location_category: 'Urban',
        customer_loyalty_status: 'Gold',
        number_of_past_rides: 20,
        average_ratings: 4.5,
        time_of_booking: 'Evening',
        vehicle_type: 'Premium',
        expected_ride_duration: 30,
        historical_cost_of_ride: 35.0,
      })) {
        // Should not get here
      }
    } catch (e) {
      error = e as Error;
    }

    expect(error).not.toBe(null);
    expect(error?.message).toContain('No response body');
  });
});


