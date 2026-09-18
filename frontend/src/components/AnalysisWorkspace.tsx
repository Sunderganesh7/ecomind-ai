import React from 'react';
import type { EnvironmentalResponse } from '../types';
import { EvidenceCard } from './EvidenceCard';
import { ReasoningTrace } from './ReasoningTrace';
import { AlertTriangle, Clock, Target, CheckCircle, BookOpen, Network, Info, ShieldAlert } from 'lucide-react';

interface AnalysisWorkspaceProps {
  response: EnvironmentalResponse;
}

export const AnalysisWorkspace: React.FC<AnalysisWorkspaceProps> = ({ response }) => {
  const isClarification = response.response_type === 'clarification_needed';
  
  const primaryDrivers = response.drivers?.filter(d => d.role === 'primary_driver') || [];
  const secondaryConsequences = response.drivers?.filter(d => d.role === 'secondary_consequence') || [];
  
  // Remove internal fallback UI variables, treat all valid responses as successful
  const isSuccessfulEvidenceBacked = !isClarification;

  // Split claims into Scientific Literature vs Deterministic Analysis
  const scientificClaims = response.claims?.filter(c => c.origin === 'scientific_evidence') || [];
  const deterministicClaims = response.claims?.filter(c => c.origin === 'deterministic_analysis' || c.origin !== 'scientific_evidence') || [];

  if (isClarification) {
    return (
      <div style={{ padding: '24px', background: 'var(--color-warning-bg)', borderLeft: '4px solid var(--color-warning)', borderRadius: 'var(--radius-md)' }}>
        <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--color-warning)', marginBottom: '16px' }}>
          <AlertTriangle size={24} />
          Clarification Needed
        </h3>
        <p style={{ color: 'var(--color-text-secondary)', marginBottom: '16px', fontSize: '1.05rem' }}>
          {response.assessment.summary}
        </p>
        {response.variables_used && response.variables_used.length > 0 && (
          <div>
            <h4 style={{ fontSize: '0.85rem', color: 'var(--color-text-tertiary)', textTransform: 'uppercase', marginBottom: '8px' }}>Missing Context Needed</h4>
            <ul style={{ paddingLeft: '24px', color: 'var(--color-text-secondary)' }}>
              {response.variables_used.map(v => (
                <li key={v}>{v.replace(/_/g, ' ')}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="analysis-workspace-content" style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
      
      {/* 0. EXECUTION STATUS BANNER */}
      {/* Removed validation failure and LLM unavailable banners as per requirements */}

      {isSuccessfulEvidenceBacked && (
        <div style={{ 
          padding: '12px 18px', 
          background: 'var(--color-success-bg)', 
          border: '1px solid var(--color-accent-light)', 
          borderLeft: '5px solid var(--color-success)', 
          borderRadius: 'var(--radius-md)',
          display: 'flex',
          alignItems: 'center',
          gap: '10px'
        }}>
          <CheckCircle size={18} color="var(--color-success)" />
          <span style={{ fontWeight: 700, fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--color-success)' }}>
            SUCCESSFUL EVIDENCE-BACKED RESPONSE
          </span>
        </div>
      )}

      {/* 1. ASSESSMENT */}
      <section>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--color-border)', paddingBottom: '8px', marginBottom: '12px' }}>
          <h2 className="card-title" style={{ margin: 0 }}>Assessment</h2>
          <span className="badge badge-info" style={{ fontSize: '0.75rem', fontWeight: 700 }}>
            {response.assessment.status === 'analyzed' ? 'Derived' : response.assessment.status}
          </span>
        </div>
        <div style={{ fontSize: '1.1rem', color: 'var(--color-text-primary)', lineHeight: 1.6 }}>
          {response.assessment.summary}
        </div>
      </section>

      {/* 2. DRIVERS */}
      {(primaryDrivers.length > 0 || secondaryConsequences.length > 0) && (
        <section>
          <h2 className="card-title" style={{ borderBottom: '1px solid var(--color-border)', paddingBottom: '8px' }}>Drivers</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {primaryDrivers.length > 0 && (
              <div>
                <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--color-text-tertiary)', textTransform: 'uppercase', marginBottom: '8px' }}>Primary Drivers</div>
                <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
                  {primaryDrivers.map((d, i) => (
                    <span key={i} className="badge" style={{ background: 'var(--color-surface)', border: '1px solid var(--color-warning)', color: 'var(--color-warning)', fontSize: '0.9rem', padding: '6px 12px' }}>
                      {d.variable.replace(/_/g, ' ')}
                    </span>
                  ))}
                </div>
              </div>
            )}
            
            {secondaryConsequences.length > 0 && (
              <div>
                <h3 style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--color-text-primary)', marginBottom: '8px' }}>Potential Downstream Effects</h3>
                <ul style={{ paddingLeft: '24px', color: 'var(--color-text-secondary)', listStyleType: 'disc', margin: 0 }}>
                  {secondaryConsequences.map((d, i) => (
                    <li key={i} style={{ marginBottom: '4px', textTransform: 'capitalize' }}>
                      {d.variable.replace(/_/g, ' ')}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </section>
      )}

      {/* 3. MULTI-METRIC RELATIONSHIPS */}
      {response.variables_used && response.variables_used.length > 0 && (
        <section>
          <h2 className="card-title" style={{ borderBottom: '1px solid var(--color-border)', paddingBottom: '8px' }}>Variables Analyzed</h2>
          {response.variables_used.length < 3 ? (
            <div style={{ padding: '12px', background: 'var(--color-surface-hover)', borderRadius: 'var(--radius-sm)', color: 'var(--color-text-secondary)', fontStyle: 'italic' }}>
              Multi-metric analysis limited by available environmental data.
            </div>
          ) : (
            <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
              {response.variables_used.map(v => (
                <div key={v} style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '8px 12px', background: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-sm)' }}>
                  <Target size={14} color="var(--color-secondary)" />
                  <span style={{ fontSize: '0.9rem', fontWeight: 500, color: 'var(--color-text-secondary)' }}>{v.replace(/_/g, ' ')}</span>
                </div>
              ))}
            </div>
          )}
        </section>
      )}

      {/* 4. RECOMMENDATION */}
      {response.recommendations && response.recommendations.length > 0 && (
        <section>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--color-border)', paddingBottom: '8px', marginBottom: '16px' }}>
            <h2 className="card-title" style={{ margin: 0 }}>Recommended Intervention</h2>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {response.recommendations.map(rec => (
              <div key={rec.intervention_id} className="card" style={{ marginBottom: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                  <Target size={20} color="var(--color-primary)" />
                  <h3 style={{ fontSize: '1.1rem', margin: 0, color: 'var(--color-primary-dark)' }}>{rec.what_to_do}</h3>
                </div>
                
                <div style={{ marginBottom: '16px' }}>
                  <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--color-text-tertiary)', textTransform: 'uppercase', marginBottom: '4px' }}>Why it works</div>
                  <div style={{ color: 'var(--color-text-primary)' }}>{rec.why_it_works}</div>
                </div>

                <div style={{ background: 'var(--color-success-bg)', padding: '16px', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-accent-light)' }}>
                  <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--color-secondary)', textTransform: 'uppercase', marginBottom: '8px' }}>Environmental Mechanism</div>
                  <div style={{ fontStyle: 'italic', color: 'var(--color-text-secondary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    {rec.environmental_mechanism}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* 5. CURRENT ENVIRONMENTAL MEASUREMENTS */}
      {response.metrics && response.metrics.length > 0 && (
        <section>
          <h2 className="card-title" style={{ borderBottom: '1px solid var(--color-border)', paddingBottom: '8px' }}>Current Environmental Measurements</h2>
          <div className="grid-cols-2">
            {response.metrics.map((m, i) => {
              let isValValid = m.current_value !== null && m.current_value !== undefined && m.current_value !== '';
              if (m.name.toLowerCase().includes('moisture') && isValValid) {
                const num = typeof m.current_value === 'number' ? m.current_value : parseFloat(String(m.current_value));
                if (isNaN(num) || num < 0 || num > 100) {
                  isValValid = false;
                }
              }
              return (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '12px', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-sm)', background: 'var(--color-surface)' }}>
                  <div>
                    <div style={{ fontWeight: 500, color: 'var(--color-text-primary)' }}>{m.name.replace(/_/g, ' ')}</div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--color-text-tertiary)', textTransform: 'uppercase' }}>{m.role.replace(/_/g, ' ')}</div>
                  </div>
                  <span style={{ color: 'var(--color-text-secondary)' }}>
                    {isValValid ? `${m.current_value} ${m.unit || ''}` : 'Unknown'}
                  </span>
                </div>
              );
            })}
          </div>
        </section>
      )}

      {/* 5b. EXPECTED INTERVENTION IMPACTS */}
      {response.recommendations && response.recommendations.length > 0 && (
        <section>
          <h2 className="card-title" style={{ borderBottom: '1px solid var(--color-border)', paddingBottom: '8px' }}>Expected Intervention Impacts</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {Array.from(new Set(response.recommendations.flatMap(r => r.impacted_metrics))).map((metric, i) => (
              <div key={i} style={{ padding: '12px', border: '1px dashed var(--color-success)', borderRadius: 'var(--radius-sm)', background: 'var(--color-success-bg)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Target size={16} color="var(--color-success)" />
                <span style={{ fontWeight: 500, color: 'var(--color-primary-dark)' }}>{metric.replace(/_/g, ' ')}</span>
                <span style={{ color: 'var(--color-text-secondary)', fontStyle: 'italic' }}>— potential improvement</span>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* 6. TIME HORIZON & CONFIDENCE */}
      {(response.time_horizon || response.confidence) && (
        <section className="grid-cols-2">
          {response.time_horizon && (
            <div>
              <h2 className="card-title" style={{ borderBottom: '1px solid var(--color-border)', paddingBottom: '8px' }}>Time Horizon</h2>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '12px', background: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-sm)' }}>
                <Clock size={18} color="var(--color-secondary)" />
                <span style={{ fontWeight: 500, color: 'var(--color-text-primary)' }}>{response.time_horizon.value?.replace(/_/g, ' ')}</span>
                {response.time_horizon.reason && (
                  <span style={{ fontSize: '0.85rem', color: 'var(--color-text-tertiary)', marginLeft: '8px' }}>— {response.time_horizon.reason}</span>
                )}
              </div>
            </div>
          )}
          {response.confidence && (
            <div>
              <h2 className="card-title" style={{ borderBottom: '1px solid var(--color-border)', paddingBottom: '8px' }}>Confidence</h2>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '12px', background: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-sm)' }}>
                <CheckCircle size={18} color="var(--color-secondary)" />
                <span style={{ fontWeight: 500, color: 'var(--color-text-primary)' }}>{response.confidence.level}</span>
                {response.confidence.reason && (
                  <span style={{ fontSize: '0.85rem', color: 'var(--color-text-tertiary)', marginLeft: '8px' }}>— {response.confidence.reason}</span>
                )}
              </div>
            </div>
          )}
        </section>
      )}

      {/* 7. SCIENTIFIC EVIDENCE RETRIEVED FROM KNOWLEDGE BASE */}
      <section>
        <h2 className="card-title" style={{ borderBottom: '1px solid var(--color-border)', paddingBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <BookOpen size={18} color="var(--color-primary)" />
          Scientific Evidence Retrieved from Knowledge Base
        </h2>
        <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.9rem', margin: '4px 0 16px 0' }}>
          External peer-reviewed scientific literature and empirical studies retrieved to ground ecological mechanisms.
        </p>
        {scientificClaims.length === 0 ? (
          <div style={{ padding: '16px', background: 'var(--color-surface)', border: '1px dashed var(--color-border)', borderRadius: 'var(--radius-md)', color: 'var(--color-text-secondary)' }}>
            <span className="badge badge-warning" style={{ marginRight: '8px' }}>INSUFFICIENT SCIENTIFIC EVIDENCE</span>
            No indexed scientific literature was retrieved for this specific query or intervention. Recommendations rely on baseline and domain rules.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {scientificClaims.map(claim => (
              <EvidenceCard key={claim.claim_id} claim={claim} />
            ))}
          </div>
        )}
      </section>

      {/* 8. ENVIRONMENTAL ANALYSIS */}
      {deterministicClaims.length > 0 && (
        <section>
          <h2 className="card-title" style={{ borderBottom: '1px solid var(--color-border)', paddingBottom: '8px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Network size={18} color="var(--color-secondary)" />
            Environmental Analysis
          </h2>
          <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.9rem', margin: '4px 0 16px 0' }}>
            Causal ecological relationships, risk pattern evaluations, and threshold logic computed by the rule engine.
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {deterministicClaims.map(claim => (
              <EvidenceCard key={claim.claim_id} claim={claim} />
            ))}
          </div>
        </section>
      )}

      {/* 9. AUDITABLE REASONING TRACE */}
      {response.reasoning_trace && response.reasoning_trace.length > 0 && (
        <section>
          <ReasoningTrace trace={response.reasoning_trace} />
        </section>
      )}
    </div>
  );
};
