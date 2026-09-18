import React from 'react';
import type { EnvironmentalRelationship } from '../types';
import { ArrowDown, Plus } from 'lucide-react';
import { StatusBadge } from './StatusBadge';

interface RelationshipGraphProps {
  relationships: EnvironmentalRelationship[];
}

export const RelationshipGraph: React.FC<RelationshipGraphProps> = ({ relationships }) => {
  if (!relationships || relationships.length === 0) {
    return (
      <div className="card" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '150px' }}>
        <p style={{ color: 'var(--color-text-tertiary)' }}>No complex relationships detected in current profile.</p>
      </div>
    );
  }

  return (
    <div className="grid-cols-2">
      {relationships.map((rel, idx) => (
        <div key={idx} className="card" style={{ marginBottom: 0, padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--color-text-tertiary)' }}>{rel.relationship_type?.replace(/_/g, ' ').toUpperCase() || 'RELATIONSHIP'}</span>
            <StatusBadge status={rel.evidence_status} />
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap', justifyContent: 'center' }}>
              {(rel.source_variables || rel.inputs || []).map((src, i) => (
                <React.Fragment key={src}>
                  <div style={{ padding: '8px 16px', background: 'var(--color-surface-hover)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', fontWeight: 600, color: 'var(--color-primary-dark)' }}>
                    {src.replace(/_/g, ' ')}
                  </div>
                  {i < (rel.source_variables || rel.inputs || []).length - 1 && <Plus size={16} color="var(--color-text-tertiary)" />}
                </React.Fragment>
              ))}
            </div>
            
            <ArrowDown size={24} color="var(--color-secondary)" />
            
            <div style={{ padding: '8px 16px', background: 'var(--color-success-bg)', border: '1px solid var(--color-accent-light)', borderRadius: 'var(--radius-md)', fontWeight: 600, color: 'var(--color-primary-dark)' }}>
              {(rel.target_variable || rel.downstream_states?.[0]?.name || rel.intermediate_states?.[0]?.name || rel.relationship_id).replace(/_/g, ' ')}
            </div>
          </div>
          
          <div style={{ marginTop: '20px', fontSize: '0.9rem', color: 'var(--color-text-secondary)', textAlign: 'center', fontStyle: 'italic' }}>
            "{rel.mechanism || 'Contributes to multi-metric environmental analysis'}"
          </div>
        </div>
      ))}
    </div>
  );
};
