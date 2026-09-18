import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ChatService } from './chatService';
import * as client from './client';

describe('ChatService Contract', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('sends exactly { message, profile_id, conversation_id } matching backend ChatRequest', async () => {
    const fetchApiSpy = vi.spyOn(client, 'fetchApi').mockResolvedValue({
      conversation_id: 'conv-123',
      response_type: 'environmental_assessment',
      assessment: { summary: 'Assessment summary', status: 'informational' },
      time_horizon: { value: 'not_applicable' },
      confidence: { level: 'high' },
      drivers: [],
      recommendations: [],
      metrics: [],
      claims: [],
      variables_used: [],
      reasoning_trace: []
    } as any);

    await ChatService.sendMessage('What is driving biodiversity loss?', 1, 'conv-123');

    expect(fetchApiSpy).toHaveBeenCalledTimes(1);
    const [endpoint, options] = fetchApiSpy.mock.calls[0];

    expect(endpoint).toBe('/chat/');
    expect(options?.method).toBe('POST');

    const body = JSON.parse(options?.body as string);
    // Assert exactly the backend contract keys
    expect(body).toEqual({
      message: 'What is driving biodiversity loss?',
      profile_id: '1',
      conversation_id: 'conv-123'
    });
    // Ensure legacy keys are NOT present
    expect(body).not.toHaveProperty('query');
    expect(body).not.toHaveProperty('history');
  });

  it('handles optional conversationId gracefully', async () => {
    const fetchApiSpy = vi.spyOn(client, 'fetchApi').mockResolvedValue({} as any);

    await ChatService.sendMessage('Evaluate soil health', 2);

    expect(fetchApiSpy).toHaveBeenCalledTimes(1);
    const [, options] = fetchApiSpy.mock.calls[0];
    const body = JSON.parse(options?.body as string);

    expect(body.message).toBe('Evaluate soil health');
    expect(body.profile_id).toBe('2');
    expect(body.conversation_id).toBeUndefined();
  });
});
