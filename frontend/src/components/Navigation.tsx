import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Leaf, 
  ThermometerSun, 
  Trees, 
  Map as MapIcon, 
  Factory, 
  ShieldAlert, 
  Bot,
  Network,
  FileText
} from 'lucide-react';

export const Navigation: React.FC = () => {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-title">
          <Leaf className="sidebar-icon" size={24} color="var(--color-primary)" fill="var(--color-primary)" />
          <span>EcoMind AI</span>
        </div>
        <div className="sidebar-subtitle">Data for a Greener Tomorrow</div>
      </div>
      
      <nav className="sidebar-nav">
        <NavLink 
          to="/environment" 
          className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
        >
          <MapIcon size={20} />
          Environmental Data
        </NavLink>
        
        <NavLink 
          to="/overview" 
          className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          end
        >
          <LayoutDashboard size={20} />
          Overview
        </NavLink>
        
        <NavLink 
          to="/soil" 
          className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
        >
          <Leaf size={20} />
          Soil
        </NavLink>
        
        <NavLink 
          to="/climate" 
          className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
        >
          <ThermometerSun size={20} />
          Climate
        </NavLink>
        
        <NavLink 
          to="/biodiversity" 
          className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
        >
          <Trees size={20} />
          Biodiversity
        </NavLink>
        
        <NavLink 
          to="/land" 
          className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
        >
          <MapIcon size={20} />
          Land
        </NavLink>
        
        <NavLink 
          to="/human-impact" 
          className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
        >
          <Factory size={20} />
          Human Impact
        </NavLink>

        <div className="section-divider" style={{ margin: '12px 16px', backgroundColor: 'var(--color-border)' }}></div>

        <NavLink 
          to="/risk-profile" 
          className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
        >
          <ShieldAlert size={20} />
          Risk Profile
        </NavLink>

        <NavLink 
          to="/ai-scientist" 
          className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
        >
          <Bot size={20} />
          AI Scientist
        </NavLink>

        <NavLink 
          to="/reasoning" 
          className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
        >
          <Network size={20} />
          Evidence & Reasoning
        </NavLink>


      </nav>

      <div className="sidebar-banner">
        <img 
          src="https://images.unsplash.com/photo-1542273917363-3b1817f69a5d?q=80&w=400&auto=format&fit=crop" 
          alt=""
          onError={(e) => { e.currentTarget.style.display = 'none'; }}
        />
        <div className="sidebar-banner-content">
          <h3 style={{color: 'white', fontSize: '1.25rem', marginBottom: '8px', lineHeight: 1.2}}>Smarter<br/>Insights.<br/>Healthier<br/>Planet.</h3>
          <p style={{fontSize: '0.8rem', color: 'rgba(255,255,255,0.85)', lineHeight: 1.4}}>AI-driven intelligence for a sustainable future.</p>
          <div style={{ position: 'absolute', bottom: '24px', right: '24px', background: 'var(--color-success)', borderRadius: '50%', width: '28px', height: '28px', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: 'var(--shadow-md)' }}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
          </div>
        </div>
      </div>

      <div className="sidebar-footer">
        <div style={{display: 'flex', alignItems: 'center', gap: '10px', color: 'var(--color-primary)', fontWeight: 700, fontSize: '0.95rem'}}>
          <Leaf size={18} fill="var(--color-primary)"/> EcoMind AI
        </div>
        <div style={{fontSize: '0.8rem', color: 'var(--color-text-tertiary)', marginTop: '4px'}}>v1.0.0 Enterprise</div>
      </div>
    </aside>
  );
};
