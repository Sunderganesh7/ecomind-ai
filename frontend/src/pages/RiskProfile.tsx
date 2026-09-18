import React from 'react';
import { useEnvironmentalData } from '../context/EnvironmentalContext';
import { RiskCard } from '../components/RiskCard';

export const RiskProfile: React.FC = () => {
  const { risks, loading, error } = useEnvironmentalData();

  if (loading) {
    return (
      <div className="main-content">
        <div style={{ marginBottom: '40px' }}>
          <div className="skeleton-box" style={{ height: '40px', width: '250px', marginBottom: '16px' }}></div>
          <div className="skeleton-box" style={{ height: '24px', width: '400px' }}></div>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div className="card skeleton-box" style={{ height: '160px' }}></div>
          <div className="card skeleton-box" style={{ height: '160px' }}></div>
          <div className="card skeleton-box" style={{ height: '160px' }}></div>
        </div>
      </div>
    );
  }
  if (error) {
    return <div className="main-content"><div className="card badge-danger">{error}</div></div>;
  }

  return (
    <div className="main-content">
      <div style={{ marginBottom: '40px' }}>
        <h1 style={{ marginBottom: '8px' }}>Risk Profile</h1>
        <p style={{ color: 'var(--color-text-secondary)' }}>
          Detailed view of active and potential environmental risk patterns.
        </p>
      </div>

      {(!risks?.risk_patterns || risks.risk_patterns.length === 0) ? (
        <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
          <p style={{ color: 'var(--color-text-tertiary)' }}>No active risk patterns detected.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {risks.risk_patterns.map(risk => (
            <RiskCard key={risk.risk_pattern_id} risk={risk} />
          ))}
        </div>
      )}
    </div>
  );
};
