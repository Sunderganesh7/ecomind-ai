import React from 'react';

type BadgeType = 'success' | 'warning' | 'danger' | 'info' | 'unknown';

interface StatusBadgeProps {
  status?: string;
  label?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, label }) => {
  let badgeClass: BadgeType = 'unknown';
  let displayLabel = label || status || 'Unknown';

  const lowerStatus = (status || '').toLowerCase();

  if (lowerStatus === 'optimal' || lowerStatus === 'supported' || lowerStatus === 'active') {
    badgeClass = 'success';
  } else if (lowerStatus === 'marginal' || lowerStatus === 'potential' || lowerStatus === 'context_dependent') {
    badgeClass = 'warning';
  } else if (lowerStatus === 'critical' || lowerStatus === 'low' || lowerStatus === 'insufficient_evidence') {
    badgeClass = 'danger';
  } else if (lowerStatus === 'informational' || lowerStatus === 'mitigated') {
    badgeClass = 'info';
  }

  if (lowerStatus === 'unknown') {
    badgeClass = 'unknown';
    displayLabel = 'Unknown';
  }

  return (
    <span className={`badge badge-${badgeClass}`}>
      {displayLabel.replace(/_/g, ' ')}
    </span>
  );
};
