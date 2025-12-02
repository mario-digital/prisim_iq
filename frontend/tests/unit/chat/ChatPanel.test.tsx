import { describe, it, expect, beforeEach, mock } from 'bun:test';
import { useChatStore } from '@/stores/chatStore';

// Mock the chat service
mock.module('@/services/chatService', () => ({
  sendMessage: mock(() =>
    Promise.resolve({
      message: 'Test AI response',
      confidence: 0.85,
    })
  ),
}));

describe('Chat Store', () => {
  beforeEach(() => {
    // Reset store state before each test
    useChatStore.getState().clearChat();
    useChatStore.setState({ isLoading: false });
  });

  it('should start with empty messages', () => {
    const { messages } = useChatStore.getState();
    expect(messages).toEqual([]);
  });

  it('should add a user message', () => {
    const { addMessage } = useChatStore.getState();
    
    addMessage({ role: 'user', content: 'Hello' });
    
    const { messages } = useChatStore.getState();
    expect(messages).toHaveLength(1);
    expect(messages[0].role).toBe('user');
    expect(messages[0].content).toBe('Hello');
    expect(messages[0].id).toBeDefined();
    expect(messages[0].timestamp).toBeDefined();
  });

  it('should add an assistant message with confidence', () => {
    const { addMessage } = useChatStore.getState();
    
    addMessage({
      role: 'assistant',
      content: 'AI response',
      confidence: 0.9,
    });
    
    const { messages } = useChatStore.getState();
    expect(messages).toHaveLength(1);
    expect(messages[0].role).toBe('assistant');
    expect(messages[0].confidence).toBe(0.9);
  });

  it('should set loading state', () => {
    const { setLoading } = useChatStore.getState();
    
    setLoading(true);
    expect(useChatStore.getState().isLoading).toBe(true);
    
    setLoading(false);
    expect(useChatStore.getState().isLoading).toBe(false);
  });

  it('should clear all messages', () => {
    const { addMessage, clearChat } = useChatStore.getState();
    
    addMessage({ role: 'user', content: 'Test 1' });
    addMessage({ role: 'assistant', content: 'Test 2' });
    
    expect(useChatStore.getState().messages).toHaveLength(2);
    
    clearChat();
    
    expect(useChatStore.getState().messages).toHaveLength(0);
  });

  it('should generate unique IDs for each message', () => {
    const { addMessage } = useChatStore.getState();
    
    addMessage({ role: 'user', content: 'Message 1' });
    addMessage({ role: 'user', content: 'Message 2' });
    
    const { messages } = useChatStore.getState();
    expect(messages[0].id).not.toBe(messages[1].id);
  });
});

describe('Message Formatting', () => {
  it('should generate valid ISO timestamps', () => {
    const { addMessage } = useChatStore.getState();
    
    addMessage({ role: 'user', content: 'Test' });
    
    const { messages } = useChatStore.getState();
    const timestamp = new Date(messages[0].timestamp);
    expect(timestamp.toISOString()).toBe(messages[0].timestamp);
  });
});

