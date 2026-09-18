import React, { createContext, useContext, useState, useEffect } from 'react';
import { EnvironmentalService } from '../api/environmentalService';
import type {
  EnvironmentalObservation,
  BaselineProfileResponse,
  RelationshipProfileResponse,
  RiskProfileResponse,
  GuardedRecommendationProfileResponse,
} from '../types';

interface EnvironmentalState {
  profileId: number;
  profile: EnvironmentalObservation | null;
  baseline: BaselineProfileResponse | null;
  relationships: RelationshipProfileResponse | null;
  risks: RiskProfileResponse | null;
  recommendations: GuardedRecommendationProfileResponse | null;
  loading: boolean;
  isFetching: boolean;
  error: string | null;
  refresh: () => void;
}

const EnvironmentalContext = createContext<EnvironmentalState | undefined>(undefined);

export const EnvironmentalProvider: React.FC<{ children: React.ReactNode; defaultProfileId?: number }> = ({ 
  children, 
  defaultProfileId = 1 
}) => {
  const [profileId] = useState(defaultProfileId);
  const [profile, setProfile] = useState<EnvironmentalObservation | null>(null);
  const [baseline, setBaseline] = useState<BaselineProfileResponse | null>(null);
  const [relationships, setRelationships] = useState<RelationshipProfileResponse | null>(null);
  const [risks, setRisks] = useState<RiskProfileResponse | null>(null);
  const [recommendations, setRecommendations] = useState<GuardedRecommendationProfileResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [isFetching, setIsFetching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    // Only set hard loading if we have no profile data yet
    if (!profile) {
      setLoading(true);
    }
    setIsFetching(true);
    setError(null);
    
    try {
      // 1. Fetch Profile
      const profData = await EnvironmentalService.getProfile(profileId);
      setProfile(profData);

      // 2. We can run the reasoning chain in parallel since they just require the profileId
      const [baseData, relData, riskData, recData] = await Promise.all([
        EnvironmentalService.getBaseline(profileId).catch(() => null),
        EnvironmentalService.getRelationships(profileId).catch(() => null),
        EnvironmentalService.getRisks(profileId).catch(() => null),
        EnvironmentalService.getRecommendations(profileId).catch(() => null),
      ]);

      setBaseline(baseData);
      setRelationships(relData);
      setRisks(riskData);
      setRecommendations(recData);

    } catch (err: any) {
      setError(err.message || 'Failed to load environmental intelligence.');
    } finally {
      setLoading(false);
      setIsFetching(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [profileId]);

  return (
    <EnvironmentalContext.Provider
      value={{
        profileId,
        profile,
        baseline,
        relationships,
        risks,
        recommendations,
        loading,
        isFetching,
        error,
        refresh: loadData
      }}
    >
      {children}
    </EnvironmentalContext.Provider>
  );
};

export const useEnvironmentalData = () => {
  const context = useContext(EnvironmentalContext);
  if (context === undefined) {
    throw new Error('useEnvironmentalData must be used within an EnvironmentalProvider');
  }
  return context;
};
