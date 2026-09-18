import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useEnvironmentalData } from '../context/EnvironmentalContext';
import { EnvironmentalService } from '../api/environmentalService';
import type { EnvironmentalObservationCreate } from '../types';
import { 
  FlaskConical, 
  CloudRain, 
  Map as MapIcon, 
  Trees, 
  Users, 
  Save, 
  CheckCircle2, 
  AlertCircle, 
  ArrowLeft,
  RefreshCw,
  Leaf
} from 'lucide-react';

interface FormValues {
  // Soil
  organic_carbon: string;
  moisture: string;
  soil_ph: string;
  // Climate
  rainfall: string;
  temperature: string;
  // Land
  land_use: string;
  crop: string;
  cropping_system: string;
  // Biodiversity
  species_richness: string;
  habitat_diversity: string;
  // Human Impact
  pollution: string;
  deforestation: string;
  // Location & Metadata
  region: string;
  source_name: string;
  data_quality: string;
}

const safeString = (val: any): string => {
  if (val === null || val === undefined) return '';
  if (typeof val === 'object' && 'value' in val) return val.value !== null && val.value !== undefined ? String(val.value) : '';
  return String(val);
};

export const EnvironmentalData: React.FC = () => {
  const { profileId, profile, loading, isFetching, refresh } = useEnvironmentalData();
  const navigate = useNavigate();

  const [formData, setFormData] = useState<FormValues>({
    organic_carbon: '', moisture: '', soil_ph: '',
    rainfall: '', temperature: '',
    land_use: '', crop: '', cropping_system: '',
    species_richness: '', habitat_diversity: '',
    pollution: '', deforestation: '',
    region: '', source_name: '', data_quality: '',
  });

  const [saving, setSaving] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (profile) {
      setFormData({
        organic_carbon: safeString(profile.soil?.organic_carbon),
        moisture: safeString(profile.soil?.moisture),
        soil_ph: safeString(profile.soil?.soil_ph ?? profile.soil?.ph),
        rainfall: safeString(profile.climate?.rainfall),
        temperature: safeString(profile.climate?.temperature),
        land_use: safeString(profile.land?.land_use ?? profile.land?.use ?? profile.land_use?.use),
        crop: safeString(profile.land?.crop ?? profile.land_use?.crop),
        cropping_system: safeString(profile.land?.cropping_system ?? profile.land_use?.cropping_system),
        species_richness: safeString(profile.biodiversity?.species_richness),
        habitat_diversity: safeString(profile.biodiversity?.habitat_diversity),
        pollution: safeString(profile.human_impact?.pollution),
        deforestation: safeString(profile.human_impact?.deforestation),
        region: safeString(profile.location?.region),
        source_name: safeString(profile.source_name),
        data_quality: safeString(profile.data_quality),
      });
    }
  }, [profile]);

  const handleChange = (field: keyof FormValues, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (validationErrors[field]) {
      setValidationErrors(prev => {
        const copy = { ...prev };
        delete copy[field];
        return copy;
      });
    }
  };

  const validate = (): boolean => {
    const errors: Record<string, string> = {};

    if (formData.soil_ph.trim() !== '') {
      const ph = parseFloat(formData.soil_ph);
      if (isNaN(ph) || ph < 0 || ph > 14) {
        errors.soil_ph = 'Soil pH must be between 0.0 and 14.0';
      }
    }

    if (formData.organic_carbon.trim() !== '') {
      const soc = parseFloat(formData.organic_carbon);
      if (isNaN(soc) || soc < 0) {
        errors.organic_carbon = 'Organic carbon must be a non-negative percentage';
      }
    }

    if (formData.rainfall.trim() !== '') {
      const rain = parseFloat(formData.rainfall);
      if (isNaN(rain) || rain < 0) {
        errors.rainfall = 'Rainfall must be a non-negative value (mm)';
      }
    }

    if (formData.moisture.trim() !== '') {
      const moisture = parseFloat(formData.moisture);
      if (isNaN(moisture) || moisture < 0 || moisture > 100) {
        errors.moisture = 'Soil moisture must be a valid percentage between 0.0% and 100.0%';
      }
    }

    if (formData.temperature.trim() !== '') {
      const temp = parseFloat(formData.temperature);
      if (isNaN(temp)) {
        errors.temperature = 'Temperature must be a valid number';
      }
    }

    if (formData.species_richness.trim() !== '') {
      const count = parseInt(formData.species_richness, 10);
      if (isNaN(count) || count < 0) {
        errors.species_richness = 'Species richness must be a non-negative integer';
      }
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSuccessMessage(null);
    setErrorMessage(null);

    if (!validate()) {
      setErrorMessage('Please correct the validation errors below before saving.');
      return;
    }

    setSaving(true);
    try {
      const parseNum = (val: string): number | undefined => {
        const trimmed = val.trim();
        return trimmed !== '' ? parseFloat(trimmed) : undefined;
      };

      const parseIntNum = (val: string): number | undefined => {
        const trimmed = val.trim();
        return trimmed !== '' ? parseInt(trimmed, 10) : undefined;
      };

      const parseStr = (val: string): string | undefined => {
        const trimmed = val.trim();
        return trimmed !== '' ? trimmed : undefined;
      };

      const payload: EnvironmentalObservationCreate = {
        soil: {
          organic_carbon: parseNum(formData.organic_carbon),
          moisture: parseNum(formData.moisture),
          soil_ph: parseNum(formData.soil_ph),
        },
        climate: {
          rainfall: parseNum(formData.rainfall),
          temperature: parseNum(formData.temperature),
        },
        land: {
          land_use: parseStr(formData.land_use),
          crop: parseStr(formData.crop),
          cropping_system: parseStr(formData.cropping_system),
        },
        biodiversity: {
          species_richness: parseIntNum(formData.species_richness),
          habitat_diversity: parseStr(formData.habitat_diversity),
        },
        human_impact: {
          pollution: parseStr(formData.pollution),
          deforestation: parseStr(formData.deforestation),
        },
        location: parseStr(formData.region) ? {
          latitude: profile?.location?.latitude ?? 0.0,
          longitude: profile?.location?.longitude ?? 0.0,
          region: parseStr(formData.region),
        } : undefined,
        source_name: parseStr(formData.source_name) ?? 'User Observation Form',
        source_type: 'Field Observation',
        data_quality: parseStr(formData.data_quality) ?? 'Direct Input',
        confidence: 1.0,
        observed_at: new Date().toISOString(),
      };

      await EnvironmentalService.updateProfile(profileId, payload);
      refresh();
      setSuccessMessage(`Environmental observations for Profile #${profileId} successfully saved and downstream pipeline updated!`);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to save environmental observations.');
    } finally {
      setSaving(false);
    }
  };

  const inputStyle = {
    width: '100%', 
    height: '42px',
    padding: '10px 14px', 
    border: '1px solid var(--color-border)', 
    borderRadius: '8px', 
    fontSize: '0.95rem',
    color: 'var(--color-text-primary)',
    transition: 'border-color var(--transition-fast), box-shadow var(--transition-fast)',
    outline: 'none',
    backgroundColor: '#ffffff'
  };

  const labelStyle = {
    display: 'block', 
    fontSize: '0.85rem', 
    fontWeight: 600, 
    marginBottom: '8px', 
    color: 'var(--color-text-secondary)'
  };

  const cardStyle = {
    background: '#ffffff',
    border: '1px solid var(--color-border)',
    borderRadius: '16px',
    padding: '32px',
    marginBottom: '24px',
    boxShadow: 'var(--shadow-sm)',
    position: 'relative' as const,
    overflow: 'hidden' as const,
    transition: 'box-shadow var(--transition-normal)'
  };

  return (
    <>
      <div className="main-content" style={{ width: '92%', margin: '0 auto', maxWidth: '1400px' }}>
      {/* Header */}
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
          <h1 style={{ margin: 0, fontSize: '2rem', color: 'var(--color-primary-dark)', fontWeight: 700, letterSpacing: '-0.02em' }}>
            Environmental Observations
          </h1>
          <p style={{ color: 'var(--color-text-secondary)', marginTop: '8px', fontSize: '1rem', lineHeight: 1.5 }}>
            Enter or update real environmental metrics for Profile #{profileId}. All downstream baseline analysis, relationships, risks, and recommendations re-evaluate automatically.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-start' }}>
          <button 
            type="button" 
            onClick={refresh} 
            disabled={isFetching || saving}
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
              <Leaf size={18} />
            </div>
            <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--color-primary-dark)', zIndex: 1, lineHeight: 1.4 }}>
              Accurate Data<br/>Stronger Insights<br/>A Healthier Planet
            </div>
            <svg style={{ position: 'absolute', right: '-15px', top: '5px', opacity: 0.08, zIndex: 0, transform: 'rotate(15deg)' }} width="80" height="80" viewBox="0 0 24 24" fill="var(--color-success)">
              <path d="M17.8,2.7C17.8,2.7 13.9,2 10.7,4.8C9.6,5.8 8.9,7 8.5,8.1C6.7,7.2 4.6,7 2.6,7.6C2.6,7.6 2.5,12.5 5.5,15.7C7.6,18 10.2,18.8 12.3,18.9C13,21.5 15,22.8 15,22.8C15,22.8 15.9,21 15.5,18.9C18.1,17.9 20,15.2 20.3,12C20.7,7.8 17.8,2.7 17.8,2.7M14.6,13.6C12.9,15.2 9.5,15.5 9.5,15.5C9.5,15.5 10.5,12.2 12.1,10.6C13.8,8.9 17.3,8.7 17.3,8.7C17.3,8.7 16.3,12 14.6,13.6Z" />
            </svg>
          </div>
        </div>
      </div>

      {/* Notifications */}
      {successMessage && (
        <div style={{ padding: '16px 20px', background: 'var(--color-success-bg)', color: 'var(--color-success-dark)', borderRadius: '12px', marginBottom: '24px', border: '1px solid rgba(34, 197, 94, 0.2)', display: 'flex', alignItems: 'center', gap: '12px' }}>
          <CheckCircle2 size={24} color="var(--color-success)" />
          <div style={{ flex: 1, fontWeight: 500, fontSize: '0.95rem' }}>{successMessage}</div>
        </div>
      )}

      {errorMessage && (
        <div style={{ padding: '16px 20px', background: 'var(--color-danger-bg)', color: 'var(--color-danger)', borderRadius: '12px', marginBottom: '24px', border: '1px solid rgba(239, 68, 68, 0.2)', display: 'flex', alignItems: 'center', gap: '12px' }}>
          <AlertCircle size={24} />
          <div style={{ flex: 1, fontWeight: 500, fontSize: '0.95rem' }}>{errorMessage}</div>
        </div>
      )}

      <form onSubmit={handleSubmit} noValidate style={{ position: 'relative', zIndex: 10 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>

          {/* Section 1: Soil */}
          <div className="form-card" style={cardStyle} onMouseOver={(e) => e.currentTarget.style.boxShadow = 'var(--shadow-md)'} onMouseOut={(e) => e.currentTarget.style.boxShadow = 'var(--shadow-sm)'}>
            <div style={{ position: 'absolute', right: '-20px', top: '20px', opacity: 0.04, transform: 'scale(2.5) rotate(-15deg)', pointerEvents: 'none' }}>
              <FlaskConical size={100} />
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
              <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
                <div style={{ background: '#dcfce7', padding: '16px', borderRadius: '16px', display: 'flex' }}>
                  <FlaskConical size={28} color="#16a34a" />
                </div>
                <div>
                  <h2 style={{ fontSize: '1.25rem', margin: '0 0 6px 0', color: 'var(--color-primary-dark)' }}>Soil Characteristics</h2>
                  <p style={{ fontSize: '0.9rem', color: 'var(--color-text-secondary)', margin: 0 }}>Key indicators of soil health and quality</p>
                </div>
              </div>
              <div style={{ background: '#dcfce7', color: '#16a34a', padding: '6px 14px', borderRadius: '20px', fontSize: '0.85rem', fontWeight: 600, border: '1px solid rgba(22, 163, 74, 0.2)' }}>
                Healthy Range
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '32px' }}>
              <div>
                <label style={labelStyle}>Soil Organic Carbon (%)</label>
                <input type="number" step="0.01" min="0" placeholder="e.g. 0.3" style={inputStyle} value={formData.organic_carbon} onChange={(e) => handleChange('organic_carbon', e.target.value)}
                  onFocus={(e) => { e.currentTarget.style.borderColor = 'var(--color-primary)'; e.currentTarget.style.boxShadow = '0 0 0 2px rgba(30, 63, 51, 0.1)'; }}
                  onBlur={(e) => { e.currentTarget.style.borderColor = 'var(--color-border)'; e.currentTarget.style.boxShadow = 'none'; }}
                />
                {validationErrors.organic_carbon && <span style={{ color: 'var(--color-danger)', fontSize: '0.8rem', marginTop: '6px', display: 'block' }}>{validationErrors.organic_carbon}</span>}
                <span style={{ fontSize: '0.75rem', color: 'var(--color-text-tertiary)', marginTop: '8px', display: 'block', fontWeight: 500 }}>Target: &gt; 1.0% in arable land</span>
              </div>
              <div>
                <label style={labelStyle}>Soil Moisture (%)</label>
                <input type="number" step="0.1" min="0" max="100" placeholder="e.g. 18.0" style={inputStyle} value={formData.moisture} onChange={(e) => handleChange('moisture', e.target.value)}
                  onFocus={(e) => { e.currentTarget.style.borderColor = 'var(--color-primary)'; e.currentTarget.style.boxShadow = '0 0 0 2px rgba(30, 63, 51, 0.1)'; }}
                  onBlur={(e) => { e.currentTarget.style.borderColor = 'var(--color-border)'; e.currentTarget.style.boxShadow = 'none'; }}
                />
                {validationErrors.moisture && <span style={{ color: 'var(--color-danger)', fontSize: '0.8rem', marginTop: '6px', display: 'block' }}>{validationErrors.moisture}</span>}
              </div>
              <div>
                <label style={labelStyle}>Soil pH (0.0 – 14.0)</label>
                <input type="number" step="0.1" min="0" max="14" placeholder="e.g. 6.2" style={inputStyle} value={formData.soil_ph} onChange={(e) => handleChange('soil_ph', e.target.value)}
                  onFocus={(e) => { e.currentTarget.style.borderColor = 'var(--color-primary)'; e.currentTarget.style.boxShadow = '0 0 0 2px rgba(30, 63, 51, 0.1)'; }}
                  onBlur={(e) => { e.currentTarget.style.borderColor = 'var(--color-border)'; e.currentTarget.style.boxShadow = 'none'; }}
                />
                {validationErrors.soil_ph && <span style={{ color: 'var(--color-danger)', fontSize: '0.8rem', marginTop: '6px', display: 'block' }}>{validationErrors.soil_ph}</span>}
              </div>
            </div>
          </div>

          {/* Section 2: Climate */}
          <div className="form-card" style={cardStyle} onMouseOver={(e) => e.currentTarget.style.boxShadow = 'var(--shadow-md)'} onMouseOut={(e) => e.currentTarget.style.boxShadow = 'var(--shadow-sm)'}>
            <div style={{ position: 'absolute', right: '-10px', top: '10px', opacity: 0.04, transform: 'scale(2.5) rotate(10deg)', pointerEvents: 'none' }}>
              <CloudRain size={100} />
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
              <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
                <div style={{ background: '#dbeafe', padding: '16px', borderRadius: '16px', display: 'flex' }}>
                  <CloudRain size={28} color="#2563eb" />
                </div>
                <div>
                  <h2 style={{ fontSize: '1.25rem', margin: '0 0 6px 0', color: 'var(--color-primary-dark)' }}>Climate & Weather</h2>
                  <p style={{ fontSize: '0.9rem', color: 'var(--color-text-secondary)', margin: 0 }}>Long-term climate and weather patterns</p>
                </div>
              </div>
              <div style={{ background: '#fef3c7', color: '#d97706', padding: '6px 14px', borderRadius: '20px', fontSize: '0.85rem', fontWeight: 600, border: '1px solid rgba(245, 158, 11, 0.2)' }}>
                Context Dependent
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '32px' }}>
              <div>
                <label style={labelStyle}>Annual Rainfall (mm/year)</label>
                <input type="number" step="1" min="0" placeholder="e.g. 500" style={inputStyle} value={formData.rainfall} onChange={(e) => handleChange('rainfall', e.target.value)}
                  onFocus={(e) => { e.currentTarget.style.borderColor = 'var(--color-primary)'; e.currentTarget.style.boxShadow = '0 0 0 2px rgba(30, 63, 51, 0.1)'; }}
                  onBlur={(e) => { e.currentTarget.style.borderColor = 'var(--color-border)'; e.currentTarget.style.boxShadow = 'none'; }}
                />
                {validationErrors.rainfall && <span style={{ color: 'var(--color-danger)', fontSize: '0.8rem', marginTop: '6px', display: 'block' }}>{validationErrors.rainfall}</span>}
              </div>
              <div>
                <label style={labelStyle}>Mean Temperature (°C)</label>
                <input type="number" step="0.1" placeholder="e.g. 29.0" style={inputStyle} value={formData.temperature} onChange={(e) => handleChange('temperature', e.target.value)}
                  onFocus={(e) => { e.currentTarget.style.borderColor = 'var(--color-primary)'; e.currentTarget.style.boxShadow = '0 0 0 2px rgba(30, 63, 51, 0.1)'; }}
                  onBlur={(e) => { e.currentTarget.style.borderColor = 'var(--color-border)'; e.currentTarget.style.boxShadow = 'none'; }}
                />
                {validationErrors.temperature && <span style={{ color: 'var(--color-danger)', fontSize: '0.8rem', marginTop: '6px', display: 'block' }}>{validationErrors.temperature}</span>}
              </div>
            </div>
          </div>

          {/* Section 3: Land Use & Cropping */}
          <div className="form-card" style={cardStyle} onMouseOver={(e) => e.currentTarget.style.boxShadow = 'var(--shadow-md)'} onMouseOut={(e) => e.currentTarget.style.boxShadow = 'var(--shadow-sm)'}>
            <div style={{ position: 'absolute', right: '-10px', top: '10px', opacity: 0.04, transform: 'scale(2.5)', pointerEvents: 'none' }}>
              <MapIcon size={100} />
            </div>

            <div style={{ display: 'flex', gap: '20px', alignItems: 'center', marginBottom: '32px' }}>
              <div style={{ background: '#ffedd5', padding: '16px', borderRadius: '16px', display: 'flex' }}>
                <MapIcon size={28} color="#ea580c" />
              </div>
              <div>
                <h2 style={{ fontSize: '1.25rem', margin: '0 0 6px 0', color: 'var(--color-primary-dark)' }}>Land Use & Agronomy</h2>
                <p style={{ fontSize: '0.9rem', color: 'var(--color-text-secondary)', margin: 0 }}>Current land use and agricultural practices</p>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '32px' }}>
              <div>
                <label style={labelStyle}>Land Use</label>
                <select className="select-input" style={{ ...inputStyle, appearance: 'none', backgroundImage: 'url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'currentColor\' stroke-width=\'2\' stroke-linecap=\'round\' stroke-linejoin=\'round\'%3e%3cpolyline points=\'6 9 12 15 18 9\'%3e%3c/polyline%3e%3c/svg%3e")', backgroundRepeat: 'no-repeat', backgroundPosition: 'right 12px center', backgroundSize: '16px' }} value={formData.land_use} onChange={(e) => handleChange('land_use', e.target.value)}
                  onFocus={(e) => { e.currentTarget.style.borderColor = 'var(--color-primary)'; e.currentTarget.style.boxShadow = '0 0 0 2px rgba(30, 63, 51, 0.1)'; }}
                  onBlur={(e) => { e.currentTarget.style.borderColor = 'var(--color-border)'; e.currentTarget.style.boxShadow = 'none'; }}
                >
                  <option value="">Select...</option>
                  <option value="agriculture">agriculture</option>
                  <option value="forestry">forestry</option>
                  <option value="urban">urban</option>
                  <option value="conservation">conservation</option>
                </select>
              </div>
              <div>
                <label style={labelStyle}>Primary Crop</label>
                <select className="select-input" style={{ ...inputStyle, appearance: 'none', backgroundImage: 'url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'currentColor\' stroke-width=\'2\' stroke-linecap=\'round\' stroke-linejoin=\'round\'%3e%3cpolyline points=\'6 9 12 15 18 9\'%3e%3c/polyline%3e%3c/svg%3e")', backgroundRepeat: 'no-repeat', backgroundPosition: 'right 12px center', backgroundSize: '16px' }} value={formData.crop} onChange={(e) => handleChange('crop', e.target.value)}
                  onFocus={(e) => { e.currentTarget.style.borderColor = 'var(--color-primary)'; e.currentTarget.style.boxShadow = '0 0 0 2px rgba(30, 63, 51, 0.1)'; }}
                  onBlur={(e) => { e.currentTarget.style.borderColor = 'var(--color-border)'; e.currentTarget.style.boxShadow = 'none'; }}
                >
                  <option value="">Select...</option>
                  <option value="wheat">wheat</option>
                  <option value="maize">maize</option>
                  <option value="soy">soy</option>
                  <option value="rice">rice</option>
                  <option value="cotton">cotton</option>
                  <option value="mixed">mixed</option>
                  <option value="none">none</option>
                </select>
              </div>
              <div>
                <label style={labelStyle}>Cropping System</label>
                <select className="select-input" style={{ ...inputStyle, appearance: 'none', backgroundImage: 'url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'currentColor\' stroke-width=\'2\' stroke-linecap=\'round\' stroke-linejoin=\'round\'%3e%3cpolyline points=\'6 9 12 15 18 9\'%3e%3c/polyline%3e%3c/svg%3e")', backgroundRepeat: 'no-repeat', backgroundPosition: 'right 12px center', backgroundSize: '16px' }} value={formData.cropping_system} onChange={(e) => handleChange('cropping_system', e.target.value)}
                  onFocus={(e) => { e.currentTarget.style.borderColor = 'var(--color-primary)'; e.currentTarget.style.boxShadow = '0 0 0 2px rgba(30, 63, 51, 0.1)'; }}
                  onBlur={(e) => { e.currentTarget.style.borderColor = 'var(--color-border)'; e.currentTarget.style.boxShadow = 'none'; }}
                >
                  <option value="">Select...</option>
                  <option value="monoculture">monoculture</option>
                  <option value="intercropping">intercropping</option>
                  <option value="rotation">rotation</option>
                  <option value="agroforestry">agroforestry</option>
                </select>
              </div>
            </div>
          </div>

          {/* Section 4: Biodiversity & Ecology */}
          <div className="form-card" style={cardStyle} onMouseOver={(e) => e.currentTarget.style.boxShadow = 'var(--shadow-md)'} onMouseOut={(e) => e.currentTarget.style.boxShadow = 'var(--shadow-sm)'}>
            <div style={{ position: 'absolute', right: '-10px', top: '10px', opacity: 0.04, transform: 'scale(2.5)', pointerEvents: 'none' }}>
              <Trees size={100} />
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
              <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
                <div style={{ background: '#dcfce7', padding: '16px', borderRadius: '16px', display: 'flex' }}>
                  <Trees size={28} color="#16a34a" />
                </div>
                <div>
                  <h2 style={{ fontSize: '1.25rem', margin: '0 0 6px 0', color: 'var(--color-primary-dark)' }}>Biodiversity & Ecosystem</h2>
                  <p style={{ fontSize: '0.9rem', color: 'var(--color-text-secondary)', margin: 0 }}>Indicators of ecosystem health</p>
                </div>
              </div>
              <div style={{ background: '#fef3c7', color: '#d97706', padding: '6px 14px', borderRadius: '20px', fontSize: '0.85rem', fontWeight: 600, border: '1px solid rgba(245, 158, 11, 0.2)' }}>
                Needs Attention
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '32px' }}>
              <div>
                <label style={labelStyle}>Species Richness (count)</label>
                <input type="number" step="1" min="0" placeholder="e.g. 12" style={inputStyle} value={formData.species_richness} onChange={(e) => handleChange('species_richness', e.target.value)}
                  onFocus={(e) => { e.currentTarget.style.borderColor = 'var(--color-primary)'; e.currentTarget.style.boxShadow = '0 0 0 2px rgba(30, 63, 51, 0.1)'; }}
                  onBlur={(e) => { e.currentTarget.style.borderColor = 'var(--color-border)'; e.currentTarget.style.boxShadow = 'none'; }}
                />
                {validationErrors.species_richness && <span style={{ color: 'var(--color-danger)', fontSize: '0.8rem', marginTop: '6px', display: 'block' }}>{validationErrors.species_richness}</span>}
              </div>
              <div>
                <label style={labelStyle}>Habitat Diversity</label>
                <select className="select-input" style={{ ...inputStyle, appearance: 'none', backgroundImage: 'url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'currentColor\' stroke-width=\'2\' stroke-linecap=\'round\' stroke-linejoin=\'round\'%3e%3cpolyline points=\'6 9 12 15 18 9\'%3e%3c/polyline%3e%3c/svg%3e")', backgroundRepeat: 'no-repeat', backgroundPosition: 'right 12px center', backgroundSize: '16px' }} value={formData.habitat_diversity} onChange={(e) => handleChange('habitat_diversity', e.target.value)}
                  onFocus={(e) => { e.currentTarget.style.borderColor = 'var(--color-primary)'; e.currentTarget.style.boxShadow = '0 0 0 2px rgba(30, 63, 51, 0.1)'; }}
                  onBlur={(e) => { e.currentTarget.style.borderColor = 'var(--color-border)'; e.currentTarget.style.boxShadow = 'none'; }}
                >
                  <option value="">Select...</option>
                  <option value="low">low</option>
                  <option value="moderate">moderate</option>
                  <option value="high">high</option>
                </select>
              </div>
            </div>
          </div>

          {/* Section 5: Human Impact & Location */}
          <div className="form-card" style={cardStyle} onMouseOver={(e) => e.currentTarget.style.boxShadow = 'var(--shadow-md)'} onMouseOut={(e) => e.currentTarget.style.boxShadow = 'var(--shadow-sm)'}>
            <div style={{ position: 'absolute', right: '-10px', top: '10px', opacity: 0.04, transform: 'scale(2.5)', pointerEvents: 'none' }}>
              <Users size={100} />
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
              <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
                <div style={{ background: '#f3e8ff', padding: '16px', borderRadius: '16px', display: 'flex' }}>
                  <Users size={28} color="#9333ea" />
                </div>
                <div>
                  <h2 style={{ fontSize: '1.25rem', margin: '0 0 6px 0', color: 'var(--color-primary-dark)' }}>Human Impact & Metadata</h2>
                  <p style={{ fontSize: '0.9rem', color: 'var(--color-text-secondary)', margin: 0 }}>Anthropogenic pressures and region details</p>
                </div>
              </div>
              <div style={{ background: '#fee2e2', color: '#dc2626', padding: '6px 14px', borderRadius: '20px', fontSize: '0.85rem', fontWeight: 600, border: '1px solid rgba(239, 68, 68, 0.2)' }}>
                At Risk
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '32px' }}>
              <div>
                <label style={labelStyle}>Pollution Pressure</label>
                <select className="select-input" style={{ ...inputStyle, appearance: 'none', backgroundImage: 'url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'currentColor\' stroke-width=\'2\' stroke-linecap=\'round\' stroke-linejoin=\'round\'%3e%3cpolyline points=\'6 9 12 15 18 9\'%3e%3c/polyline%3e%3c/svg%3e")', backgroundRepeat: 'no-repeat', backgroundPosition: 'right 12px center', backgroundSize: '16px' }} value={formData.pollution} onChange={(e) => handleChange('pollution', e.target.value)}
                  onFocus={(e) => { e.currentTarget.style.borderColor = 'var(--color-primary)'; e.currentTarget.style.boxShadow = '0 0 0 2px rgba(30, 63, 51, 0.1)'; }}
                  onBlur={(e) => { e.currentTarget.style.borderColor = 'var(--color-border)'; e.currentTarget.style.boxShadow = 'none'; }}
                >
                  <option value="">Select...</option>
                  <option value="low">low</option>
                  <option value="moderate">moderate</option>
                  <option value="high">high</option>
                </select>
              </div>
              <div>
                <label style={labelStyle}>Deforestation Pressure</label>
                <select className="select-input" style={{ ...inputStyle, appearance: 'none', backgroundImage: 'url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'currentColor\' stroke-width=\'2\' stroke-linecap=\'round\' stroke-linejoin=\'round\'%3e%3cpolyline points=\'6 9 12 15 18 9\'%3e%3c/polyline%3e%3c/svg%3e")', backgroundRepeat: 'no-repeat', backgroundPosition: 'right 12px center', backgroundSize: '16px' }} value={formData.deforestation} onChange={(e) => handleChange('deforestation', e.target.value)}
                  onFocus={(e) => { e.currentTarget.style.borderColor = 'var(--color-primary)'; e.currentTarget.style.boxShadow = '0 0 0 2px rgba(30, 63, 51, 0.1)'; }}
                  onBlur={(e) => { e.currentTarget.style.borderColor = 'var(--color-border)'; e.currentTarget.style.boxShadow = 'none'; }}
                >
                  <option value="">Select...</option>
                  <option value="low">low</option>
                  <option value="active">active</option>
                  <option value="severe">severe</option>
                  <option value="high">high</option>
                </select>
              </div>
              <div>
                <label style={labelStyle}>Region Name</label>
                <input type="text" placeholder="e.g. Semi-Arid North, Mediterranean" style={inputStyle} value={formData.region} onChange={(e) => handleChange('region', e.target.value)}
                  onFocus={(e) => { e.currentTarget.style.borderColor = 'var(--color-primary)'; e.currentTarget.style.boxShadow = '0 0 0 2px rgba(30, 63, 51, 0.1)'; }}
                  onBlur={(e) => { e.currentTarget.style.borderColor = 'var(--color-border)'; e.currentTarget.style.boxShadow = 'none'; }}
                />
              </div>
            </div>
          </div>

          {/* Form Actions */}
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '20px', marginTop: '16px', position: 'relative', zIndex: 10, paddingBottom: '32px' }}>
            <button 
              type="button" 
              onClick={() => navigate('/')} 
              disabled={saving}
              style={{ background: 'white', border: '1px solid var(--color-border)', color: 'var(--color-text-secondary)', padding: '12px 24px', borderRadius: '10px', fontWeight: 600, fontSize: '0.95rem', cursor: 'pointer', transition: 'all var(--transition-fast)' }}
              onMouseOver={(e) => { e.currentTarget.style.background = 'var(--color-surface-hover)'; e.currentTarget.style.borderColor = 'var(--color-border-focus)'; }}
              onMouseOut={(e) => { e.currentTarget.style.background = 'white'; e.currentTarget.style.borderColor = 'var(--color-border)'; }}
            >
              Cancel
            </button>

            <button 
              type="submit" 
              disabled={saving}
              style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '12px 28px', fontSize: '0.95rem', borderRadius: '10px', background: 'var(--color-primary)', color: 'white', border: 'none', fontWeight: 600, cursor: 'pointer', boxShadow: 'var(--shadow-sm)', transition: 'all var(--transition-fast)' }}
              onMouseOver={(e) => { e.currentTarget.style.background = 'var(--color-primary-light)'; e.currentTarget.style.boxShadow = 'var(--shadow-md)'; }}
              onMouseOut={(e) => { e.currentTarget.style.background = 'var(--color-primary)'; e.currentTarget.style.boxShadow = 'var(--shadow-sm)'; }}
              onMouseDown={(e) => e.currentTarget.style.transform = 'scale(0.98)'}
              onMouseUp={(e) => e.currentTarget.style.transform = 'scale(1)'}
            >
              <Save size={18} />
              {saving ? 'Saving...' : 'Save Observations'}
            </button>
          </div>

        </div>
      </form>
      </div>
      
      {/* Decorative background leaf element exactly as requested */}
      <div style={{ position: 'fixed', bottom: '-15%', right: '-5%', width: '600px', height: '600px', opacity: 0.04, pointerEvents: 'none', zIndex: 0, transform: 'rotate(-10deg)' }}>
        <svg viewBox="0 0 24 24" fill="var(--color-primary)" width="100%" height="100%">
          <path d="M17.8,2.7C17.8,2.7 13.9,2 10.7,4.8C9.6,5.8 8.9,7 8.5,8.1C6.7,7.2 4.6,7 2.6,7.6C2.6,7.6 2.5,12.5 5.5,15.7C7.6,18 10.2,18.8 12.3,18.9C13,21.5 15,22.8 15,22.8C15,22.8 15.9,21 15.5,18.9C18.1,17.9 20,15.2 20.3,12C20.7,7.8 17.8,2.7 17.8,2.7M14.6,13.6C12.9,15.2 9.5,15.5 9.5,15.5C9.5,15.5 10.5,12.2 12.1,10.6C13.8,8.9 17.3,8.7 17.3,8.7C17.3,8.7 16.3,12 14.6,13.6Z" />
        </svg>
      </div>
    </>
  );
};
