import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { vi, describe, it, expect } from 'vitest';
import { EnvironmentalProvider } from './context/EnvironmentalContext';
import { AiScientist } from './pages/AiScientist';
import { ChatService } from './api/chatService';

vi.mock('./api/client', () => ({
  fetchApi: vi.fn((endpoint: string) => {
    if (endpoint.includes('/profiles/1')) {
      return Promise.resolve({
        id: 1,
        soil: { organic_carbon: { value: 0.3 } }
      });
    }
    return Promise.resolve({});
  })
}));

vi.mock('./api/chatService', () => ({
  ChatService: {
    sendMessage: vi.fn()
  }
}));

describe('AI Scientist Workspace', () => {
  it('renders context correctly and handles missing values as Unknown', async () => {
    render(
      <MemoryRouter>
        <EnvironmentalProvider>
          <AiScientist />
        </EnvironmentalProvider>
      </MemoryRouter>
    );

    // Context should load
    await waitFor(() => {
      expect(screen.getByText(/0.3/)).toBeDefined();
    });

    const unknownElements = screen.getAllByText('Unknown');
    expect(unknownElements.length).toBeGreaterThan(0);
  });

  it('renders clarification state from backend properly', async () => {
    const mockSendMessage = vi.mocked(ChatService.sendMessage);
    mockSendMessage.mockResolvedValueOnce({
      response_type: 'clarification_needed',
      assessment: { summary: 'I need more data to analyze biodiversity.', status: 'flagged' },
      drivers: [],
      recommendations: [],
      metrics: [],
      time_horizon: { value: 'context_dependent' },
      confidence: { level: 'low', reason: '' },
      claims: [],
      variables_used: ['rainfall', 'soil_moisture'],
      reasoning_trace: []
    });

    render(
      <MemoryRouter>
        <EnvironmentalProvider>
          <AiScientist />
        </EnvironmentalProvider>
      </MemoryRouter>
    );

    await waitFor(() => screen.getByText(/0.3/));

    const input = screen.getByPlaceholderText(/Ask your environmental question/i);
    fireEvent.change(input, { target: { value: 'Why is biodiversity dropping?' } });
    
    const sendButton = screen.getByRole('button', { name: /Ask/i });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getAllByText(/Clarification Needed/i).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/I need more data to analyze biodiversity/i).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/Missing Context Needed/i).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/rainfall/i).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/soil moisture/i).length).toBeGreaterThan(0);
    });
  });
});
