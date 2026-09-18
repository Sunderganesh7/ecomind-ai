// Core Environmental Models

export interface Location {
  latitude?: number;
  longitude?: number;
  region?: string;
  country?: string;
}

export interface VariableObservation {
  variable: string;
  value: any;
  unit?: string;
  timestamp?: string;
  source?: string;
  confidence?: string;
}

export interface SoilCreate {
  ph?: number;
  soil_ph?: number;
  organic_carbon?: number;
  moisture?: number;
}

export interface ClimateCreate {
  temperature?: number;
  rainfall?: number;
}

export interface LandCreate {
  use?: string;
  land_use?: string;
  crop?: string;
  cropping_system?: string;
}

export interface BiodiversityCreate {
  species_richness?: number;
  habitat_diversity?: string;
}

export interface HumanImpactCreate {
  pollution?: string;
  deforestation?: string;
}

export interface EnvironmentalObservationCreate {
  location?: Location;
  soil?: SoilCreate;
  climate?: ClimateCreate;
  land?: LandCreate;
  biodiversity?: BiodiversityCreate;
  human_impact?: HumanImpactCreate;
  observed_at?: string;
  source_name?: string;
  source_type?: string;
  source_reference?: string;
  data_quality?: string;
  confidence?: number;
}

export interface EnvironmentalObservation {
  id: number;
  location?: Location;
  timestamp?: string;
  observed_at?: string;
  created_at?: string;
  source_name?: string;
  source_type?: string;
  source_reference?: string;
  data_quality?: string;
  confidence?: number;
  soil?: {
    ph?: VariableObservation | number;
    soil_ph?: VariableObservation | number;
    organic_carbon?: VariableObservation | number;
    moisture?: VariableObservation | number;
    nitrogen?: VariableObservation | number;
    phosphorus?: VariableObservation | number;
  };
  climate?: {
    temperature?: VariableObservation | number;
    rainfall?: VariableObservation | number;
    humidity?: VariableObservation | number;
  };
  biodiversity?: {
    species_richness?: VariableObservation | number;
    habitat_diversity?: VariableObservation | string;
  };
  land?: {
    use?: VariableObservation | string;
    land_use?: VariableObservation | string;
    crop?: VariableObservation | string;
    cropping_system?: VariableObservation | string;
  };
  land_use?: {
    use?: VariableObservation | string;
    crop?: VariableObservation | string;
    cropping_system?: VariableObservation | string;
    management_practices?: VariableObservation | string;
  };
  human_impact?: {
    pollution?: VariableObservation | string;
    deforestation?: VariableObservation | string;
  };
}

// Baseline Models
export interface AnalyzedMetric {
  name: string;
  value: any;
  status: 'optimal' | 'marginal' | 'critical' | 'unknown';
  interpretation: string;
  historical_context?: string;
}

export interface BaselineProfileResponse {
  profile_id: number;
  metrics: Record<string, AnalyzedMetric>;
  warnings: string[];
  summary: {
    soil_status?: string;
    water_status?: string;
    habitat_status?: string;
  };
}

export interface EnvironmentalRelationship {
  relationship_id: string;
  source_variables?: string[];
  inputs?: string[];
  target_variable?: string;
  intermediate_states?: Array<{ name: string; status: string; type: string }>;
  downstream_states?: Array<{ name: string; status: string; type: string }>;
  relationship_type?: string;
  strength?: 'strong' | 'moderate' | 'weak';
  evidence_status: string;
  mechanism?: string;
}

export interface RelationshipProfileResponse {
  profile_id: number;
  relationships: EnvironmentalRelationship[];
  variables_used: string[];
}

// Risk Models
export interface Driver {
  variable?: string;
  state?: string;
  status: string;
  type: string;
  role: string;
}

export interface Uncertainty {
  level: string;
  reasons: string[];
}

export interface CompositeRiskPattern {
  risk_pattern_id: string;
  name: string;
  status: 'active' | 'potential' | 'mitigated';
  variables_used: string[];
  primary_drivers: Driver[];
  supporting_signals: Driver[];
  secondary_consequences: string[];
  relationships_used: string[];
  evidence_status: string;
  uncertainty: Uncertainty;
}

export interface RiskProfileResponse {
  profile_id: number;
  risk_patterns: CompositeRiskPattern[];
}

// Recommendation Models
export interface Confidence {
  level: string;
  reason: string;
}

export interface ReasoningStep {
  step: number;
  type: string;
  variables?: string[];
  relationship_id?: string;
  risk_pattern_id?: string;
  intervention_id?: string;
  chunk_ids?: string[];
  status?: string;
}

export interface Claim {
  claim_id: string;
  claim_text: string;
  claim_type: string;
  origin: string;
  support_status: string;
  evidence?: EvidenceReference[];
}

export interface EvidenceReference {
  source_id?: string;
  chunk_id?: string;
  document_id?: string;
  source?: string;
  document?: string;
  year?: number;
  page_number?: number;
  section?: string;
  url?: string;
  relevance?: string;
}

export interface StructuredRecommendation {
  recommendation_id: string;
  what_to_do: string;
  why_it_works: string;
  environmental_mechanism: string;
  impacted_metrics: {
    direct: string[];
    indirect: string[];
    context_dependent: string[];
  };
  time_horizon: {
    estimate: string;
    dependency: string;
  };
  confidence: Confidence;
  evidence_status: string;
  claims: Claim[];
  risk_patterns_used: string[];
  relationships_used: string[];
  variables_used: string[];
  reasoning_trace: ReasoningStep[];
  applicability: string;
  missing_context: string[];
}

export interface GuardedRecommendationProfileResponse {
  recommendation?: StructuredRecommendation;
  recommendation_available: boolean;
  quality_guard: {
    status: string;
    action: string;
    reason: string;
  };
}

// Chat Models
export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface ChatRecommendation {
  intervention_id: string;
  what_to_do: string;
  why_it_works: string;
  environmental_mechanism: string;
  impacted_metrics: string[];
  time_horizon: string;
  confidence: string;
  evidence_claims: string[];
}

export interface ChatMetric {
  name: string;
  current_value: any;
  unit?: string;
  role: 'direct' | 'indirect' | 'context' | 'context_dependent';
  status: string;
}

export interface ChatDriver {
  variable: string;
  value?: any;
  unit?: string;
  status: string;
  role: 'primary_driver' | 'secondary_consequence' | 'context';
  source: string;
}

export interface EnvironmentalResponse {
  response_type: string;
  assessment: {
    summary: string;
    status: string;
  };
  drivers: ChatDriver[];
  recommendations: ChatRecommendation[];
  metrics: ChatMetric[];
  time_horizon: { value: string; reason?: string };
  confidence: Confidence;
  claims: Claim[];
  variables_used: string[];
  reasoning_trace: ReasoningStep[];
}
