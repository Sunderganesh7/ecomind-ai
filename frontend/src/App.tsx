import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { EnvironmentalProvider } from './context/EnvironmentalContext';
import { Navigation } from './components/Navigation';
import { Search, MapPin, Calendar, Bell, ChevronDown } from 'lucide-react';

// Pages
import { DashboardOverview } from './pages/DashboardOverview';
import { EnvironmentalData } from './pages/EnvironmentalData';
import { SoilIntelligence } from './pages/SoilIntelligence';
import { ClimateIntelligence } from './pages/ClimateIntelligence';
import { BiodiversityIntelligence } from './pages/BiodiversityIntelligence';
import { LandIntelligence } from './pages/LandIntelligence';
import { HumanImpact } from './pages/HumanImpact';
import { RiskProfile } from './pages/RiskProfile';
import { AiScientist } from './pages/AiScientist';
import { EvidenceAndReasoning } from './pages/EvidenceAndReasoning';

const AppLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="app-container">
      <Navigation />
      <div className="main-wrapper">
        {children}
      </div>
    </div>
  );
};

function App() {
  return (
    <EnvironmentalProvider defaultProfileId={1}>
      <Router>
        <AppLayout>
          <Routes>
            <Route path="/" element={<Navigate to="/environment" replace />} />
            <Route path="/overview" element={<DashboardOverview />} />
            <Route path="/environment" element={<EnvironmentalData />} />
            <Route path="/soil" element={<SoilIntelligence />} />
            <Route path="/climate" element={<ClimateIntelligence />} />
            <Route path="/biodiversity" element={<BiodiversityIntelligence />} />
            <Route path="/land" element={<LandIntelligence />} />
            <Route path="/human-impact" element={<HumanImpact />} />
            <Route path="/risk-profile" element={<RiskProfile />} />
            <Route path="/ai-scientist" element={<AiScientist />} />
            <Route path="/reasoning" element={<EvidenceAndReasoning />} />

            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AppLayout>
      </Router>
    </EnvironmentalProvider>
  );
}

export default App;
