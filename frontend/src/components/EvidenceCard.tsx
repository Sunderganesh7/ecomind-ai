import React, { useState } from 'react';
import type { Claim } from '../types';
import { BookOpen, ExternalLink, ChevronDown, ChevronRight, Cpu, AlertCircle } from 'lucide-react';

interface EvidenceCardProps {
  claim: Claim;
}

export const EvidenceCard: React.FC<EvidenceCardProps> = ({ claim }) => {
  const [expanded, setExpanded] = useState(false);
  const isDeterministic = claim.origin === 'deterministic_analysis';
  const isSupported = claim.support_status === 'supported';
  const hasEvidenceChunks = Boolean(claim.evidence && claim.evidence.length > 0);

  // Determine badge and label
  let badgeClass = 'badge-warning';
  let badgeLabel = 'INSUFFICIENT SCIENTIFIC EVIDENCE';
  let sourceLabel = 'Peer-Reviewed Scientific Literature';

  if (isDeterministic) {
    badgeClass = 'badge-info';
    badgeLabel = 'DETERMINISTIC ANALYSIS';
    sourceLabel = 'Ecological Rule Engine & Risk Patterns';
  } else if (isSupported && hasEvidenceChunks) {
    badgeClass = 'badge-success';
    badgeLabel = 'SUPPORTED BY SCIENTIFIC LITERATURE';
    sourceLabel = 'Scientific Knowledge Base';
  } else {
    badgeClass = 'badge-warning';
    badgeLabel = 'INSUFFICIENT SCIENTIFIC EVIDENCE';
    sourceLabel = 'Scientific Knowledge Base (No Chunks Found)';
  }

  return (
    <div style={{ marginBottom: '16px', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', overflow: 'hidden' }}>
      <div 
        style={{ padding: '16px', background: 'var(--color-surface)', cursor: 'pointer', display: 'flex', gap: '12px', alignItems: 'flex-start' }}
        onClick={() => setExpanded(!expanded)}
      >
        <div style={{ marginTop: '2px', color: 'var(--color-secondary)' }}>
          {expanded ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: '0.95rem', fontWeight: 500, color: 'var(--color-text-primary)', marginBottom: '6px' }}>
            {claim.claim_text}
          </div>
          <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
            <span className={`badge ${badgeClass}`} style={{ fontSize: '0.72rem', fontWeight: 700, letterSpacing: '0.03em' }}>
              {badgeLabel}
            </span>
            <span style={{ fontSize: '0.8rem', color: 'var(--color-text-tertiary)' }}>
              Source: {sourceLabel}
            </span>
          </div>
        </div>
      </div>
      
      {expanded && (
        <div style={{ padding: '0 16px 16px 48px', background: 'var(--color-surface)', borderTop: '1px solid var(--color-border-hover)' }}>
          {isDeterministic ? (
            <div style={{ marginTop: '12px' }}>
              <h4 style={{ fontSize: '0.85rem', color: 'var(--color-text-tertiary)', textTransform: 'uppercase', margin: '12px 0 8px 0', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Cpu size={16} /> Deterministic Reasoning Basis
              </h4>
              <p style={{ fontSize: '0.9rem', color: 'var(--color-text-secondary)', margin: '0 0 8px 0' }}>
                This relationship is established through ecological domain rules, baseline threshold evaluation, and risk pattern detection. It does not cite literature chunks directly.
              </p>
              {claim.reasoning_reference && (
                <div style={{ fontSize: '0.85rem', color: 'var(--color-text-tertiary)' }}>
                  Reasoning Reference: {JSON.stringify(claim.reasoning_reference)}
                </div>
              )}
            </div>
          ) : hasEvidenceChunks ? (
            <div>
              <h4 style={{ fontSize: '0.85rem', color: 'var(--color-text-tertiary)', textTransform: 'uppercase', margin: '16px 0 12px 0', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <BookOpen size={16} /> Supporting Scientific Evidence
              </h4>
              
              {claim.evidence!.map((ev, idx) => (
                <div key={idx} style={{ marginBottom: '16px', padding: '12px', background: 'var(--color-background)', borderRadius: 'var(--radius-sm)' }}>
                  <div style={{ fontWeight: 600, color: 'var(--color-primary-dark)', fontSize: '0.95rem', marginBottom: '4px' }}>
                    {ev.source || 'Peer-Reviewed Source'}
                  </div>
                  <div style={{ fontSize: '0.9rem', color: 'var(--color-text-secondary)', marginBottom: '8px', fontStyle: 'italic' }}>
                    {ev.document || 'Scientific literature publication'} {ev.year ? `(${ev.year})` : ''}
                  </div>
                  <div style={{ display: 'flex', gap: '16px', fontSize: '0.85rem', color: 'var(--color-text-tertiary)', marginBottom: '12px', flexWrap: 'wrap' }}>
                    {ev.chunk_id && <span>Chunk ID: {ev.chunk_id.substring(0, 8)}...</span>}
                    {ev.page_number && <span>Page: {ev.page_number}</span>}
                    {ev.section && <span>Section: {ev.section}</span>}
                  </div>
                  
                  {ev.url && (
                    <a href={ev.url} target="_blank" rel="noopener noreferrer" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '0.85rem', fontWeight: 600 }}>
                      <ExternalLink size={14} /> View Source
                    </a>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div style={{ marginTop: '16px', padding: '12px', background: 'var(--color-background)', borderRadius: 'var(--radius-sm)', display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
              <AlertCircle size={18} color="var(--color-warning)" style={{ marginTop: '2px', flexShrink: 0 }} />
              <div style={{ fontSize: '0.88rem', color: 'var(--color-text-secondary)' }}>
                <strong>Insufficient Scientific Evidence:</strong> No indexed peer-reviewed scientific literature chunks were found to directly corroborate this mechanism. The system preserves uncertainty honestly rather than fabricating citations.
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
