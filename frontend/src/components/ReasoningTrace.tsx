import React, { useState } from 'react';
import type { ReasoningStep } from '../types';
import { ChevronDown, ChevronRight, Activity, Link as LinkIcon, ShieldAlert, Zap, BookOpen, CheckCircle } from 'lucide-react';

interface ReasoningTraceProps {
  trace: ReasoningStep[];
}

export const ReasoningTrace: React.FC<ReasoningTraceProps> = ({ trace }) => {
  const [expanded, setExpanded] = useState(false);

  const getStepIcon = (type: string) => {
    switch (type) {
      case 'observed_condition': return <Activity size={16} />;
      case 'relationship': return <LinkIcon size={16} />;
      case 'risk_pattern': return <ShieldAlert size={16} />;
      case 'intervention': return <Zap size={16} />;
      case 'evidence': return <BookOpen size={16} />;
      case 'recommendation': return <CheckCircle size={16} />;
      default: return <Activity size={16} />;
    }
  };

  const getStepText = (step: ReasoningStep) => {
    switch (step.type) {
      case 'observed_condition': 
        return `Observed Environmental Variables: ${step.variables?.map(v => v.replace(/_/g, ' ')).join(', ')}`;
      case 'relationship': 
        return `Analyzed Environmental Relationship: ${step.relationship_id}`;
      case 'risk_pattern': 
        return `Detected Risk Pattern: ${step.risk_pattern_id?.replace(/_/g, ' ')}`;
      case 'intervention': 
        return `Matched Candidate Intervention: ${step.intervention_id?.replace(/_/g, ' ')}`;
      case 'evidence': 
        return `Retrieved Scientific Evidence Chunks (${step.chunk_ids?.length || 0} found)`;
      case 'recommendation': 
        return `Validated Recommendation (Status: ${step.status})`;
      default: 
        return `Processing Step ${step.step}`;
    }
  };

  if (!trace || trace.length === 0) return null;

  return (
    <div style={{ marginTop: '24px' }}>
      <button 
        onClick={() => setExpanded(!expanded)}
        style={{ 
          background: 'none', 
          border: 'none', 
          display: 'flex', 
          alignItems: 'center', 
          gap: '8px', 
          color: 'var(--color-secondary)', 
          fontWeight: 600, 
          cursor: 'pointer',
          padding: 0
        }}
      >
        {expanded ? <ChevronDown size={18} /> : <ChevronRight size={18} />}
        How this conclusion was reached (Auditable Trace)
      </button>

      {expanded && (
        <div style={{ marginTop: '16px', paddingLeft: '12px', borderLeft: '2px solid var(--color-border)' }}>
          {trace.map((step, idx) => (
            <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '12px', marginBottom: '16px' }}>
              <div style={{ 
                width: '28px', 
                height: '28px', 
                borderRadius: '50%', 
                background: 'var(--color-surface)', 
                border: '1px solid var(--color-border)',
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                color: 'var(--color-text-tertiary)',
                marginLeft: '-27px',
                zIndex: 1,
                position: 'relative'
              }}>
                {getStepIcon(step.type)}
              </div>
              <div style={{ paddingTop: '4px' }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--color-text-tertiary)', textTransform: 'uppercase', marginBottom: '2px', fontWeight: 600 }}>
                  Step {step.step}: {step.type.replace(/_/g, ' ')}
                </div>
                <div style={{ fontSize: '0.9rem', color: 'var(--color-text-secondary)' }}>
                  {getStepText(step)}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
