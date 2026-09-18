import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { vi, describe, it, expect } from 'vitest';
import { EnvironmentalProvider } from '../context/EnvironmentalContext';
import { EvidenceAndReasoning } from './EvidenceAndReasoning';

vi.mock('../api/client', () => ({
  fetchApi: vi.fn((endpoint: string) => {
    if (endpoint.includes('/profiles/1/relationships')) {
      return Promise.resolve({
        profile_id: 1,
        relationships: [
          {
            relationship_id: 'rel_1',
            source_variables: ['organic_carbon', 'soil_moisture'],
            target_variable: 'vegetation_condition',
            relationship_type: 'synergistic',
            mechanism: 'Supports vegetation condition assessment',
            evidence_status: 'supported'
          }
        ],
        variables_used: ['organic_carbon', 'soil_moisture']
      });
    }
    if (endpoint.includes('/profiles/1/risks')) {
      return Promise.resolve({
        profile_id: 1,
        risk_patterns: [
          {
            risk_pattern_id: 'risk_1',
            name: 'Composite Biodiversity Pressure',
            primary_drivers: [{ variable: 'organic_carbon', state: 'Low' }],
            secondary_consequences: ['Potential reduced habitat quality'],
            relationships_used: ['rel_1'],
            variables_used: ['organic_carbon']
          }
        ]
      });
    }
    if (endpoint.includes('/profiles/1/recommendations')) {
      return Promise.resolve({
        recommendation_available: true,
        recommendation: {
          what_to_do: 'Test recommendation action',
          why_it_works: 'Test reason',
          environmental_mechanism: 'Test mechanism',
          variables_used: ['organic_carbon'],
          relationships_used: ['rel_1'],
          risk_patterns_used: ['risk_1'],
          time_horizon: { estimate: 'short_term' },
          confidence: { level: 'high' },
          impacted_metrics: { direct: ['organic_carbon'], indirect: [] },
          claims: [
            {
              claim_id: 'claim_1',
              claim_type: 'environmental_mechanism',
              claim_text: 'Test scientific claim',
              evidence: [
                { chunk_id: 'chunk_abc', document: 'Test Paper', source: 'IPCC', year: 2023 }
              ]
            }
          ],
          reasoning_trace: []
        },
        quality_guard: { status: 'passed' }
      });
    }
    if (endpoint.includes('/profiles/1')) {
      return Promise.resolve({
        id: 1,
        soil: {
          organic_carbon: { value: 0.3 }
        }
      });
    }
    return Promise.resolve({});
  })
}));

describe('Evidence & Reasoning Visualization', () => {
  it('renders all pipeline layers successfully with mocked data', async () => {
    render(
      <MemoryRouter>
        <EnvironmentalProvider>
          <EvidenceAndReasoning />
        </EnvironmentalProvider>
      </MemoryRouter>
    );

    // Wait for the page to load data
    await waitFor(() => {
      expect(screen.getByText(/Trace how environmental observations/i)).toBeDefined();
    });

    // 1. Check Variables
    expect(screen.getByText('0.3')).toBeDefined();

    // 2. Check Relationships
    expect(screen.getByText('vegetation condition')).toBeDefined();

    // 3. Check Risks
    expect(screen.getByText('Composite Biodiversity Pressure')).toBeDefined();

    // 4. Check Evidence
    expect(screen.getByText(/Test scientific claim/)).toBeDefined();
    expect(screen.getByText(/Test Paper/)).toBeDefined();
    expect(screen.getByText(/IPCC/)).toBeDefined();

    // 5. Check Recommendation
    expect(screen.getByText('Test recommendation action')).toBeDefined();
    expect(screen.getByText('Test mechanism')).toBeDefined();
  });
});
