import React, { useState } from 'react';

export function ScoreBreakdown({ factorBreakdown, formulaVersion }) {
  const [isOpen, setIsOpen] = useState(false);

  if (!factorBreakdown) return null;

  return (
    <div style={{ marginTop: '1rem', background: 'rgba(0,0,0,0.2)', padding: '1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <strong style={{ color: 'var(--primary)' }}>Explainability Breakdown</strong>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginLeft: '0.5rem' }}>Formula v{formulaVersion || '1.0.0'}</span>
        </div>
        <button 
          className="btn btn-secondary" 
          style={{ padding: '0.25rem 0.65rem', fontSize: '0.8rem' }}
          onClick={() => setIsOpen(!isOpen)}
        >
          {isOpen ? 'Hide Factors' : 'Why this score?'}
        </button>
      </div>

      {isOpen && (
        <div className="animate-fade-in" style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {Object.entries(factorBreakdown).map(([key, factor]) => (
            <div key={key} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'var(--bg-card-hover)', padding: '0.75rem 1rem', borderRadius: 'var(--radius-sm)' }}>
              <div>
                <div style={{ fontWeight: '600', textTransform: 'capitalize' }}>{key}</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{factor.reason}</div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontWeight: '700', color: 'var(--primary)' }}>{factor.score}/100</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Weight: {Math.round((factor.weight || 0) * 100)}%</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
