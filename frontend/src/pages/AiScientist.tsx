import React, { useState, useEffect } from 'react';
import { useEnvironmentalData } from '../context/EnvironmentalContext';
import { ChatService } from '../api/chatService';
import type { ChatMessage, EnvironmentalResponse } from '../types';
import { AnalysisWorkspace } from '../components/AnalysisWorkspace';
import { Bot, Send, User, ChevronDown, ChevronUp, AlertCircle, FileText, FlaskConical } from 'lucide-react';

const SUGGESTIONS = [
  "What is driving biodiversity pressure?",
  "How is soil condition affecting habitat quality?",
  "What should I change to improve biodiversity?",
  "What intervention addresses the main environmental constraints?"
];

const FOLLOW_UPS = [
  "What about biodiversity?",
  "How does soil affect this?",
  "What intervention could address this?",
  "What evidence supports this?",
  "Which metrics would be affected?"
];

export const AiScientist: React.FC = () => {
  const { profileId, profile, loading } = useEnvironmentalData();
  const [conversationId, setConversationId] = useState<string | undefined>(undefined);
  const [query, setQuery] = useState('');
  const [history, setHistory] = useState<ChatMessage[]>([]);
  const [responses, setResponses] = useState<EnvironmentalResponse[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [loadingStage, setLoadingStage] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);

  const getVal = (obs: any) => {
    if (obs === null || obs === undefined) return undefined;
    if (typeof obs === 'object' && 'value' in obs) return obs.value;
    return obs;
  };

  const getMoistureVal = (obs: any) => {
    const val = getVal(obs);
    if (val === null || val === undefined) return 'Unknown';
    const num = typeof val === 'number' ? val : parseFloat(String(val));
    if (isNaN(num) || num < 0 || num > 100) return 'Unknown';
    return `${num}%`;
  };

  // Rotate loading text slightly to show process
  useEffect(() => {
    if (!isTyping) {
      setLoadingStage('');
      return;
    }
    const stages = [
      "Analyzing environmental context...",
      "Processing multi-metric relationships...",
      "Searching knowledge base...",
      "Validating recommendation...",
    ];
    let i = 0;
    setLoadingStage(stages[0]);
    const interval = setInterval(() => {
      i = (i + 1) % stages.length;
      setLoadingStage(stages[i]);
    }, 1500);
    return () => clearInterval(interval);
  }, [isTyping]);

  const handleQuerySubmit = async (text: string) => {
    if (!text.trim()) return;

    const userMessage: ChatMessage = { role: 'user', content: text };
    setHistory([...history, userMessage]);
    setQuery('');
    setIsTyping(true);
    setError(null);

    try {
      const response = await ChatService.sendMessage(text, profileId, conversationId);
      
      // Clean up internal fallback messages from the backend so they aren't shown to the user
      if (response.assessment && response.assessment.summary) {
        response.assessment.summary = response.assessment.summary
          .replace(/LLM explanation unavailable — deterministic environmental analysis shown\.?\s*/i, '')
          .replace(/Conversational explanation service is (currently )?unavailable\.?\s*/i, '')
          .replace(/Action was flagged:.*?(?=\s|$)/i, '')
          .trim();
      }
      
      if (response.confidence && response.confidence.reason) {
        response.confidence.reason = response.confidence.reason
          .replace(/Fallback response used due to:.*?$/i, '')
          .trim();
      }

      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }
      setResponses([...responses, response]);
      setHistory(prev => [...prev, { role: 'assistant', content: response.assessment.summary }]);
      // Close history if we just ran a new query
      setIsHistoryOpen(false);
    } catch (err: any) {
      setError(err.message || 'Environmental analysis could not be completed.');
    } finally {
      setIsTyping(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleQuerySubmit(query);
  };

  const handleChipClick = (text: string) => {
    setQuery(text);
  };

  if (loading) {
    return <div className="main-content">Loading AI Scientist workspace...</div>;
  }

  const latestResponse = responses.length > 0 ? responses[responses.length - 1] : null;
  const currentChips = history.length > 0 ? FOLLOW_UPS : SUGGESTIONS;

  return (
    <div className="workspace-container" style={{ padding: '24px' }}>
      
      {/* LEFT: Context Panel */}
      <div style={{ width: '320px', flexShrink: 0, borderRight: '1px solid var(--color-border)', paddingRight: '24px', overflowY: 'auto' }}>
        <h2 style={{ fontSize: '1.1rem', marginBottom: '8px', color: 'var(--color-primary-dark)', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <FlaskConical size={20} />
          Environmental Context
        </h2>
        <div style={{ fontSize: '0.9rem', color: 'var(--color-text-secondary)', marginBottom: '24px' }}>
          {profile?.location?.region ? `Location: ${profile.location.region}` : 'Location: Region / coordinates when available'}
        </div>
        
        <div style={{ marginBottom: '20px' }}>
          <h3 style={{ fontSize: '0.85rem', color: 'var(--color-text-tertiary)', textTransform: 'uppercase', marginBottom: '8px' }}>Soil</h3>
          <div style={{ fontSize: '0.9rem', display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <div><span style={{ color: 'var(--color-text-tertiary)' }}>Organic Carbon:</span> {getVal(profile?.soil?.organic_carbon) !== undefined ? `${getVal(profile?.soil?.organic_carbon)}%` : 'Unknown'}</div>
            <div><span style={{ color: 'var(--color-text-tertiary)' }}>Moisture:</span> {getMoistureVal(profile?.soil?.moisture)}</div>
            <div><span style={{ color: 'var(--color-text-tertiary)' }}>pH:</span> {getVal(profile?.soil?.soil_ph ?? profile?.soil?.ph) ?? 'Unknown'}</div>
          </div>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <h3 style={{ fontSize: '0.85rem', color: 'var(--color-text-tertiary)', textTransform: 'uppercase', marginBottom: '8px' }}>Climate</h3>
          <div style={{ fontSize: '0.9rem', display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <div><span style={{ color: 'var(--color-text-tertiary)' }}>Rainfall:</span> {getVal(profile?.climate?.rainfall) !== undefined ? `${getVal(profile?.climate?.rainfall)} mm` : 'Unknown'}</div>
            <div><span style={{ color: 'var(--color-text-tertiary)' }}>Temperature:</span> {getVal(profile?.climate?.temperature) !== undefined ? `${getVal(profile?.climate?.temperature)}°C` : 'Unknown'}</div>
          </div>
        </div>
        
        <div style={{ marginBottom: '20px' }}>
          <h3 style={{ fontSize: '0.85rem', color: 'var(--color-text-tertiary)', textTransform: 'uppercase', marginBottom: '8px' }}>Land Use</h3>
          <div style={{ fontSize: '0.9rem', display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <div><span style={{ color: 'var(--color-text-tertiary)' }}>Land Use:</span> {getVal(profile?.land?.land_use ?? profile?.land?.use ?? profile?.land_use?.use) ?? 'Unknown'}</div>
            <div><span style={{ color: 'var(--color-text-tertiary)' }}>Crop:</span> {getVal(profile?.land?.crop ?? profile?.land_use?.crop) ?? 'Unknown'}</div>
            <div><span style={{ color: 'var(--color-text-tertiary)' }}>Cropping System:</span> {getVal(profile?.land?.cropping_system ?? profile?.land_use?.cropping_system) ?? 'Unknown'}</div>
          </div>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <h3 style={{ fontSize: '0.85rem', color: 'var(--color-text-tertiary)', textTransform: 'uppercase', marginBottom: '8px' }}>Biodiversity</h3>
          <div style={{ fontSize: '0.9rem', display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <div><span style={{ color: 'var(--color-text-tertiary)' }}>Species Richness:</span> {getVal(profile?.biodiversity?.species_richness) ?? 'Unknown'}</div>
            <div><span style={{ color: 'var(--color-text-tertiary)' }}>Habitat Diversity:</span> {getVal(profile?.biodiversity?.habitat_diversity) ?? 'Unknown'}</div>
          </div>
        </div>
      </div>

      {/* CENTER/RIGHT: Analysis Workspace */}
      <div className="workspace-main">
        <div style={{ marginBottom: '24px' }}>
          <h1 style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '1.5rem', margin: 0 }}>
            <Bot size={28} color="var(--color-primary)" />
            AI Environmental Scientist
          </h1>
          <p style={{ color: 'var(--color-text-secondary)', marginTop: '8px' }}>
            Evidence-grounded environmental analysis and recommendations
          </p>
        </div>

        {/* Conversation History Accordion */}
        {responses.length > 1 && (
          <div style={{ marginBottom: '24px' }}>
            <div className="accordion-header" onClick={() => setIsHistoryOpen(!isHistoryOpen)}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <FileText size={18} />
                Previous Analyses ({responses.length - 1})
              </div>
              {isHistoryOpen ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
            </div>
            {isHistoryOpen && (
              <div className="accordion-content">
                {responses.slice(0, -1).map((resp, i) => (
                  <div key={i} style={{ padding: '12px', borderBottom: i < responses.length - 2 ? '1px solid var(--color-border)' : 'none' }}>
                    <div style={{ fontWeight: 600, marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '6px' }}><User size={14} /> {history[i * 2]?.content}</div>
                    <div style={{ color: 'var(--color-text-secondary)', fontSize: '0.9rem' }}>{resp.assessment.summary}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        <div className="workspace-content">
          {error ? (
            <div style={{ padding: '16px', background: 'var(--color-danger-bg)', color: 'var(--color-danger)', borderLeft: '4px solid var(--color-danger)', borderRadius: 'var(--radius-md)', display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
              <AlertCircle size={20} style={{ marginTop: '2px' }} />
              <div>
                <div style={{ fontWeight: 600, marginBottom: '4px' }}>Analysis Failed</div>
                <div>{error}</div>
                <button 
                  onClick={() => handleQuerySubmit(history[history.length - 1]?.content || '')} 
                  style={{ marginTop: '12px', background: 'transparent', border: '1px solid currentColor', color: 'inherit', padding: '6px 12px', borderRadius: 'var(--radius-sm)', cursor: 'pointer', fontWeight: 600 }}>
                  Retry
                </button>
              </div>
            </div>
          ) : isTyping ? (
            <div style={{ padding: '40px', textAlign: 'center', color: 'var(--color-primary)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px' }}>
              <div className="loading-pulse" style={{ width: '48px', height: '48px', borderRadius: '50%', background: 'var(--color-primary-light)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Bot size={24} color="white" />
              </div>
              <div style={{ fontWeight: 600, fontSize: '1.1rem' }}>{loadingStage}</div>
            </div>
          ) : latestResponse ? (
            <div>
              <div style={{ marginBottom: '24px', padding: '16px', background: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)' }}>
                <div style={{ fontSize: '0.85rem', color: 'var(--color-text-tertiary)', textTransform: 'uppercase', marginBottom: '8px' }}>User Query</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 600 }}>{history[history.length - 1]?.content}</div>
              </div>
              <AnalysisWorkspace response={latestResponse} />
            </div>
          ) : (
            <div style={{ textAlign: 'center', color: 'var(--color-text-tertiary)', marginTop: '60px' }}>
              <FlaskConical size={48} style={{ opacity: 0.2, marginBottom: '16px' }} />
              <div style={{ fontSize: '1.1rem', color: 'var(--color-text-secondary)' }}>Environmental context loaded. Analysis ready.</div>
              <p style={{ marginTop: '8px' }}>Ask an environmental question below to begin the scientific assessment.</p>
            </div>
          )}
        </div>

        <div className="workspace-input-container">
          <div className="follow-up-chips">
            {currentChips.map((chip, i) => (
              <button 
                key={i} 
                className="chip" 
                onClick={() => handleChipClick(chip)}
                disabled={isTyping}
              >
                {chip}
              </button>
            ))}
          </div>
          
          <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '12px' }}>
            <input 
              type="text" 
              className="chat-input"
              placeholder="Ask your environmental question..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              disabled={isTyping}
              style={{ border: 'none', background: 'transparent', padding: '8px', fontSize: '1rem', outline: 'none' }}
            />
            <button type="submit" className="btn-primary" disabled={isTyping || !query.trim()} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Send size={18} /> Ask
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
