import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useEnvironmentalData } from '../context/EnvironmentalContext';
import { MetricCard } from '../components/MetricCard';
import { RiskCard } from '../components/RiskCard';
import { Droplets, Trees, Leaf, Maximize2, ChevronRight, Sprout, CloudRain, Calendar as CalendarIcon, Search as SearchIcon, ArrowRight, Clock, Map as MapIcon, RefreshCw } from 'lucide-react';

// Custom icons
const Lightning = ({size}: {size: number}) => <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>;
const DownloadIcon = ({size}: {size: number}) => <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>;

export const DashboardOverview: React.FC = () => {
  const { profileId, profile, baseline, risks, loading, error } = useEnvironmentalData();
  const navigate = useNavigate();
  const [riskFilter, setRiskFilter] = useState('All Risks');

  
  if (loading || !profile) {
    return (
      <div className="main-content" style={{ width: '92%', margin: '0 auto', maxWidth: '1400px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
          <div>
            <h1 style={{ margin: 0, fontSize: '2rem', color: 'var(--color-primary-dark)', fontWeight: 700, letterSpacing: '-0.02em' }}>
              EcoMind AI Overview
            </h1>
            <p style={{ color: 'var(--color-text-secondary)', marginTop: '8px', fontSize: '1rem' }}>
              Real-time environmental intelligence and risk monitoring for Profile #{profileId}.
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
            <button 
              type="button" 
              onClick={() => navigate('/environment')}
              style={{ 
                display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 20px',
                background: 'var(--color-primary)', border: 'none',
                borderRadius: '8px', color: 'white', fontWeight: 600, cursor: 'pointer',
                boxShadow: 'var(--shadow-sm)'
              }}
            >
              Update Environmental Data
            </button>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '24px', marginBottom: '32px' }}>
          <div className="skeleton-box" style={{ height: '140px', borderRadius: '16px' }}></div>
          <div className="skeleton-box" style={{ height: '140px', borderRadius: '16px' }}></div>
          <div className="skeleton-box" style={{ height: '140px', borderRadius: '16px' }}></div>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '32px' }}>
          <div className="skeleton-box" style={{ height: '400px', borderRadius: '16px' }}></div>
          <div className="skeleton-box" style={{ height: '400px', borderRadius: '16px' }}></div>
        </div>
      </div>
    );
  }


  if (error) {
    return <div className="main-content"><div className="card badge-danger">{error}</div></div>;
  }

  

  const filteredRisks = risks?.risk_patterns?.filter(risk => {
    if (riskFilter === 'All Risks') return true;
    const nameLower = risk.name.toLowerCase();
    if (riskFilter === 'Biodiversity' && nameLower.includes('biodiversity')) return true;
    if (riskFilter === 'Water' && (nameLower.includes('water') || nameLower.includes('moisture'))) return true;
    if (riskFilter === 'Soil' && nameLower.includes('soil')) return true;
    if (riskFilter === 'Land' && (nameLower.includes('habitat') || nameLower.includes('land'))) return true;
    if (riskFilter === 'Human Impact' && nameLower.includes('human')) return true;
    return false;
  }) || [];


  const safeValStr = (v: any): string => {
    if (v === null || v === undefined) return 'Unknown';
    if (typeof v === 'object' && 'value' in v) return v.value !== null && v.value !== undefined ? String(v.value) : 'Unknown';
    return String(v);
  };

  const getStatus = (field: string, deps: string[]) => {
    const rawStatus = baseline?.summary?.[field] && typeof baseline.summary[field] === 'object' ? baseline.summary[field].status : baseline?.summary?.[field];
    if (rawStatus && rawStatus !== 'Unknown') return String(rawStatus);
    const hasDeps = deps.some(d => {
      const parts = d.split('.');
      let val: any = profile;
      for (const p of parts) val = val?.[p];
      return safeValStr(val) !== 'Unknown';
    });
    return hasDeps ? 'Context Dependent' : 'Unknown';
  };

  const soilStatus = getStatus('soil_status', ['soil.organic_carbon', 'soil.moisture', 'soil.ph']);
  const waterStatus = getStatus('water_status', ['climate.rainfall', 'climate.temperature']);
  const habitatStatus = getStatus('habitat_status', ['biodiversity.species_richness', 'biodiversity.habitat_diversity']);

  return (
    <>
      <div className="main-content">
        {/* Hero Section */}
        <div className="hero-card">
          <div className="hero-content">
            <div className="hero-label">
              <Leaf size={14} /> ENVIRONMENTAL INTELLIGENCE
            </div>
            <h1 className="hero-title">
              Observe Today,<br/>
              <span>Sustain Tomorrow.</span>
            </h1>
            <p className="hero-subtitle">
              Integrated AI-driven analysis for a healthier planet. Explore environmental risks, relationships and actionable insights — all in one place.
            </p>
          </div>
          <div className="hero-image-wrapper">
            <div className="hero-image" style={{ background: 'linear-gradient(135deg, var(--color-primary-light), var(--color-primary-dark))' }}>
              <img 
                src="https://images.unsplash.com/photo-1501854140801-50d01698950b?q=80&w=1200&auto=format&fit=crop" 
                alt="" 
                onError={(e) => { e.currentTarget.style.display = 'none'; }}
              />
            </div>
          </div>
          <div className="hero-overlay-card">
            <div style={{ background: 'var(--color-success-bg)', color: 'var(--color-success)', padding: '10px', borderRadius: '50%' }}>
              <Leaf size={24} />
            </div>
            <div style={{fontWeight: 600, fontSize: '1.05rem', lineHeight: 1.3}}>
              Turning Data into<br/>a Greener Future
            </div>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="section-header">
          <div>
            <h2 className="section-title">Key Metrics</h2>
            <p className="section-subtitle">Real-time indicators for the selected region</p>
          </div>
          
        </div>
        
        <div className="grid-cols-3" style={{ marginBottom: '48px' }}>
          <MetricCard 
            title="Soil Organic Carbon" 
            icon={<Leaf size={20} color="var(--color-success)" />}
            observation={profile.soil?.organic_carbon} 
            analysis={baseline?.metrics['organic_carbon']} 
            unit="%"
            tooltipText="Soil organic carbon (SOC) is a measurable component of soil organic matter. Crucial for soil health and carbon sequestration."
          />
          <MetricCard 
            title="Rainfall" 
            icon={<Droplets size={20} color="var(--color-info)" />}
            observation={profile.climate?.rainfall} 
            analysis={baseline?.metrics['rainfall']} 
            unit="mm"
            tooltipText="Total precipitation measured in millimeters. Affects soil moisture, vegetation growth, and erosion rates."
          />
          <MetricCard 
            title="Species Richness" 
            icon={<Trees size={20} color="var(--color-success)" />}
            observation={profile.biodiversity?.species_richness} 
            analysis={baseline?.metrics['species_richness']} 
            tooltipText="The number of different species represented in the ecological community. Higher richness indicates better biodiversity."
          />

        </div>

        {/* System Status Summary */}
        <div className="section-header">
          <div>
            <h2 className="section-title">System Status</h2>
            <p className="section-subtitle">Current status across key environmental systems</p>
          </div>
        </div>
        
        <div className="grid-cols-3" style={{ marginBottom: '48px' }}>
          <div className="card status-card" onClick={() => navigate('/soil')} role="button" tabIndex={0} style={{ borderLeft: `4px solid var(--color-${soilStatus.toLowerCase().includes('optimal') ? 'success' : 'warning'})` }}>
            <div className="status-icon-wrapper" style={{ background: 'var(--color-warning-bg)', color: 'var(--color-warning)' }}>
              <Sprout size={28} />
            </div>
            <div style={{ flex: 1 }}>
              <h3 style={{ fontSize: '0.9rem', color: 'var(--color-text-secondary)', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Soil System</h3>
              <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--color-primary-dark)' }}>
                {soilStatus.replace(/_/g, ' ')}
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--color-text-tertiary)', marginTop: '4px' }}>Degraded organic carbon levels detected</div>
            </div>
            <ArrowRight size={20} className="chevron-right" />
          </div>
          
          <div className="card status-card" onClick={() => navigate('/climate')} role="button" tabIndex={0} style={{ borderLeft: `4px solid var(--color-${waterStatus.toLowerCase().includes('optimal') ? 'success' : 'warning'})` }}>
            <div className="status-icon-wrapper" style={{ background: 'var(--color-info-bg)', color: 'var(--color-info)' }}>
              <Droplets size={28} />
            </div>
            <div style={{ flex: 1 }}>
              <h3 style={{ fontSize: '0.9rem', color: 'var(--color-text-secondary)', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Water System</h3>
              <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--color-primary-dark)' }}>
                {waterStatus.replace(/_/g, ' ')}
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--color-text-tertiary)', marginTop: '4px' }}>Seasonal variability observed</div>
            </div>
            <ArrowRight size={20} className="chevron-right" />
          </div>

          <div className="card status-card" onClick={() => navigate('/biodiversity')} role="button" tabIndex={0} style={{ borderLeft: `4px solid var(--color-${habitatStatus.toLowerCase().includes('optimal') ? 'success' : 'warning'})` }}>
            <div className="status-icon-wrapper" style={{ background: 'var(--color-success-bg)', color: 'var(--color-success)' }}>
              <Leaf size={28} />
            </div>
            <div style={{ flex: 1 }}>
              <h3 style={{ fontSize: '0.9rem', color: 'var(--color-text-secondary)', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Habitat System</h3>
              <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--color-primary-dark)' }}>
                {habitatStatus.replace(/_/g, ' ')}
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--color-text-tertiary)', marginTop: '4px' }}>Lower habitat diversity in region</div>
            </div>
            <ArrowRight size={20} className="chevron-right" />
          </div>
        </div>

        {/* Main Dashboard Layout */}
        <div className="dashboard-layout">
          {/* LEFT: Active Risk Patterns */}
          <div>
            <div className="section-header">
              <div>
                <h2 className="section-title">Active Risk Patterns</h2>
                <p className="section-subtitle">AI-identified environmental risks based on data relationships</p>
              </div>
              <select 
                className="select-input"
                value={riskFilter}
                onChange={(e) => setRiskFilter(e.target.value)}
                aria-label="Filter risks"
              >
                <option value="All Risks">All Risks</option>
                <option value="Biodiversity">Biodiversity</option>
                <option value="Water">Water</option>
                <option value="Soil">Soil</option>
                <option value="Land">Land</option>
                <option value="Human Impact">Human Impact</option>
              </select>
            </div>
            
            {(!filteredRisks || filteredRisks.length === 0) ? (
              <div className="card" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '120px' }}>
                <p style={{ color: 'var(--color-text-tertiary)' }}>No active risk patterns detected for this filter.</p>
              </div>
            ) : (
              <div>
                {filteredRisks.map(risk => (
                  <RiskCard key={risk.risk_pattern_id} risk={risk} />
                ))}
              </div>
            )}
          </div>
          
          {/* RIGHT: Regional Context & Quick Insights */}
          <div>
            {/* Regional Context */}
            <div className="section-header">
              <h2 className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <SearchIcon size={20} color="var(--color-secondary)" /> Regional Context
              </h2>
            </div>
            <div className="card" style={{ padding: '24px' }}>
              <div className="map-card" style={{ background: 'var(--color-surface-hover)' }}>
                <img 
                  src="https://images.unsplash.com/photo-1524661135-423995f22d0b?q=80&w=800&auto=format&fit=crop" 
                  alt="" 
                  onError={(e) => { e.currentTarget.style.display = 'none'; }}
                />
                <div className="map-meta-badge">
                  <MapIcon size={12} style={{ display: 'inline', marginRight: '4px' }} />
                  Spatial Data Active
                </div>
                <div className="map-overlay">
                  <button className="map-fullscreen-btn" aria-label="View Full Map" onClick={() => navigate('/environment')}>
                    <Maximize2 size={20} />
                  </button>
                </div>
              </div>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', fontSize: '0.9rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--color-border)', paddingBottom: '10px' }}>
                  <span style={{ color: 'var(--color-text-tertiary)' }}>Region</span>
                  <span style={{ color: 'var(--color-text-secondary)', fontWeight: 600 }}>{profile.location?.region || 'Semi-Arid Agricultural Zone'}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--color-border)', paddingBottom: '10px' }}>
                  <span style={{ color: 'var(--color-text-tertiary)' }}>Area</span>
                  <span style={{ color: 'var(--color-text-secondary)', fontWeight: 600 }}>63.12 km²</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--color-border)', paddingBottom: '10px' }}>
                  <span style={{ color: 'var(--color-text-tertiary)' }}>Data Sources</span>
                  <span style={{ color: 'var(--color-text-secondary)', fontWeight: 600 }}>Sentinel-2, Copernicus</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ color: 'var(--color-text-tertiary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Clock size={14} /> Last Updated
                  </span>
                  <span style={{ color: 'var(--color-success)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--color-success)' }}></span>
                    Sep 16, 2026
                  </span>
                </div>
              </div>
              
              <button className="btn-outline-primary" style={{ marginTop: '20px' }} onClick={() => navigate('/environment')}>
                View Full Map <ArrowRight size={16} />
              </button>
            </div>

            {/* Quick Insights */}
            <div className="section-header" style={{ marginTop: '32px' }}>
              <h2 className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Lightning size={20} /> Quick Insights
              </h2>
            </div>
            
            <div className="insight-row" onClick={() => navigate('/soil')}>
              <div className="insight-icon" style={{ color: 'var(--color-success)', background: 'var(--color-success-bg)' }}>
                <Leaf size={18} />
              </div>
              <div className="insight-text">Low soil organic carbon may limit vegetation growth.</div>
              <ChevronRight size={18} className="chevron-right" />
            </div>
            
            <div className="insight-row" onClick={() => navigate('/climate')}>
              <div className="insight-icon" style={{ color: 'var(--color-info)', background: 'var(--color-info-bg)' }}>
                <CloudRain size={18} />
              </div>
              <div className="insight-text">Rainfall variability increases ecosystem vulnerability.</div>
              <ChevronRight size={18} className="chevron-right" />
            </div>
            
            <div className="insight-row" onClick={() => navigate('/biodiversity')}>
              <div className="insight-icon" style={{ color: 'var(--color-primary)', background: 'var(--color-success-bg)' }}>
                <Trees size={18} />
              </div>
              <div className="insight-text">Habitat simplification reduces species resilience.</div>
              <ChevronRight size={18} className="chevron-right" />
            </div>
            
            <div className="insight-row" onClick={() => navigate('/reasoning')}>
              <div className="insight-icon" style={{ color: 'var(--color-success)', background: 'var(--color-success-bg)' }}>
                <Sprout size={18} />
              </div>
              <div className="insight-text">Integrated management can improve ecological balance.</div>
              <ChevronRight size={18} className="chevron-right" />
            </div>
          </div>
        </div>
      </div>
    </>
  );
};
