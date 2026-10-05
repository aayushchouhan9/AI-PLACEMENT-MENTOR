import React, { useState } from 'react';
import { apiClient } from '../api/client';

export function InterviewsPage() {
  const [session, setSession] = useState(null);
  const [answers, setAnswers] = useState({});
  const [feedbacks, setFeedbacks] = useState({});
  const [summary, setSummary] = useState(null);
  const [errMsg, setErrMsg] = useState('');
  const [loading, setLoading] = useState(false);

  const startSession = async (type) => {
    setErrMsg('');
    setSummary(null);
    setFeedbacks({});
    setAnswers({});
    try {
      const res = await apiClient.post('/api/interviews/start', { interview_type: type });
      setSession(res.data);
    } catch (err) {
      setErrMsg(err.response?.data?.detail || "Failed to start interview session.");
    }
  };

  const handleAnswerSubmit = async (qId) => {
    const text = answers[qId];
    if (!text || !text.trim()) return;
    setLoading(true);
    try {
      const res = await apiClient.post(`/api/interviews/${session.interview_id}/answer`, {
        question_id: qId,
        answer_text: text
      });
      setFeedbacks(prev => ({ ...prev, [qId]: res.data }));
    } catch (err) {
      alert("Failed to evaluate answer.");
    } finally {
      setLoading(false);
    }
  };

  const handleCompleteSession = async () => {
    if (!session) return;
    try {
      const res = await apiClient.post(`/api/interviews/${session.interview_id}/complete`);
      setSummary(res.data);
    } catch (err) {
      alert("Failed to complete interview.");
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div className="card">
        <h3>Text-Based Mock Interviews</h3>
        <p style={{ color: 'var(--text-muted)' }}>
          Practice technical & behavioral questions, or defend your own structured projects under AI evaluation.
        </p>

        {errMsg && (
          <div style={{ marginTop: '1rem', background: 'rgba(239,68,68,0.15)', border: '1px solid var(--danger)', padding: '1rem', borderRadius: 'var(--radius-sm)', color: '#f87171' }}>
            {errMsg}
          </div>
        )}

        {!session && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginTop: '1.5rem' }}>
            <div style={{ background: 'var(--bg-card-hover)', padding: '1.5rem', borderRadius: 'var(--radius-md)' }}>
              <h4>General Mock Interview</h4>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                Curated technical and behavioral questions tailored to target roles.
              </p>
              <button className="btn btn-primary" style={{ marginTop: '1rem' }} onClick={() => startSession('general')}>
                Start General Interview
              </button>
            </div>

            <div style={{ background: 'var(--bg-card-hover)', padding: '1.5rem', borderRadius: 'var(--radius-md)' }}>
              <h4>Project Defense Mode</h4>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                Rule-grounded questions built directly from your structured project entries.
              </p>
              <button className="btn btn-primary" style={{ marginTop: '1rem' }} onClick={() => startSession('project_defense')}>
                Start Project Defense
              </button>
            </div>
          </div>
        )}
      </div>

      {session && (
        <div className="card animate-fade-in">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3>Mock Interview Session ({session.interview_type.toUpperCase()})</h3>
            <button className="btn btn-secondary" onClick={() => setSession(null)}>Exit Session</button>
          </div>

          <div style={{ marginTop: '1.5rem', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
            {session.questions.map((q, idx) => (
              <div key={q.id} style={{ background: 'var(--bg-dark)', padding: '1.25rem', borderRadius: 'var(--radius-md)' }}>
                <strong style={{ fontSize: '1.05rem' }}>Q{idx + 1}: {q.text}</strong>
                {q.grounded_project_fields && (
                  <div style={{ fontSize: '0.75rem', color: 'var(--accent)', marginTop: '0.25rem' }}>
                    Grounded in project field(s): {q.grounded_project_fields.join(', ')}
                  </div>
                )}

                <div className="form-group" style={{ marginTop: '1rem' }}>
                  <textarea 
                    className="form-textarea" 
                    rows={3} 
                    placeholder="Type your response here..." 
                    value={answers[q.id] || ''} 
                    onChange={e => setAnswers({ ...answers, [q.id]: e.target.value })} 
                  />
                </div>

                <button className="btn btn-secondary" onClick={() => handleAnswerSubmit(q.id)} disabled={loading}>
                  Submit Answer for AI Feedback
                </button>

                {feedbacks[q.id] && (
                  <div style={{ marginTop: '1rem', background: 'var(--bg-card-hover)', padding: '1rem', borderRadius: 'var(--radius-sm)', borderLeft: '4px solid var(--primary)' }}>
                    <div style={{ fontWeight: '700', color: 'var(--primary)' }}>Score: {feedbacks[q.id].score}/100</div>
                    <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>{feedbacks[q.id].feedback_text}</p>
                  </div>
                )}
              </div>
            ))}

            <div style={{ textAlign: 'right' }}>
              <button className="btn btn-primary" onClick={handleCompleteSession}>Complete Session & View Summary</button>
            </div>
          </div>
        </div>
      )}

      {summary && (
        <div className="card animate-fade-in" style={{ background: 'linear-gradient(135deg, rgba(16,185,129,0.15), rgba(6,182,212,0.15))', border: '1px solid var(--success)' }}>
          <h2 style={{ color: 'var(--success)' }}>Interview Session Completed!</h2>
          <h1>Overall Performance Score: {summary.overall_score}/100</h1>
          <p style={{ marginTop: '0.5rem', color: 'var(--text-main)' }}>{summary.summary_feedback}</p>
        </div>
      )}
    </div>
  );
}
