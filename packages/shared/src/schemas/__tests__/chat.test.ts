import { describe, it, expect } from 'bun:test';
import { ChatRequestSchema, ChatResponseSchema, ChatStreamEventSchema } from '../chat';

describe('ChatRequestSchema', () => {
    const validContext = {
        number_of_riders: 50,
        number_of_drivers: 25,
        location_category: 'Urban',
        customer_loyalty_status: 'Gold',
        number_of_past_rides: 10,
        average_ratings: 4.5,
        time_of_booking: 'Evening',
        vehicle_type: 'Premium',
        expected_ride_duration: 30,
        historical_cost_of_ride: 35.0,
    };

    it('validates correct input', () => {
        const request = {
            message: 'What is the optimal price?',
            context: validContext,
        };
        expect(() => ChatRequestSchema.parse(request)).not.toThrow();
    });

    it('accepts optional session_id', () => {
        const request = {
            message: 'What is the optimal price?',
            context: validContext,
            session_id: 'session-123',
        };
        const result = ChatRequestSchema.parse(request);
        expect(result.session_id).toBe('session-123');
    });

    it('accepts null session_id', () => {
        const request = {
            message: 'What is the optimal price?',
            context: validContext,
            session_id: null,
        };
        expect(() => ChatRequestSchema.parse(request)).not.toThrow();
    });

    it('rejects empty message', () => {
        const request = {
            message: '',
            context: validContext,
        };
        expect(() => ChatRequestSchema.parse(request)).toThrow();
    });

    it('rejects message > 4000 chars', () => {
        const request = {
            message: 'a'.repeat(4001),
            context: validContext,
        };
        expect(() => ChatRequestSchema.parse(request)).toThrow();
    });

    it('accepts message at max length (4000 chars)', () => {
        const request = {
            message: 'a'.repeat(4000),
            context: validContext,
        };
        expect(() => ChatRequestSchema.parse(request)).not.toThrow();
    });

    it('validates nested context', () => {
        const request = {
            message: 'Test',
            context: { ...validContext, number_of_riders: 200 }, // Invalid
        };
        expect(() => ChatRequestSchema.parse(request)).toThrow();
    });
});

describe('ChatResponseSchema', () => {
    it('validates correct input', () => {
        const response = {
            message: 'The optimal price is $42.50',
            tools_used: ['optimize_price'],
            context: { number_of_riders: 50 },
            timestamp: '2024-12-02T10:30:00Z',
        };
        expect(() => ChatResponseSchema.parse(response)).not.toThrow();
    });

    it('defaults tools_used to empty array', () => {
        const response = {
            message: 'The optimal price is $42.50',
            context: {},
            timestamp: '2024-12-02T10:30:00Z',
        };
        const parsed = ChatResponseSchema.parse(response);
        expect(parsed.tools_used).toEqual([]);
    });

    it('accepts optional processing_time_ms', () => {
        const response = {
            message: 'The optimal price is $42.50',
            context: {},
            timestamp: '2024-12-02T10:30:00Z',
            processing_time_ms: 1250.5,
        };
        const result = ChatResponseSchema.parse(response);
        expect(result.processing_time_ms).toBe(1250.5);
    });

    it('accepts optional error', () => {
        const response = {
            message: '',
            context: {},
            timestamp: '2024-12-02T10:30:00Z',
            error: 'Rate limit exceeded',
        };
        expect(() => ChatResponseSchema.parse(response)).not.toThrow();
    });

    it('rejects invalid timestamp format', () => {
        const response = {
            message: 'Test',
            context: {},
            timestamp: 'invalid-date',
        };
        expect(() => ChatResponseSchema.parse(response)).toThrow();
    });
});

describe('ChatStreamEventSchema', () => {
    it('validates token event', () => {
        const event = { token: 'The ', done: false };
        expect(() => ChatStreamEventSchema.parse(event)).not.toThrow();
    });

    it('validates tool_call event', () => {
        const event = { tool_call: 'optimize_price', done: false };
        expect(() => ChatStreamEventSchema.parse(event)).not.toThrow();
    });

    it('validates completion event', () => {
        const event = {
            message: 'The optimal price is $42.50',
            tools_used: ['optimize_price'],
            done: true,
        };
        expect(() => ChatStreamEventSchema.parse(event)).not.toThrow();
    });

    it('validates error event', () => {
        const event = { error: 'Rate limit exceeded', done: true };
        expect(() => ChatStreamEventSchema.parse(event)).not.toThrow();
    });

    it('defaults done to false', () => {
        const event = { token: 'Test' };
        const parsed = ChatStreamEventSchema.parse(event);
        expect(parsed.done).toBe(false);
    });

    it('accepts empty event (for heartbeat)', () => {
        const event = { done: false };
        expect(() => ChatStreamEventSchema.parse(event)).not.toThrow();
    });
});

