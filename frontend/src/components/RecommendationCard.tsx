import React from 'react';
import type { StructuredRecommendation } from '../types';
import { StatusBadge } from './StatusBadge';
import { EvidenceCard } from './EvidenceCard';
import { ReasoningTrace } from './ReasoningTrace';
import { Clock, Zap } from 'lucide-react';

interface RecommendationCardProps {
  recommendation: StructuredRecommendation;
}

export const RecommendationCard: React.FC<RecommendationCardProps> = ({ recommendation }) => {
  return (
    <div className="card" style={{ borderTop: '4px solid var(--color-success)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
        <h3 style={{ margin: 0, fontSize: '1.25rem', color: 'var(--color-primary-dark)' }}>
          {recommendation.what_to_do}
        </h3>
        <StatusBadge status={recommendation.confidence.level} label={`${recommendation.confidence.level} Confidence`} />
      </div>

      <div style={{ fontSize: '1rem', color: 'var(--color-text-secondary)', marginBottom: '24px' }}>
        {recommendation.why_it_works}
      </div>

      <div className="grid-cols-2" style={{ marginBottom: '24px' }}>
        <div style={{ background: 'var(--color-surface-hover)', padding: '16px', borderRadius: 'var(--radius-md)' }}>
          <h4 style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem', color: 'var(--color-text-tertiary)', textTransform: 'uppercase', marginBottom: '12px' }}>
            <Zap size={16} /> Environmental Mechanism
          </h4>
          <p style={{ fontSize: '0.95rem', color: 'var(--color-text-primary)' }}>{recommendation.environmental_mechanism}</p>
        </div>
        
        <div style={{ background: 'var(--color-surface-hover)', padding: '16px', borderRadius: 'var(--radius-md)' }}>
          <h4 style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem', color: 'var(--color-text-tertiary)', textTransform: 'uppercase', marginBottom: '12px' }}>
            <Clock size={16} /> Time Horizon
          </h4>
          <p style={{ fontSize: '0.95rem', color: 'var(--color-text-primary)' }}>
            <strong>{recommendation.time_horizon.estimate.replace(/_/g, ' ')}</strong>
            <br />
            <span style={{ fontSize: '0.85rem', color: 'var(--color-text-secondary)' }}>{recommendation.time_horizon.dependency}</span>
          </p>
        </div>
      </div>

      <div style={{ marginBottom: '24px' }}>
        <h4 style={{ fontSize: '0.85rem', color: 'var(--color-text-tertiary)', textTransform: 'uppercase', marginBottom: '12px' }}>Impacted Metrics</h4>
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          {recommendation.impacted_metrics.direct.map(m => (
            <span key={m} className="badge badge-success">Direct: {m.replace(/_/g, ' ')}</span>
          ))}
          {recommendation.impacted_metrics.indirect.map(m => (
            <span key={m} className="badge badge-info">Indirect: {m.replace(/_/g, ' ')}</span>
          ))}
        </div>
      </div>

      <div className="section-divider"></div>

      <div>
        <h4 style={{ fontSize: '0.85rem', color: 'var(--color-text-tertiary)', textTransform: 'uppercase', marginBottom: '16px' }}>Scientific Foundation</h4>
        {recommendation.claims.map(claim => (
          <EvidenceCard key={claim.claim_id} claim={claim} />
        ))}
      </div>

      <ReasoningTrace trace={recommendation.reasoning_trace} />
    </div>
  );
};
