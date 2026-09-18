import { fetchApi } from './client';
import type { EnvironmentalResponse } from '../types';

export const ChatService = {
  sendMessage: (
    message: string,
    profileId: number,
    conversationId?: string
  ) => {
    return fetchApi<EnvironmentalResponse>(`/chat/`, {
      method: 'POST',
      body: JSON.stringify({
        message,
        profile_id: String(profileId),
        conversation_id: conversationId,
      }),
    });
  },
};
