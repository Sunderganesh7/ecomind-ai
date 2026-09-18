import React from 'react';
import type { VariableObservation, AnalyzedMetric } from '../types';
import { StatusBadge } from './StatusBadge';
import { Info } from 'lucide-react';

interface MetricCardProps {
  title: string;
  observation?: VariableObservation | number | string;
  analysis?: AnalyzedMetric;
  icon?: React.ReactNode;
  unit?: string;
  tooltipText?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({ title, observation, analysis, icon, unit: propUnit, tooltipText }) => {
  const value = typeof observation === 'object' && observation !== null ? observation.value : observation;
  const rawUnit = typeof observation === 'object' && observation !== null ? (observation as any).unit : undefined;
  
  let resolvedUnit = propUnit || rawUnit || analysis?.unit || (analysis as any)?.reference?.unit;
  if (!resolvedUnit) {
    const lower = title.toLowerCase();
    if (lower.includes('carbon') || lower.includes('soc')) resolvedUnit = '%';
    else if (lower.includes('rainfall')) resolvedUnit = 'mm';
    else if (lower.includes('temperature')) resolvedUnit = '°C';
    else if (lower.includes('moisture')) resolvedUnit = '%';
  }

  let isObservationValid = true;
  if (title.toLowerCase().includes('moisture')) {
    const num = typeof value === 'number' ? value : parseFloat(String(value));
    if (!isNaN(num) && (num < 0 || num > 100)) {
      isObservationValid = false;
    }
  }

  const hasValue = value !== null && value !== undefined && value !== '' && value !== 'Unknown' && isObservationValid;
  const isUnitAlreadyPresent = typeof value === 'string' && resolvedUnit && value.trim().endsWith(resolvedUnit);

  const defaultTooltip = `Current value for ${title}. ${hasValue ? 'Data is available.' : 'Data is currently unknown or unavailable.'}`;

  return (
    <div className="card card-interactive" style={{ padding: '24px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          {icon && (
            <div style={{ background: 'var(--color-surface-hover)', borderRadius: '50%', padding: '8px', display: 'flex', transition: 'transform var(--transition-fast)' }} className="metric-icon">
              {icon}
            </div>
          )}
          <span style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--color-text-secondary)' }}>{title}</span>
          
          <div className="tooltip-container" style={{ marginLeft: '4px', cursor: 'help' }}>
            <Info size={14} color="var(--color-text-tertiary)" />
            <div className="tooltip-content">
              {tooltipText || defaultTooltip}
            </div>
          </div>
        </div>
        {analysis && (
          <StatusBadge status={analysis.status} />
        )}
      </div>
      
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '4px' }}>
          {hasValue ? (
            <div className="metric-value">
              {value}
              {resolvedUnit && !isUnitAlreadyPresent && (
                <span className="metric-unit">
                  {resolvedUnit}
                </span>
              )}
            </div>
          ) : (
            <div className="metric-unknown">Unknown</div>
          )}
        </div>
      </div>
    </div>
  );
};
