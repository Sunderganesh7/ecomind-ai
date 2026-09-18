import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { vi, describe, it, expect } from 'vitest';
import { EnvironmentalProvider } from './context/EnvironmentalContext';
import { DashboardOverview } from './pages/DashboardOverview';

// Mock the API client
vi.mock('./api/client', () => ({
  fetchApi: vi.fn((endpoint: string) => {
    if (endpoint.includes('/profiles/1/baseline')) {
      return Promise.resolve({
        profile_id: 1,
        metrics: {
          organic_carbon: { status: 'low', interpretation: 'Low SOC' }
        },
        warnings: [],
        summary: { soil_status: 'marginal' }
      });
    }
    if (endpoint.includes('/profiles/1/relationships')) {
      return Promise.resolve({ profile_id: 1, relationships: [], variables_used: [] });
    }
    if (endpoint.includes('/profiles/1/risks')) {
      return Promise.resolve({ profile_id: 1, risk_patterns: [] });
    }
    if (endpoint.includes('/profiles/1/recommendations')) {
      return Promise.resolve({ recommendation_available: false, quality_guard: { status: 'passed' } });
    }
    if (endpoint.includes('/profiles/1')) {
      return Promise.resolve({
        id: 1,
        soil: {
          organic_carbon: { value: 0.3 }
          // intentionally omitting moisture to test "Unknown" state
        }
      });
    }
    return Promise.resolve({});
  })
}));

describe('Professional Environmental Dashboard', () => {
  it('renders loading state initially', () => {
    render(
      <MemoryRouter>
        <EnvironmentalProvider>
          <DashboardOverview />
        </EnvironmentalProvider>
      </MemoryRouter>
    );
    expect(document.querySelector('.skeleton-box')).not.toBeNull();
  });

  it('renders Dashboard Overview and handles missing values as Unknown', async () => {
    render(
      <MemoryRouter>
        <EnvironmentalProvider>
          <DashboardOverview />
        </EnvironmentalProvider>
      </MemoryRouter>
    );

    // Wait for the data to load
    await waitFor(() => {
      // Profile ID should be rendered
      expect(screen.getByText(/ENVIRONMENTAL INTELLIGENCE/i)).toBeDefined();
    });

    // Check organic carbon value is rendered
    expect(screen.getByText(/0.3/)).toBeDefined();

    // Check missing value is rendered as "Unknown", not 0 or silently omitted
    // Soil Moisture is completely missing from the mock
    const unknownElements = screen.getAllByText('Unknown');
    expect(unknownElements.length).toBeGreaterThan(0);
  });
});
