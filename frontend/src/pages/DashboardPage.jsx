import React, { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import { ScoreBreakdown } from '../components/ScoreBreakdown';

export function DashboardPage() {
  const [readiness, setReadiness] = useState(null);
  const [gaps, setGaps] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [readinessRes, gapsRes, recsRes] = await Promise.all([
        apiClient.get('/api/readiness'),
        apiClient.get('/api/skill-gaps'),
        apiClient.get('/api/recommendations')
      ]);
      setReadiness(readinessRes.data);
      setGaps(gapsRes.data.gaps || []);
      setRecommendations(recsRes.data || []);
    } catch (err) {
      console.error("Failed to load dashboard data:", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div style={{ padding: '2rem', color: 'var(--text-muted)' }}>Loading dashboard...</div>;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Overall Readiness Header Card */}
      <div className="card" style={{ background: 'linear-gradient(135deg, rgba(99,102,241,0.15), rgba(139,92,246,0.15))', border: '1px solid rgba(99,102,241,0.3)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <span className="badge badge-primary">Current Target Role: {readiness?.target_role || 'Role-Agnostic Core'}</span>
            <h1 style={{ fontSize: '2.5rem', marginTop: '0.5rem', color: '#fff' }}>
              Readiness Score: <span style={{ color: 'var(--primary)', fontWeight: '800' }}>{readiness?.overall_score}%</span>
            </h1>
            <p style={{ color: 'var(--text-muted)', marginTop: '0.25rem' }}>
              Calculated deterministically from your resume, skill assessments, roadmap, and mock interviews.
            </p>
          </div>
          <button className="btn btn-primary" onClick={fetchDashboardData}>Recalculate Readiness</button>
        </div>

        <ScoreBreakdown factorBreakdown={readiness?.factor_breakdown} formulaVersion={readiness?.formula_version} />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        {/* Top Skill Gaps */}
        <div className="card">
          <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span>⚡</span> Top Skill Gaps
          </h3>
          {gaps.length === 0 ? (
            <p style={{ color: 'var(--text-muted)' }}>No skill gaps identified. Select a target role in Profile to calculate gaps!</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {gaps.slice(0, 4).map((gap, idx) => (
                <div key={idx} style={{ background: 'var(--bg-card-hover)', padding: '0.75rem 1rem', borderRadius: 'var(--radius-sm)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <strong style={{ color: '#fff' }}>{gap.skill_name}</strong>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      Current: {gap.current_proficiency}% | Required: {gap.required_proficiency}%
                    </div>
                  </div>
                  <span className={`badge badge-${gap.priority_urgency === 'high' ? 'danger' : 'warning'}`}>
                    {gap.priority_urgency} gap
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Today's Recommended Actions */}
        <div className="card">
          <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span>🎯</span> Recommended Actions
          </h3>
          {recommendations.length === 0 ? (
            <p style={{ color: 'var(--text-muted)' }}>No recommendations generated yet.</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {recommendations.slice(0, 3).map((rec, idx) => (
                <div key={idx} style={{ background: 'var(--bg-card-hover)', padding: '0.75rem 1rem', borderRadius: 'var(--radius-sm)' }}>
                  <div style={{ fontWeight: '600', color: 'var(--primary)' }}>{rec.title}</div>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                    {rec.phrased_description || rec.description}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
