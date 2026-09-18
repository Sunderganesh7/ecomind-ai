import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { EnvironmentalProvider } from './context/EnvironmentalContext';
import { DashboardOverview } from './pages/DashboardOverview';
import { AiScientist } from './pages/AiScientist';
import { EnvironmentalService } from './api/environmentalService';

// Mock EnvironmentalService
vi.mock('./api/environmentalService', () => ({
  EnvironmentalService: {
    getProfile: vi.fn(),
    getBaseline: vi.fn(),
    getRelationships: vi.fn(),
    getRisks: vi.fn(),
    getRecommendations: vi.fn(),
    updateProfile: vi.fn(),
  }
}));

describe('Dynamic Dashboard & AI Scientist Profile Updates', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders Unknown on Dashboard when observations are missing, and shows formatted units when present', async () => {
    // Initial profile with only SOC, rainfall and species richness omitted
    vi.mocked(EnvironmentalService.getProfile).mockResolvedValueOnce({
      id: 1,
      soil: { organic_carbon: 0.3 },
      climate: null, // rainfall missing
      biodiversity: null, // species richness missing
    } as any);

    vi.mocked(EnvironmentalService.getBaseline).mockResolvedValueOnce({
      profile_id: 1,
      metrics: {
        organic_carbon: { status: 'low', unit: '%' },
      },
      summary: { soil_status: 'degraded', water_status: null, habitat_status: null },
    } as any);
    vi.mocked(EnvironmentalService.getRelationships).mockResolvedValueOnce({ relationships: [] } as any);
    vi.mocked(EnvironmentalService.getRisks).mockResolvedValueOnce({ risk_patterns: [] } as any);
    vi.mocked(EnvironmentalService.getRecommendations).mockResolvedValueOnce({ recommendation_available: false } as any);

    render(
      <MemoryRouter>
        <EnvironmentalProvider defaultProfileId={1}>
          <DashboardOverview />
        </EnvironmentalProvider>
      </MemoryRouter>
    );

    // Wait for Dashboard to render
    await waitFor(() => {
      expect(screen.getByText(/ENVIRONMENTAL INTELLIGENCE/i)).toBeDefined();
    });

    // SOC is present with unit
    expect(screen.getByText(/0.3/)).toBeDefined();

    // Rainfall and Species Richness cards should display "Unknown"
    const unknownElements = screen.getAllByText('Unknown');
    expect(unknownElements.length).toBeGreaterThanOrEqual(2);
  });

  it('displays updated profile values in AI Scientist Environmental Context panel', async () => {
    vi.mocked(EnvironmentalService.getProfile).mockResolvedValueOnce({
      id: 1,
      soil: { organic_carbon: 0.45, moisture: 22.0, soil_ph: 6.8 },
      climate: { rainfall: 620.0, temperature: 26.5 },
      land: { crop: 'legumes', cropping_system: 'intercropping' },
      biodiversity: { species_richness: 25, habitat_diversity: 'moderate' },
      location: { region: 'Eastern Highlands' },
    } as any);

    vi.mocked(EnvironmentalService.getBaseline).mockResolvedValueOnce({} as any);
    vi.mocked(EnvironmentalService.getRelationships).mockResolvedValueOnce({ relationships: [] } as any);
    vi.mocked(EnvironmentalService.getRisks).mockResolvedValueOnce({ risk_patterns: [] } as any);
    vi.mocked(EnvironmentalService.getRecommendations).mockResolvedValueOnce({ recommendation_available: false } as any);

    render(
      <MemoryRouter>
        <EnvironmentalProvider defaultProfileId={1}>
          <AiScientist />
        </EnvironmentalProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/AI Environmental Scientist/i)).toBeDefined();
    });

    // Check that context panel reflects updated values
    expect(screen.getByText(/Eastern Highlands/i)).toBeDefined();
    expect(screen.getByText(/0.45%/)).toBeDefined();
    expect(screen.getByText(/620 mm/)).toBeDefined();
    expect(screen.getByText(/legumes/i)).toBeDefined();
    expect(screen.getByText(/25/)).toBeDefined();
  });
});
