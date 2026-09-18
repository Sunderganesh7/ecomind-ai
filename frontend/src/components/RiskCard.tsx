import React, { useState } from 'react';
import type { CompositeRiskPattern } from '../types';
import { StatusBadge } from './StatusBadge';
import { Leaf, Droplets, Trees, MapIcon, ChevronDown, ChevronUp } from 'lucide-react';

interface RiskCardProps {
  risk: CompositeRiskPattern;
}

export const RiskCard: React.FC<RiskCardProps> = ({ risk }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const isWarning = risk.status !== 'active';
  const riskClass = isWarning ? 'risk-potential' : 'risk-active';
  
  // Choose an icon based on risk name for aesthetic variety matching the screenshot
  const nameLower = risk.name.toLowerCase();
  let Icon = Leaf;
  if (nameLower.includes('water') || nameLower.includes('moisture')) Icon = Droplets;
  else if (nameLower.includes('habitat') || nameLower.includes('deforestation')) Icon = Trees;
  else if (nameLower.includes('biodiversity')) Icon = Leaf;
  const formatLabel = (str: string) => {
    return str
      .replace(/_/g, ' ')
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <div className={`risk-card ${riskClass}`}>
      <div className="risk-accent-line"></div>
      
      <div className="risk-header" onClick={() => setIsExpanded(!isExpanded)} role="button" tabIndex={0} onKeyDown={(e) => { if(e.key === 'Enter' || e.key === ' ') setIsExpanded(!isExpanded); }}>
        <div className="risk-icon-wrapper">
          <Icon size={24} />
        </div>
        <div style={{ flex: 1 }}>
          <h3 className="risk-title" style={{ marginBottom: '4px' }}>
            {formatLabel(risk.name)}
          </h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--color-text-secondary)', margin: 0, opacity: isExpanded ? 0 : 1, transition: 'opacity 0.2s', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '80%' }}>
            {risk.primary_drivers.map(d => formatLabel(d.variable || '')).join(', ')}
          </p>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <StatusBadge status={risk.status} />
          <div style={{ color: 'var(--color-text-tertiary)' }}>
            {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
          </div>
        </div>
      </div>

      {isExpanded && (
        <div className="risk-details-content">
          <div>
            <h4>Primary Drivers</h4>
            <ul>
              {risk.primary_drivers.map((d, idx) => (
                <li key={idx}>
                  {formatLabel(d.variable || d.state || '')} <span style={{color: 'var(--color-text-tertiary)', fontSize: '0.8rem', marginLeft: '4px'}}>({formatLabel(d.status)})</span>
                </li>
              ))}
            </ul>
          </div>
          
          <div>
            <h4>Secondary Consequences</h4>
            {risk.secondary_consequences.length > 0 ? (
              <ul>
                {risk.secondary_consequences.map((c: any, idx) => {
                  const rawLabel = typeof c === 'object' && c !== null 
                    ? (c.variable || c.name || c.state || c.status || 'Unknown')
                    : String(c);
                  return <li key={idx}>{formatLabel(String(rawLabel))}</li>;
                })}
              </ul>
            ) : (
              <div style={{ color: 'var(--color-text-tertiary)', fontSize: '0.85rem' }}>None identified</div>
            )}
          </div>
        </div>
      )}

      {isExpanded && (
        <div className="risk-metadata">
          <div className="meta-group">
            <span className="meta-label">Evidence</span>
            <StatusBadge status={risk.evidence_status} />
          </div>
          <div className="meta-group">
            <span className="meta-label">Uncertainty</span>
            <StatusBadge status={risk.uncertainty.level} />
          </div>
          <div className="meta-group" style={{ flex: 1 }}>
            <span className="meta-label">Variables Used</span>
            <div className="meta-value">
              {risk.variables_used.map(v => (
                <span key={v} className="meta-pill">
                  {formatLabel(v)}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
