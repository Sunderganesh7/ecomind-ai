import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useEnvironmentalData } from '../context/EnvironmentalContext';
import { 
  ArrowLeft, RefreshCw, Trees, Leaf, ShieldCheck, ChevronDown, ChevronUp, Link as LinkIcon, BookOpen, Bug
} from 'lucide-react';

const safeVal = (v: any): string => {
  if (v === null || v === undefined) return 'Unknown';
  if (typeof v === 'object' && 'value' in v) {
    return v.value !== null && v.value !== undefined ? String(v.value) : 'Unknown';
  }
  return String(v);
};

export const BiodiversityIntelligence: React.FC = () => {
  const { profileId, profile, baseline, relationships, risks, recommendations, loading, isFetching, refresh } = useEnvironmentalData();
  const navigate = useNavigate();

  const [expandedRels, setExpandedRels] = useState<Record<string, boolean>>({});
  const [expandedRisks, setExpandedRisks] = useState<Record<string, boolean>>({});

  const toggleRel = (id: string) => setExpandedRels(prev => ({ ...prev, [id]: !prev[id] }));
  const toggleRisk = (id: string) => setExpandedRisks(prev => ({ ...prev, [id]: !prev[id] }));

  const cardStyle = {
    background: '#ffffff',
    border: '1px solid var(--color-border)',
    borderRadius: '16px',
    padding: '24px',
    boxShadow: 'var(--shadow-sm)',
    transition: 'box-shadow var(--transition-normal)'
  };

  const badgeStyle = (status: string) => {
    const s = (status || '').toLowerCase();
    if (s.includes('optimal') || s.includes('healthy') || s.includes('supported') || s.includes('active')) {
      return { background: 'var(--color-success-bg)', color: 'var(--color-success)', border: '1px solid var(--color-success-border)' };
    }
    if (s.includes('critical') || s.includes('severe') || s.includes('risk') || s.includes('insufficient')) {
      return { background: 'var(--color-danger-bg)', color: 'var(--color-danger)', border: '1px solid var(--color-danger-border)' };
    }
    return { background: 'var(--color-warning-bg)', color: 'var(--color-warning)', border: '1px solid var(--color-warning-border)' };
  };

  const getMetricAnalysis = (key: string) => baseline?.metrics[key] || { status: 'unknown', interpretation: 'Analysis unavailable' };

  
  if (loading || !profile) {
    return (
      <div className="main-content" style={{ width: '92%', margin: '0 auto', maxWidth: '1400px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
          <div style={{ maxWidth: '650px' }}>
            <button 
              type="button"
              onClick={() => navigate('/')} 
              style={{ 
                display: 'inline-flex', alignItems: 'center', gap: '6px', 
                marginBottom: '16px', padding: '6px 12px', fontSize: '0.85rem',
                background: 'transparent', border: '1px solid var(--color-border)',
                borderRadius: '20px', color: 'var(--color-text-secondary)', cursor: 'pointer',
                transition: 'background var(--transition-fast)'
              }}
            >
              <ArrowLeft size={16} /> Back to Overview
            </button>
            <h1 style={{ margin: 0, fontSize: '2rem', color: 'var(--color-primary-dark)', fontWeight: 700, letterSpacing: '-0.02em', textTransform: 'uppercase' }}>
              Biodiversity Intelligence
            </h1>
            <p style={{ color: 'var(--color-text-secondary)', marginTop: '8px', fontSize: '1rem', lineHeight: 1.5 }}>
              Analyze habitat conditions, species diversity, and ecological resilience.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-start' }}>
            <button 
              type="button" 
              disabled={true}
              style={{ 
                display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 20px',
                background: 'white', border: '1px solid var(--color-border)',
                borderRadius: '8px', color: 'var(--color-primary)', fontWeight: 600, cursor: 'not-allowed',
                boxShadow: 'var(--shadow-sm)'
              }}
            >
              <RefreshCw size={18} className="loading-pulse" />
              Loading...
            </button>

            <div style={{ background: 'var(--color-success-bg)', borderRadius: '12px', padding: '16px', display: 'flex', gap: '16px', alignItems: 'flex-start', width: '240px', position: 'relative', overflow: 'hidden', border: '1px solid rgba(34, 197, 94, 0.2)' }}>
              <div style={{ background: 'var(--color-success)', color: 'white', borderRadius: '50%', padding: '8px', display: 'flex', zIndex: 1 }}>
                <Trees size={18} />
              </div>
              <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--color-primary-dark)', zIndex: 1, lineHeight: 1.4 }}>
                Rich Ecosystems<br/>Stronger Resilience<br/>Lasting Impact
              </div>
            </div>
          </div>
        </div>

        {/* Skeleton Main Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '32px' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
            <div className="skeleton-box" style={{ height: '250px', borderRadius: '16px' }}></div>
            <div className="skeleton-box" style={{ height: '180px', borderRadius: '16px' }}></div>
            <div className="skeleton-box" style={{ height: '180px', borderRadius: '16px' }}></div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
            <div className="skeleton-box" style={{ height: '200px', borderRadius: '16px' }}></div>
            <div className="skeleton-box" style={{ height: '250px', borderRadius: '16px' }}></div>
            <div className="skeleton-box" style={{ height: '300px', borderRadius: '16px' }}></div>
          </div>
        </div>
      </div>
    );
  }


  

  const sr = safeVal(profile.biodiversity?.species_richness);
  const hd = safeVal(profile.biodiversity?.habitat_diversity);
  
  const srAnalysis = getMetricAnalysis('species_richness');
  const hdAnalysis = getMetricAnalysis('habitat_diversity');

  const rawStatus = baseline?.summary?.habitat_status && typeof baseline.summary.habitat_status === 'object' ? baseline.summary.habitat_status.status : baseline?.summary?.habitat_status;
  let bioStatus = 'Unknown';
  if (rawStatus && rawStatus !== 'Unknown') {
    bioStatus = String(rawStatus);
  } else if (safeVal(profile.biodiversity?.species_richness) !== 'Unknown' || safeVal(profile.biodiversity?.habitat_diversity) !== 'Unknown') {
    bioStatus = 'Context Dependent';
  }

  const pageRels = (relationships?.relationships || []).filter(r => {
    const sources = r.source_variables || r.inputs || [];
    const target = r.target_variable || r.downstream_states?.[0]?.name || r.intermediate_states?.[0]?.name || '';
    return sources.some(v => v.toLowerCase().includes('species') || v.toLowerCase().includes('habitat') || v.toLowerCase().includes('biodiversity')) ||
      target.toLowerCase().includes('species') || target.toLowerCase().includes('habitat') || target.toLowerCase().includes('biodiversity');
  });

  const pageRisks = (risks?.risk_patterns || []).filter(r => {
    const vars = r.variables_used || [];
    return vars.some(v => v.toLowerCase().includes('species') || v.toLowerCase().includes('habitat') || v.toLowerCase().includes('biodiversity')) ||
      r.name.toLowerCase().includes('biodiversity') || r.name.toLowerCase().includes('habitat');
  });

  const claims = recommendations?.recommendation?.claims || [];

  return (
    <div className="main-content" style={{ width: '92%', margin: '0 auto', maxWidth: '1400px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div style={{ maxWidth: '650px' }}>
          <button 
            type="button"
            onClick={() => navigate('/')} 
            style={{ 
              display: 'inline-flex', alignItems: 'center', gap: '6px', 
              marginBottom: '16px', padding: '6px 12px', fontSize: '0.85rem',
              background: 'transparent', border: '1px solid var(--color-border)',
              borderRadius: '20px', color: 'var(--color-text-secondary)', cursor: 'pointer',
              transition: 'background var(--transition-fast)'
            }}
            onMouseOver={(e) => e.currentTarget.style.background = 'var(--color-surface-hover)'}
            onMouseOut={(e) => e.currentTarget.style.background = 'transparent'}
          >
            <ArrowLeft size={16} /> Back to Overview
          </button>
          <h1 style={{ margin: 0, fontSize: '2rem', color: 'var(--color-primary-dark)', fontWeight: 700, letterSpacing: '-0.02em', textTransform: 'uppercase' }}>
            Biodiversity Intelligence
          </h1>
          <p style={{ color: 'var(--color-text-secondary)', marginTop: '8px', fontSize: '1rem', lineHeight: 1.5 }}>
            Understand species richness, habitat condition, ecological pressure, and biodiversity-related environmental relationships.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-start' }}>
          <button 
            type="button" 
            onClick={refresh} 
            disabled={isFetching}
            style={{ 
              display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 20px',
              background: 'white', border: '1px solid var(--color-border)',
              borderRadius: '8px', color: 'var(--color-primary)', fontWeight: 600, cursor: 'pointer',
              boxShadow: 'var(--shadow-sm)', transition: 'all var(--transition-fast)'
            }}
            onMouseOver={(e) => { e.currentTarget.style.background = 'var(--color-surface-hover)'; e.currentTarget.style.borderColor = 'var(--color-border-focus)'; }}
            onMouseOut={(e) => { e.currentTarget.style.background = 'white'; e.currentTarget.style.borderColor = 'var(--color-border)'; }}
          >
            <RefreshCw size={18} className={isFetching ? 'loading-pulse' : ''} />
            {isFetching ? 'Loading...' : 'Reload Data'}
          </button>

          <div style={{ background: 'var(--color-success-bg)', borderRadius: '12px', padding: '16px', display: 'flex', gap: '16px', alignItems: 'flex-start', width: '240px', position: 'relative', overflow: 'hidden', border: '1px solid rgba(34, 197, 94, 0.2)' }}>
            <div style={{ background: 'var(--color-success)', color: 'white', borderRadius: '50%', padding: '8px', display: 'flex', zIndex: 1 }}>
              <Trees size={18} />
            </div>
            <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--color-primary-dark)', zIndex: 1, lineHeight: 1.4 }}>
              Conserve Habitats<br/>Stronger Ecosystems<br/>Resilient Planet
            </div>
            <svg style={{ position: 'absolute', right: '-15px', top: '5px', opacity: 0.08, zIndex: 0, transform: 'rotate(15deg)' }} width="80" height="80" viewBox="0 0 24 24" fill="var(--color-success)">
              <path d="M12 2C12 2 7 9 7 14C7 16.76 9.24 19 12 19C14.76 19 17 16.76 17 14C17 9 12 2 12 2Z" />
            </svg>
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '32px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
          
          <div style={{ ...cardStyle, position: 'relative' }}>
            <div style={{ position: 'absolute', right: '-10px', top: '10px', opacity: 0.03, transform: 'scale(2.5)', pointerEvents: 'none' }}>
              <Trees size={100} />
            </div>
            
            <h2 style={{ fontSize: '1.25rem', marginBottom: '24px', color: 'var(--color-primary-dark)' }}>Current Biodiversity Condition</h2>
            
            <div style={{ display: 'flex', gap: '32px', alignItems: 'stretch' }}>
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', background: 'var(--color-surface-hover)', borderRadius: '12px', padding: '24px' }}>
                <span style={{ fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--color-text-secondary)', marginBottom: '8px' }}>Status</span>
                <span style={{ fontSize: '2.5rem', fontWeight: 800, color: bioStatus.toLowerCase().includes('optimal') ? 'var(--color-success)' : (bioStatus.toLowerCase().includes('critical') ? 'var(--color-danger)' : 'var(--color-warning)'), textTransform: 'uppercase', lineHeight: 1 }}>
                  {bioStatus.replace(/_/g, ' ')}
                </span>
              </div>
              
              <div style={{ flex: 2, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                <h3 style={{ fontSize: '1rem', marginBottom: '12px', color: 'var(--color-text-primary)' }}>Key Observations</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ color: 'var(--color-text-secondary)', display: 'flex', alignItems: 'center', gap: '8px' }}><Bug size={16} color="var(--color-success)" /> Species Richness</span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <span style={{ fontWeight: 600 }}>{sr}</span>
                      <span style={{ ...badgeStyle(srAnalysis.status), padding: '4px 8px', borderRadius: '12px', fontSize: '0.75rem', fontWeight: 600 }}>{srAnalysis.status.replace(/_/g, ' ').toUpperCase()}</span>
                    </div>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ color: 'var(--color-text-secondary)', display: 'flex', alignItems: 'center', gap: '8px' }}><Leaf size={16} color="var(--color-primary)" /> Habitat Diversity</span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <span style={{ fontWeight: 600 }}>{hd}</span>
                      <span style={{ ...badgeStyle(hdAnalysis.status), padding: '4px 8px', borderRadius: '12px', fontSize: '0.75rem', fontWeight: 600 }}>{hdAnalysis.status.replace(/_/g, ' ').toUpperCase()}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div>
            <h2 style={{ fontSize: '1.25rem', marginBottom: '16px', color: 'var(--color-primary-dark)' }}>Biodiversity & Environmental Relationships</h2>
            {pageRels.length === 0 ? (
              <div style={cardStyle}><p style={{ color: 'var(--color-text-tertiary)', margin: 0 }}>No relationships found for current data.</p></div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {pageRels.map(r => (
                  <div key={r.relationship_id} style={{ ...cardStyle, padding: 0 }} className="hover-elevate">
                    <div 
                      onClick={() => toggleRel(r.relationship_id)}
                      style={{ padding: '20px', cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
                    >
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                          <span style={{ fontWeight: 600, color: 'var(--color-text-primary)' }}>{(r.source_variables || r.inputs || []).map(v => v.replace(/_/g, ' ')).join(' + ')}</span>
                          <ArrowLeft size={16} style={{ transform: 'rotate(180deg)', color: 'var(--color-text-tertiary)' }} />
                          <span style={{ fontWeight: 600, color: 'var(--color-text-primary)' }}>{(r.target_variable || r.downstream_states?.[0]?.name || r.intermediate_states?.[0]?.name || '').replace(/_/g, ' ')}</span>
                        </div>
                        <div style={{ display: 'flex', gap: '12px' }}>
                          <span style={{ ...badgeStyle(r.evidence_status), padding: '4px 8px', borderRadius: '12px', fontSize: '0.75rem', fontWeight: 600 }}>Evidence: {r.evidence_status.replace(/_/g, ' ').toUpperCase()}</span>
                        </div>
                      </div>
                      {expandedRels[r.relationship_id] ? <ChevronUp size={20} color="var(--color-text-tertiary)"/> : <ChevronDown size={20} color="var(--color-text-tertiary)"/>}
                    </div>
                    {expandedRels[r.relationship_id] && (
                      <div style={{ padding: '0 20px 20px 20px', borderTop: '1px solid var(--color-border)', marginTop: '4px', paddingTop: '16px' }}>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                          <div>
                            <span style={{ display: 'block', fontSize: '0.85rem', color: 'var(--color-text-secondary)', marginBottom: '4px' }}>Input Variables</span>
                            <span style={{ fontWeight: 500 }}>{(r.source_variables || r.inputs || []).join(', ')}</span>
                          </div>
                          <div>
                            <span style={{ display: 'block', fontSize: '0.85rem', color: 'var(--color-text-secondary)', marginBottom: '4px' }}>Environmental Effect</span>
                            <span style={{ fontWeight: 500 }}>{r.target_variable || r.downstream_states?.[0]?.name || r.intermediate_states?.[0]?.name || ''}</span>
                          </div>
                          {r.mechanism && (
                            <div style={{ gridColumn: '1 / -1' }}>
                              <span style={{ display: 'block', fontSize: '0.85rem', color: 'var(--color-text-secondary)', marginBottom: '4px' }}>Mechanism</span>
                              <span style={{ fontWeight: 400, color: 'var(--color-text-secondary)' }}>{r.mechanism}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          <div>
            <h2 style={{ fontSize: '1.25rem', marginBottom: '16px', color: 'var(--color-primary-dark)' }}>Biodiversity Risks</h2>
            {pageRisks.length === 0 ? (
              <div style={cardStyle}><p style={{ color: 'var(--color-text-tertiary)', margin: 0 }}>No active risk patterns detected for current biodiversity data.</p></div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {pageRisks.map(r => (
                  <div key={r.risk_pattern_id} style={{ ...cardStyle, padding: 0, borderLeft: `4px solid ${r.status === 'active' ? 'var(--color-danger)' : 'var(--color-warning)'}` }} className="hover-elevate">
                    <div 
                      onClick={() => toggleRisk(r.risk_pattern_id)}
                      style={{ padding: '20px', cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
                    >
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                          <ShieldCheck size={20} color={r.status === 'active' ? 'var(--color-danger)' : 'var(--color-warning)'} />
                          <span style={{ fontWeight: 600, color: 'var(--color-text-primary)' }}>{r.name.replace(/_/g, ' ')}</span>
                        </div>
                        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                          <span style={{ fontSize: '0.85rem', color: 'var(--color-text-secondary)' }}>Drivers: {r.primary_drivers.map(d => (d.variable || d.state || '').replace(/_/g, ' ')).join(', ')}</span>
                        </div>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                        <span style={{ ...badgeStyle(r.status), padding: '4px 8px', borderRadius: '12px', fontSize: '0.75rem', fontWeight: 600 }}>{(r.status || 'unknown').toUpperCase()}</span>
                        {expandedRisks[r.risk_pattern_id] ? <ChevronUp size={20} color="var(--color-text-tertiary)"/> : <ChevronDown size={20} color="var(--color-text-tertiary)"/>}
                      </div>
                    </div>
                    {expandedRisks[r.risk_pattern_id] && (
                      <div style={{ padding: '0 20px 20px 20px', borderTop: '1px solid var(--color-border)', marginTop: '4px', paddingTop: '16px' }}>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                          <div>
                            <span style={{ display: 'block', fontSize: '0.85rem', color: 'var(--color-text-secondary)', marginBottom: '8px' }}>Primary Drivers</span>
                            <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '0.9rem', color: 'var(--color-text-primary)' }}>
                              {r.primary_drivers.map((d, i) => <li key={i}>{(d.variable || d.state || '').replace(/_/g, ' ')}</li>)}
                            </ul>
                          </div>
                          <div>
                            <span style={{ display: 'block', fontSize: '0.85rem', color: 'var(--color-text-secondary)', marginBottom: '8px' }}>Potential Downstream Effects</span>
                            <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '0.9rem', color: 'var(--color-text-primary)' }}>
                              {r.secondary_consequences.map((c: any, i) => {
                                const label = typeof c === 'object' && c !== null ? (c.variable || c.name || c.state || c.status || 'Unknown') : String(c);
                                return <li key={i}>{String(label).replace(/_/g, ' ')}</li>;
                              })}
                            </ul>
                          </div>
                          <div>
                            <span style={{ display: 'block', fontSize: '0.85rem', color: 'var(--color-text-secondary)', marginBottom: '4px' }}>Evidence Status</span>
                            <span style={{ fontWeight: 500 }}>{r.evidence_status.replace(/_/g, ' ')}</span>
                          </div>
                          <div>
                            <span style={{ display: 'block', fontSize: '0.85rem', color: 'var(--color-text-secondary)', marginBottom: '4px' }}>Uncertainty</span>
                            <span style={{ fontWeight: 500 }}>{r.uncertainty.level.replace(/_/g, ' ')}</span>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
          
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
          <div style={{ ...cardStyle, background: 'var(--color-surface-hover)' }}>
            <h3 style={{ fontSize: '1.1rem', color: 'var(--color-primary-dark)', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <BookOpen size={20} /> BIODIVERSITY INTELLIGENCE
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div>
                <span style={{ display: 'block', fontSize: '0.85rem', color: 'var(--color-text-tertiary)', marginBottom: '4px' }}>Current Condition</span>
                <span style={{ fontWeight: 600, color: 'var(--color-text-primary)' }}>{bioStatus.replace(/_/g, ' ').toUpperCase()}</span>
              </div>
              <div>
                <span style={{ display: 'block', fontSize: '0.85rem', color: 'var(--color-text-tertiary)', marginBottom: '4px' }}>Key Indicators</span>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  <span style={{ background: 'white', padding: '4px 10px', borderRadius: '12px', fontSize: '0.8rem', border: '1px solid var(--color-border)' }}>Species Richness</span>
                  <span style={{ background: 'white', padding: '4px 10px', borderRadius: '12px', fontSize: '0.8rem', border: '1px solid var(--color-border)' }}>Habitat Diversity</span>
                </div>
              </div>
            </div>
          </div>

          <div style={cardStyle}>
            <h3 style={{ fontSize: '1.1rem', color: 'var(--color-primary-dark)', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <BookOpen size={20} /> Scientific Evidence
            </h3>
            {claims.length === 0 ? (
              <p style={{ fontSize: '0.9rem', color: 'var(--color-text-secondary)', margin: 0 }}>Insufficient scientific evidence.</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {claims.slice(0, 3).map(claim => (
                  <div key={claim.claim_id} style={{ background: 'var(--color-surface-hover)', padding: '16px', borderRadius: '12px' }} className="hover-elevate">
                    <span style={{ ...badgeStyle(claim.support_status), padding: '2px 8px', borderRadius: '12px', fontSize: '0.7rem', fontWeight: 600, display: 'inline-block', marginBottom: '8px' }}>{(claim.support_status || 'unknown').toUpperCase()}</span>
                    <p style={{ fontSize: '0.9rem', margin: '0 0 12px 0', color: 'var(--color-text-primary)' }}>{claim.claim_text}</p>
                    {(claim.evidence || []).map((ev, i) => (
                      <div key={i} style={{ borderTop: '1px solid var(--color-border)', paddingTop: '12px', marginTop: '12px' }}>
                        <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--color-text-tertiary)', marginBottom: '4px' }}>Source: {ev.source || ev.document || 'Unknown'}</span>
                        {ev.url && (
                          <a href={ev.url} target="_blank" rel="noreferrer" style={{ fontSize: '0.8rem', color: 'var(--color-primary)', display: 'inline-flex', alignItems: 'center', gap: '4px', textDecoration: 'none', fontWeight: 500 }}>
                            <LinkIcon size={12} /> View Source
                          </a>
                        )}
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
