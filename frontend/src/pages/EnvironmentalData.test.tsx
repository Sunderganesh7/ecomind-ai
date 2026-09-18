import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { EnvironmentalProvider } from '../context/EnvironmentalContext';
import { EnvironmentalData } from './EnvironmentalData';
import { EnvironmentalService } from '../api/environmentalService';

// Mock EnvironmentalService
vi.mock('../api/environmentalService', () => ({
  EnvironmentalService: {
    getProfile: vi.fn(),
    getBaseline: vi.fn().mockResolvedValue({}),
    getRelationships: vi.fn().mockResolvedValue({ relationships: [] }),
    getRisks: vi.fn().mockResolvedValue({ risk_patterns: [] }),
    getRecommendations: vi.fn().mockResolvedValue({ recommendation_available: false }),
    updateProfile: vi.fn(),
  }
}));

describe('EnvironmentalData Page & Form', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(EnvironmentalService.getProfile).mockResolvedValue({
      id: 1,
      soil: {
        organic_carbon: 0.3,
        moisture: 18.0,
        soil_ph: 6.2,
      },
      climate: {
        rainfall: 500.0,
        temperature: 29.0,
      },
      land: {
        land_use: 'agriculture',
        crop: 'wheat',
        cropping_system: 'monoculture',
      },
      biodiversity: {
        species_richness: 12,
        habitat_diversity: 'low',
      },
      human_impact: {
        pollution: 'moderate',
        deforestation: 'low',
      },
      location: {
        region: 'Northern Plains',
        latitude: 28.6,
        longitude: 77.2,
      },
      source_name: 'Field Survey',
      data_quality: 'Verified',
    } as any);
  });

  it('populates existing profile data into form fields', async () => {
    render(
      <MemoryRouter>
        <EnvironmentalProvider defaultProfileId={1}>
          <EnvironmentalData />
        </EnvironmentalProvider>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByDisplayValue('0.3')).toBeDefined();
    });

    expect(screen.getByDisplayValue('500')).toBeDefined();
    expect(screen.getByDisplayValue('6.2')).toBeDefined();
    expect(screen.getByDisplayValue('wheat')).toBeDefined();
    expect(screen.getByDisplayValue('12')).toBeDefined();
  });

  it('validates invalid inputs and prevents submission', async () => {
    render(
      <MemoryRouter>
        <EnvironmentalProvider defaultProfileId={1}>
          <EnvironmentalData />
        </EnvironmentalProvider>
      </MemoryRouter>
    );

    await waitFor(() => screen.getByDisplayValue('0.3'));

    // Set invalid pH > 14
    const phInput = screen.getByDisplayValue('6.2');
    fireEvent.change(phInput, { target: { value: '15.5' } });

    // Set negative rainfall
    const rainInput = screen.getByDisplayValue('500');
    fireEvent.change(rainInput, { target: { value: '-10' } });

    // Submit
    const saveButton = screen.getByRole('button', { name: /Save Observations/i });
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(screen.getByText(/Soil pH must be between 0.0 and 14.0/i)).toBeDefined();
      expect(screen.getByText(/Rainfall must be a non-negative value/i)).toBeDefined();
      expect(screen.getByText(/Please correct the validation errors/i)).toBeDefined();
    });

    // Verify updateProfile was NOT called
    expect(EnvironmentalService.updateProfile).not.toHaveBeenCalled();
  });

  it('successfully submits valid updates and persists to backend API', async () => {
    vi.mocked(EnvironmentalService.updateProfile).mockResolvedValueOnce({
      id: 1,
      soil: { organic_carbon: 0.45 },
    } as any);

    render(
      <MemoryRouter>
        <EnvironmentalProvider defaultProfileId={1}>
          <EnvironmentalData />
        </EnvironmentalProvider>
      </MemoryRouter>
    );

    await waitFor(() => screen.getByDisplayValue('0.3'));

    // Change organic carbon to 0.45
    const socInput = screen.getByDisplayValue('0.3');
    fireEvent.change(socInput, { target: { value: '0.45' } });

    // Change rainfall to 550
    const rainInput = screen.getByDisplayValue('500');
    fireEvent.change(rainInput, { target: { value: '550' } });

    // Submit
    const saveButton = screen.getByRole('button', { name: /Save Observations/i });
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(EnvironmentalService.updateProfile).toHaveBeenCalledTimes(1);
    });

    const [calledProfileId, calledPayload] = vi.mocked(EnvironmentalService.updateProfile).mock.calls[0];
    expect(calledProfileId).toBe(1);
    expect(calledPayload.soil.organic_carbon).toBe(0.45);
    expect(calledPayload.climate.rainfall).toBe(550);

    // Verify success feedback
    await waitFor(() => {
      expect(screen.getByText(/successfully saved and downstream pipeline updated/i)).toBeDefined();
    });
  });

  it('allows leaving unsupported or optional values empty without error', async () => {
    vi.mocked(EnvironmentalService.updateProfile).mockResolvedValueOnce({
      id: 1,
    } as any);

    render(
      <MemoryRouter>
        <EnvironmentalProvider defaultProfileId={1}>
          <EnvironmentalData />
        </EnvironmentalProvider>
      </MemoryRouter>
    );

    await waitFor(() => screen.getByDisplayValue('0.3'));

    // Clear moisture input
    const moistureInput = screen.getByDisplayValue('18');
    fireEvent.change(moistureInput, { target: { value: '' } });

    // Submit
    const saveButton = screen.getByRole('button', { name: /Save Observations/i });
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(EnvironmentalService.updateProfile).toHaveBeenCalledTimes(1);
    });

    const [, calledPayload] = vi.mocked(EnvironmentalService.updateProfile).mock.calls[0];
    expect(calledPayload.soil.moisture).toBeUndefined();
  });
});
