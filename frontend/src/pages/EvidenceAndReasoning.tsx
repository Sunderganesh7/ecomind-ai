import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useEnvironmentalData } from '../context/EnvironmentalContext';
import { 
  ArrowLeft, RefreshCw, Layers, ShieldCheck, Link as LinkIcon, BookOpen, ChevronDown, ChevronUp, CheckCircle, Network, Search
} from 'lucide-react';

const safeVal = (v: any): string => {
  if (v === null || v === undefined) return 'Unknown';
  if (typeof v === 'object' && 'value' in v) {
    return v.value !== null && v.value !== undefined ? String(v.value) : 'Unknown';
  }
  return String(v);
};

export const EvidenceAndReasoning: React.FC = () => {
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
    if (s.includes('optimal') || s.includes('healthy') || s.includes('supported') || s.includes('active') || s.includes('low')) {
      return { background: 'var(--color-success-bg)', color: 'var(--color-success)', border: '1px solid var(--color-success-border)' };
    }
    if (s.includes('critical') || s.includes('severe') || s.includes('risk') || s.includes('insufficient') || s.includes('high')) {
      return { background: 'var(--color-danger-bg)', color: 'var(--color-danger)', border: '1px solid var(--color-danger-border)' };
    }
    return { background: 'var(--color-warning-bg)', color: 'var(--color-warning)', border: '1px solid var(--color-warning-border)' };
  };

  
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
              Evidence & Reasoning
            </h1>
            <p style={{ color: 'var(--color-text-secondary)', marginTop: '8px', fontSize: '1rem', lineHeight: 1.5 }}>
              Trace how environmental observations become evidence-backed recommendations.
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

            <div style={{ background: 'var(--color-info-bg)', borderRadius: '12px', padding: '16px', display: 'flex', gap: '16px', alignItems: 'flex-start', width: '240px', position: 'relative', overflow: 'hidden', border: '1px solid rgba(59, 130, 246, 0.2)' }}>
              <div style={{ background: 'var(--color-info)', color: 'white', borderRadius: '50%', padding: '8px', display: 'flex', zIndex: 1 }}>
                <Network size={18} />
              </div>
              <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--color-primary-dark)', zIndex: 1, lineHeight: 1.4 }}>
                Transparent Logic<br/>Verified Science<br/>Trusted Actions
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


  

  // Gather variables
  const vars = [
    { name: 'Organic Carbon', value: safeVal(profile.soil?.organic_carbon) },
    { name: 'Moisture', value: safeVal(profile.soil?.moisture) },
    { name: 'Soil pH', value: safeVal(profile.soil?.soil_ph ?? profile.soil?.ph) },
    { name: 'Rainfall', value: safeVal(profile.climate?.rainfall) },
    { name: 'Temperature', value: safeVal(profile.climate?.temperature) },
    { name: 'Land Use', value: safeVal(profile.land?.use || profile.land?.land_use) },
    { name: 'Cropping System', value: safeVal(profile.land?.cropping_system) },
    { name: 'Species Richness', value: safeVal(profile.biodiversity?.species_richness) },
    { name: 'Habitat Diversity', value: safeVal(profile.biodiversity?.habitat_diversity) },
    { name: 'Pollution', value: safeVal(profile.human_impact?.pollution) },
    { name: 'Deforestation', value: safeVal(profile.human_impact?.deforestation) },
  ].filter(v => v.value !== 'Unknown');

  const pageRels = relationships?.relationships || [];
  const pageRisks = risks?.risk_patterns || [];
  const claims = recommendations?.recommendation?.claims || [];
  const rec = recommendations?.recommendation_available ? recommendations.recommendation : null;

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
            Evidence & Reasoning
          </h1>
          <p style={{ color: 'var(--color-text-secondary)', marginTop: '8px', fontSize: '1rem', lineHeight: 1.5 }}>
            Trace how environmental observations become evidence-backed recommendations.
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

          <div style={{ background: 'var(--color-info-bg)', borderRadius: '12px', padding: '16px', display: 'flex', gap: '16px', alignItems: 'flex-start', width: '240px', position: 'relative', overflow: 'hidden', border: '1px solid rgba(59, 130, 246, 0.2)' }}>
            <div style={{ background: 'var(--color-info)', color: 'white', borderRadius: '50%', padding: '8px', display: 'flex', zIndex: 1 }}>
              <Network size={18} />
            </div>
            <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--color-primary-dark)', zIndex: 1, lineHeight: 1.4 }}>
              Transparent Logic<br/>Verified Science<br/>Trusted Actions
            </div>
            <svg style={{ position: 'absolute', right: '-15px', top: '5px', opacity: 0.08, zIndex: 0, transform: 'rotate(15deg)' }} width="80" height="80" viewBox="0 0 24 24" fill="var(--color-info)">
              <path d="M16 11C17.66 11 19.99 11.89 20 13.5V17H12V13.5C12.01 11.89 14.34 11 16 11M8 11C9.66 11 11.99 11.89 12 13.5V17H4V13.5C4.01 11.89 6.34 11 8 11M8 9C6.9 9 6 8.1 6 7C6 5.9 6.9 5 8 5C9.1 5 10 5.9 10 7C10 8.1 9.1 9 8 9M16 9C14.9 9 14 8.1 14 7C14 5.9 14.9 5 16 5C17.1 5 18 5.9 18 7C18 8.1 17.1 9 16 9Z" />
            </svg>
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '40px', position: 'relative' }}>
        
        {/* Pipeline Line */}
        <div style={{ position: 'absolute', left: '32px', top: '32px', bottom: '32px', width: '2px', background: 'var(--color-border)', zIndex: 0 }}></div>

        {/* 1. ENVIRONMENTAL VARIABLES */}
        <div style={{ position: 'relative', zIndex: 1, paddingLeft: '80px' }}>
          <div style={{ position: 'absolute', left: '16px', top: '0', width: '32px', height: '32px', borderRadius: '50%', background: 'var(--color-primary-dark)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 'bold' }}>1</div>
          <h2 style={{ fontSize: '1.25rem', marginBottom: '16px', color: 'var(--color-primary-dark)' }}>ENVIRONMENTAL VARIABLES</h2>
          <div style={{ ...cardStyle, display: 'flex', flexWrap: 'wrap', gap: '12px' }}>
            {vars.map(v => (
              <div key={v.name} style={{ padding: '8px 16px', background: 'var(--color-surface-hover)', borderRadius: '20px', border: '1px solid var(--color-border)', fontSize: '0.9rem', display: 'flex', gap: '8px', alignItems: 'center' }}>
                <span style={{ color: 'var(--color-text-secondary)' }}>{v.name}</span>
                <span style={{ fontWeight: 600 }}>{v.value.replace(/_/g, ' ')}</span>
              </div>
            ))}
            {vars.length === 0 && <span style={{ color: 'var(--color-text-tertiary)' }}>No available variables found.</span>}
          </div>
        </div>

        {/* 2. MULTI-METRIC RELATIONSHIPS */}
        <div style={{ position: 'relative', zIndex: 1, paddingLeft: '80px' }}>
          <div style={{ position: 'absolute', left: '16px', top: '0', width: '32px', height: '32px', borderRadius: '50%', background: 'var(--color-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 'bold' }}>2</div>
          <h2 style={{ fontSize: '1.25rem', marginBottom: '16px', color: 'var(--color-primary-dark)' }}>MULTI-METRIC RELATIONSHIPS</h2>
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
            {pageRels.length === 0 && <div style={cardStyle}><p style={{ color: 'var(--color-text-tertiary)', margin: 0 }}>No relationships found.</p></div>}
          </div>
        </div>

        {/* 3. ENVIRONMENTAL RISKS */}
        <div style={{ position: 'relative', zIndex: 1, paddingLeft: '80px' }}>
          <div style={{ position: 'absolute', left: '16px', top: '0', width: '32px', height: '32px', borderRadius: '50%', background: 'var(--color-warning)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 'bold' }}>3</div>
          <h2 style={{ fontSize: '1.25rem', marginBottom: '16px', color: 'var(--color-primary-dark)' }}>ENVIRONMENTAL RISKS</h2>
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
            {pageRisks.length === 0 && <div style={cardStyle}><p style={{ color: 'var(--color-text-tertiary)', margin: 0 }}>No active risk patterns detected.</p></div>}
          </div>
        </div>

        {/* 4. SCIENTIFIC EVIDENCE */}
        <div style={{ position: 'relative', zIndex: 1, paddingLeft: '80px' }}>
          <div style={{ position: 'absolute', left: '16px', top: '0', width: '32px', height: '32px', borderRadius: '50%', background: 'var(--color-info)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 'bold' }}>4</div>
          <h2 style={{ fontSize: '1.25rem', marginBottom: '16px', color: 'var(--color-primary-dark)' }}>SCIENTIFIC EVIDENCE</h2>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {claims.length === 0 ? (
              <div style={cardStyle}><p style={{ fontSize: '0.9rem', color: 'var(--color-text-secondary)', margin: 0 }}>Claim could not be traced to verified scientific evidence.</p></div>
            ) : (
              claims.map(claim => (
                <div key={claim.claim_id} style={{ ...cardStyle, background: 'var(--color-info-bg)' }}>
                  <div style={{ display: 'flex', gap: '8px', marginBottom: '12px', alignItems: 'center' }}>
                    <Search size={16} color="var(--color-info)" />
                    <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--color-info)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Scientific Claim</span>
                  </div>
                  <p style={{ fontSize: '1rem', margin: '0 0 16px 0', color: 'var(--color-text-primary)', fontWeight: 500 }}>{claim.claim_text}</p>
                  <span style={{ ...badgeStyle(claim.support_status), padding: '4px 8px', borderRadius: '12px', fontSize: '0.75rem', fontWeight: 600, display: 'inline-block', marginBottom: '16px' }}>{(claim.support_status || 'unknown').toUpperCase()}</span>
                  
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', borderLeft: '2px solid var(--color-info)', paddingLeft: '16px', marginLeft: '8px' }}>
                    {(claim.evidence || []).map((ev, i) => (
                      <div key={i} style={{ background: 'white', padding: '16px', borderRadius: '12px', border: '1px solid var(--color-border)', boxShadow: '0 2px 4px rgba(0,0,0,0.02)' }}>
                        <div style={{ display: 'flex', gap: '6px', marginBottom: '8px', alignItems: 'center' }}>
                          <BookOpen size={14} color="var(--color-text-tertiary)" />
                          <span style={{ fontSize: '0.8rem', color: 'var(--color-text-tertiary)', textTransform: 'uppercase' }}>Document</span>
                        </div>
                        <span style={{ display: 'block', fontSize: '0.9rem', fontWeight: 500, marginBottom: '8px' }}>{ev.document || 'Unknown'}</span>
                        
                        <div style={{ display: 'flex', gap: '6px', marginBottom: '4px', alignItems: 'center' }}>
                          <span style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)' }}>Source: {ev.source || 'Unknown'}</span>
                        </div>
                        {ev.chunk_id && <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--color-text-tertiary)', marginBottom: '12px' }}>Chunk ID: {ev.chunk_id}</span>}
                        
                        {ev.url && (
                          <a href={ev.url} target="_blank" rel="noreferrer" style={{ fontSize: '0.85rem', color: 'var(--color-primary)', display: 'inline-flex', alignItems: 'center', gap: '6px', textDecoration: 'none', fontWeight: 600 }}>
                            <LinkIcon size={14} /> View Source
                          </a>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* 5. RECOMMENDATION */}
        <div style={{ position: 'relative', zIndex: 1, paddingLeft: '80px' }}>
          <div style={{ position: 'absolute', left: '16px', top: '0', width: '32px', height: '32px', borderRadius: '50%', background: 'var(--color-success)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontWeight: 'bold' }}>5</div>
          <h2 style={{ fontSize: '1.25rem', marginBottom: '16px', color: 'var(--color-primary-dark)' }}>RECOMMENDATION</h2>
          <div style={{ ...cardStyle, border: '1px solid var(--color-success)', boxShadow: '0 4px 12px rgba(34, 197, 94, 0.1)' }}>
            {!rec ? (
              <p style={{ fontSize: '0.9rem', color: 'var(--color-text-secondary)', margin: 0 }}>No recommendation available for the current data.</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                  <CheckCircle size={24} color="var(--color-success)" />
                  <span style={{ fontWeight: 700, color: 'var(--color-text-primary)', fontSize: '1.2rem' }}>{rec.what_to_do}</span>
                </div>
                <div>
                  <span style={{ display: 'block', fontSize: '0.85rem', color: 'var(--color-text-tertiary)', marginBottom: '4px' }}>Why it works</span>
                  <span style={{ fontSize: '0.95rem', color: 'var(--color-text-secondary)', lineHeight: 1.5 }}>{rec.why_it_works}</span>
                </div>
                {rec.environmental_mechanism && (
                  <div>
                    <span style={{ display: 'block', fontSize: '0.85rem', color: 'var(--color-text-tertiary)', marginBottom: '4px' }}>Environmental Mechanism</span>
                    <span style={{ fontSize: '0.9rem', color: 'var(--color-text-secondary)' }}>{rec.environmental_mechanism}</span>
                  </div>
                )}
                <div>
                  <span style={{ display: 'block', fontSize: '0.85rem', color: 'var(--color-text-tertiary)', marginBottom: '8px' }}>Impacted Metrics</span>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {rec.impacted_metrics?.direct?.map((m: string) => <span key={`d-${m}`} style={{ background: 'var(--color-success-bg)', color: 'var(--color-success)', padding: '4px 10px', borderRadius: '12px', fontSize: '0.8rem', fontWeight: 600 }}>{m.replace(/_/g, ' ')} (Direct)</span>)}
                    {rec.impacted_metrics?.indirect?.map((m: string) => <span key={`i-${m}`} style={{ background: 'var(--color-info-bg)', color: 'var(--color-info)', padding: '4px 10px', borderRadius: '12px', fontSize: '0.8rem', fontWeight: 600 }}>{m.replace(/_/g, ' ')} (Indirect)</span>)}
                  </div>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px', borderTop: '1px solid var(--color-border)', paddingTop: '16px', marginTop: '4px' }}>
                  <div>
                    <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--color-text-tertiary)' }}>Confidence</span>
                    <span style={{ fontSize: '0.9rem', fontWeight: 600 }}>{rec.confidence?.level || 'Unknown'}</span>
                  </div>
                  <div>
                    <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--color-text-tertiary)' }}>Time Horizon</span>
                    <span style={{ fontSize: '0.9rem', fontWeight: 600 }}>{rec.time_horizon?.estimate || 'Unknown'}</span>
                  </div>
                  <div>
                    <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--color-text-tertiary)' }}>Evidence</span>
                    <span style={{ fontSize: '0.9rem', fontWeight: 600 }}>{(rec.evidence_status || 'Unknown').replace(/_/g, ' ')}</span>
                  </div>
                </div>
                {rec.reasoning_trace && rec.reasoning_trace.length > 0 && (
                  <div style={{ borderTop: '1px solid var(--color-border)', paddingTop: '16px', marginTop: '4px' }}>
                    <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--color-text-tertiary)', marginBottom: '8px' }}>Reasoning Trace</span>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                      {rec.reasoning_trace.map((step, i) => (
                        <div key={i} style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)', display: 'flex', gap: '8px' }}>
                          <span style={{ color: 'var(--color-text-tertiary)' }}>{step.step}.</span>
                          <span>{step.type.replace(/_/g, ' ')}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
};
