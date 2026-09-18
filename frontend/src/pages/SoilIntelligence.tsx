import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useEnvironmentalData } from '../context/EnvironmentalContext';
import { 
  ArrowLeft, RefreshCw, FlaskConical, Droplets, MapPin, Search, 
  Activity, BookOpen, AlertTriangle, ShieldCheck, ChevronDown, ChevronUp, Link as LinkIcon
} from 'lucide-react';

// Extract value safely
const safeVal = (v: any): string => {
  if (v === null || v === undefined) return 'Unknown';
  if (typeof v === 'object' && 'value' in v) {
    return v.value !== null && v.value !== undefined ? String(v.value) : 'Unknown';
  }
  return String(v);
};

export const SoilIntelligence: React.FC = () => {
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
              Soil Intelligence
            </h1>
            <p style={{ color: 'var(--color-text-secondary)', marginTop: '8px', fontSize: '1rem', lineHeight: 1.5 }}>
              Understand the condition, drivers, and environmental role of your soil. Analyze soil indicators, identify potential soil pressures, understand relationships with vegetation and water, and explore evidence-backed environmental insights.
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
                <FlaskConical size={18} />
              </div>
              <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--color-primary-dark)', zIndex: 1, lineHeight: 1.4 }}>
                Accurate Soil Data<br/>Stronger Insights<br/>Healthier Ecosystems
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


  

  const oc = safeVal(profile.soil?.organic_carbon);
  const moist = safeVal(profile.soil?.moisture);
  const ph = safeVal(profile.soil?.soil_ph ?? profile.soil?.ph);
  
  const ocAnalysis = getMetricAnalysis('organic_carbon');
  const moistAnalysis = getMetricAnalysis('soil_moisture');
  const phAnalysis = getMetricAnalysis('soil_ph');

  const rawStatus = baseline?.summary?.soil_status && typeof baseline.summary.soil_status === 'object' ? baseline.summary.soil_status.status : baseline?.summary?.soil_status;
  let soilStatus = 'Unknown';
  if (rawStatus && rawStatus !== 'Unknown') {
    soilStatus = String(rawStatus);
  } else if (safeVal(profile.soil?.organic_carbon) !== 'Unknown' || safeVal(profile.soil?.moisture) !== 'Unknown' || safeVal(profile.soil?.ph) !== 'Unknown') {
    soilStatus = 'Context Dependent';
  }

  // Filter soil relationships
  const soilRels = (relationships?.relationships || []).filter(r => {
    const sources = r.source_variables || r.inputs || [];
    const target = r.target_variable || r.downstream_states?.[0]?.name || r.intermediate_states?.[0]?.name || '';
    return sources.some(v => v.toLowerCase().includes('soil') || v.toLowerCase().includes('carbon') || v.toLowerCase().includes('moisture') || v.toLowerCase().includes('ph')) ||
      target.toLowerCase().includes('soil');
  });

  // Filter soil risks
  const soilRisks = (risks?.risk_patterns || []).filter(r => {
    const vars = r.variables_used || [];
    return vars.some(v => v.toLowerCase().includes('soil') || v.toLowerCase().includes('carbon') || v.toLowerCase().includes('moisture') || v.toLowerCase().includes('ph'));
  });

  const claims = recommendations?.recommendation?.claims || [];
  const rec = recommendations?.recommendation_available ? recommendations.recommendation : null;

  return (
    <div className="main-content" style={{ width: '92%', margin: '0 auto', maxWidth: '1400px' }}>
      {/* Top Page Header */}
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
            Soil Intelligence
          </h1>
          <p style={{ color: 'var(--color-text-secondary)', marginTop: '8px', fontSize: '1rem', lineHeight: 1.5 }}>
            Understand the condition, drivers, and environmental role of your soil. Analyze soil indicators, identify potential soil pressures, understand relationships with vegetation and water, and explore evidence-backed environmental insights.
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
              <FlaskConical size={18} />
            </div>
            <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--color-primary-dark)', zIndex: 1, lineHeight: 1.4 }}>
              Accurate Soil Data<br/>Stronger Insights<br/>Healthier Ecosystems
            </div>
            <svg style={{ position: 'absolute', right: '-15px', top: '5px', opacity: 0.08, zIndex: 0, transform: 'rotate(15deg)' }} width="80" height="80" viewBox="0 0 24 24" fill="var(--color-success)">
              <path d="M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22A10,10 0 0,1 2,12A10,10 0 0,1 12,2Z" />
            </svg>
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '32px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
          
          {/* Soil Health Overview & Condition */}
          <div style={{ ...cardStyle, position: 'relative' }}>
            <div style={{ position: 'absolute', right: '-10px', top: '10px', opacity: 0.03, transform: 'scale(2.5)', pointerEvents: 'none' }}>
              <FlaskConical size={100} />
            </div>
            
            <h2 style={{ fontSize: '1.25rem', marginBottom: '24px', color: 'var(--color-primary-dark)' }}>Current Soil Condition</h2>
            
            <div style={{ display: 'flex', gap: '32px', alignItems: 'stretch' }}>
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', background: 'var(--color-surface-hover)', borderRadius: '12px', padding: '24px' }}>
                <span style={{ fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--color-text-secondary)', marginBottom: '8px' }}>Status</span>
                <span style={{ fontSize: '2.5rem', fontWeight: 800, color: soilStatus.toLowerCase().includes('optimal') ? 'var(--color-success)' : (soilStatus.toLowerCase().includes('critical') ? 'var(--color-danger)' : 'var(--color-warning)'), textTransform: 'uppercase', lineHeight: 1 }}>
                  {soilStatus.replace(/_/g, ' ')}
                </span>
              </div>
              
              <div style={{ flex: 2, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                <h3 style={{ fontSize: '1rem', marginBottom: '12px', color: 'var(--color-text-primary)' }}>Key Observations</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ color: 'var(--color-text-secondary)', display: 'flex', alignItems: 'center', gap: '8px' }}><FlaskConical size={16} color="var(--color-success)" /> Organic Carbon</span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <span style={{ fontWeight: 600 }}>{oc} %</span>
                      <span style={{ ...badgeStyle(ocAnalysis.status), padding: '4px 8px', borderRadius: '12px', fontSize: '0.75rem', fontWeight: 600 }}>{ocAnalysis.status.replace(/_/g, ' ').toUpperCase()}</span>
                    </div>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ color: 'var(--color-text-secondary)', display: 'flex', alignItems: 'center', gap: '8px' }}><Droplets size={16} color="var(--color-info)" /> Soil Moisture</span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <span style={{ fontWeight: 600 }}>{moist} %</span>
                      <span style={{ ...badgeStyle(moistAnalysis.status), padding: '4px 8px', borderRadius: '12px', fontSize: '0.75rem', fontWeight: 600 }}>{moistAnalysis.status.replace(/_/g, ' ').toUpperCase()}</span>
                    </div>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ color: 'var(--color-text-secondary)', display: 'flex', alignItems: 'center', gap: '8px' }}><Activity size={16} color="var(--color-warning)" /> Soil pH</span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <span style={{ fontWeight: 600 }}>{ph}</span>
                      <span style={{ ...badgeStyle(phAnalysis.status), padding: '4px 8px', borderRadius: '12px', fontSize: '0.75rem', fontWeight: 600 }}>{phAnalysis.status.replace(/_/g, ' ').toUpperCase()}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Relationships */}
          <div>
            <h2 style={{ fontSize: '1.25rem', marginBottom: '16px', color: 'var(--color-primary-dark)' }}>Soil & Environmental Relationships</h2>
            {soilRels.length === 0 ? (
              <div style={cardStyle}><p style={{ color: 'var(--color-text-tertiary)', margin: 0 }}>No relationships found for current data.</p></div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {soilRels.map(r => (
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

          {/* Risks */}
          <div>
            <h2 style={{ fontSize: '1.25rem', marginBottom: '16px', color: 'var(--color-primary-dark)' }}>Soil Risk Patterns</h2>
            {soilRisks.length === 0 ? (
              <div style={cardStyle}><p style={{ color: 'var(--color-text-tertiary)', margin: 0 }}>No active risk patterns detected for current soil data.</p></div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {soilRisks.map(r => (
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

        {/* Right Sidebar panels */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
          
          <div style={{ ...cardStyle, background: 'var(--color-surface-hover)' }}>
            <h3 style={{ fontSize: '1.1rem', color: 'var(--color-primary-dark)', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <BookOpen size={20} /> SOIL INTELLIGENCE
            </h3>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div>
                <span style={{ display: 'block', fontSize: '0.85rem', color: 'var(--color-text-tertiary)', marginBottom: '4px' }}>Current Condition</span>
                <span style={{ fontWeight: 600, color: 'var(--color-text-primary)' }}>{soilStatus.replace(/_/g, ' ').toUpperCase()}</span>
              </div>
              
              <div>
                <span style={{ display: 'block', fontSize: '0.85rem', color: 'var(--color-text-tertiary)', marginBottom: '4px' }}>Key Indicators</span>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  <span style={{ background: 'white', padding: '4px 10px', borderRadius: '12px', fontSize: '0.8rem', border: '1px solid var(--color-border)' }}>Organic Carbon</span>
                  <span style={{ background: 'white', padding: '4px 10px', borderRadius: '12px', fontSize: '0.8rem', border: '1px solid var(--color-border)' }}>Moisture</span>
                  <span style={{ background: 'white', padding: '4px 10px', borderRadius: '12px', fontSize: '0.8rem', border: '1px solid var(--color-border)' }}>Soil pH</span>
                </div>
              </div>

              {soilRels.length > 0 && (
                <div>
                  <span style={{ display: 'block', fontSize: '0.85rem', color: 'var(--color-text-tertiary)', marginBottom: '4px' }}>Environmental Links</span>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {Array.from(new Set(soilRels.map(r => r.target_variable || r.downstream_states?.[0]?.name || r.intermediate_states?.[0]?.name || '').filter(Boolean))).slice(0, 3).map((link, i) => (
                      <span key={i} style={{ background: 'white', padding: '4px 10px', borderRadius: '12px', fontSize: '0.8rem', border: '1px solid var(--color-border)' }}>{link.replace(/_/g, ' ')}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          <div style={cardStyle}>
            <h3 style={{ fontSize: '1.1rem', color: 'var(--color-primary-dark)', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <LinkIcon size={20} /> Recommended Action
            </h3>
            
            {!rec ? (
              <p style={{ fontSize: '0.9rem', color: 'var(--color-text-secondary)', margin: 0 }}>No recommendation available for the current data.</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div>
                  <span style={{ display: 'block', fontSize: '0.85rem', color: 'var(--color-text-tertiary)', marginBottom: '4px' }}>What to do</span>
                  <span style={{ fontWeight: 600, color: 'var(--color-text-primary)', fontSize: '0.95rem' }}>{rec.what_to_do}</span>
                </div>
                <div>
                  <span style={{ display: 'block', fontSize: '0.85rem', color: 'var(--color-text-tertiary)', marginBottom: '4px' }}>Why it works</span>
                  <span style={{ fontSize: '0.9rem', color: 'var(--color-text-secondary)' }}>{rec.why_it_works}</span>
                </div>
                <div>
                  <span style={{ display: 'block', fontSize: '0.85rem', color: 'var(--color-text-tertiary)', marginBottom: '4px' }}>Potentially affected</span>
                  <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '0.85rem', color: 'var(--color-text-secondary)' }}>
                    {rec.impacted_metrics?.direct?.map((m: string) => <li key={`d-${m}`}>{m.replace(/_/g, ' ')} (Direct)</li>)}
                    {rec.impacted_metrics?.indirect?.map((m: string) => <li key={`i-${m}`}>{m.replace(/_/g, ' ')} (Indirect)</li>)}
                  </ul>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid var(--color-border)', paddingTop: '12px', marginTop: '8px' }}>
                  <div>
                    <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--color-text-tertiary)' }}>Confidence</span>
                    <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>{rec.confidence?.level || 'Unknown'}</span>
                  </div>
                  <div>
                    <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--color-text-tertiary)' }}>Time Horizon</span>
                    <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>{rec.time_horizon?.estimate || 'Unknown'}</span>
                  </div>
                </div>
              </div>
            )}
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
