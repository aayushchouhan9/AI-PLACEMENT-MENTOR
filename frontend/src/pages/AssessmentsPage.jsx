import React, { useState, useEffect } from 'react';
import { apiClient } from '../api/client';

export function AssessmentsPage() {
  const [assessments, setAssessments] = useState([]);
  const [selectedAssessment, setSelectedAssessment] = useState(null);
  const [userAnswers, setUserAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchAssessments();
  }, []);

  const fetchAssessments = async () => {
    try {
      const res = await apiClient.get('/api/assessments');
      setAssessments(res.data || []);
    } catch (err) {
      console.error(err);
    }
  };

  const startAssessment = async (id) => {
    try {
      const res = await apiClient.get(`/api/assessments/${id}`);
      setSelectedAssessment(res.data);
      setUserAnswers({});
      setResult(null);
    } catch (err) {
      alert("Failed to load assessment.");
    }
  };

  const handleSelectOption = (qId, option) => {
    setUserAnswers(prev => ({ ...prev, [qId]: option }));
  };

  const handleSubmit = async () => {
    if (!selectedAssessment) return;
    setLoading(true);
    try {
      const answersPayload = Object.entries(userAnswers).map(([qId, opt]) => ({
        question_id: qId,
        selected_option: opt
      }));

      const res = await apiClient.post(`/api/assessments/${selectedAssessment.id}/submit`, {
        answers: answersPayload,
        time_taken_seconds: 120
      });
      setResult(res.data);
    } catch (err) {
      alert("Submission failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div className="card">
        <h3>Curated Skill Assessments</h3>
        <p style={{ color: 'var(--text-muted)' }}>
          Assessment grading is 100% deterministic and curated. Scoring updates your verified skills and feeds placement readiness.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: '1.5rem' }}>
          {assessments.map(ass => (
            <div key={ass.id} style={{ background: 'var(--bg-card-hover)', padding: '1.25rem', borderRadius: 'var(--radius-md)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <span className="badge badge-primary">{ass.difficulty_tier}</span>
                <h4 style={{ marginTop: '0.5rem' }}>{ass.title}</h4>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>{ass.description}</p>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)', marginTop: '0.5rem' }}>
                  Skill: <strong>{ass.skill_name}</strong> | Time Limit: {ass.time_limit_minutes} mins
                </div>
              </div>
              <button className="btn btn-primary" style={{ marginTop: '1rem' }} onClick={() => startAssessment(ass.id)}>
                Start Assessment
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Assessment Modal / View */}
      {selectedAssessment && (
        <div className="modal-overlay">
          <div className="modal-content animate-fade-in">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h2>{selectedAssessment.title}</h2>
              <button className="btn btn-secondary" onClick={() => setSelectedAssessment(null)}>Close</button>
            </div>

            {!result ? (
              <div style={{ marginTop: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                {selectedAssessment.questions.map((q, idx) => (
                  <div key={q.id} style={{ background: 'var(--bg-dark)', padding: '1rem', borderRadius: 'var(--radius-sm)' }}>
                    <strong>Q{idx + 1}: {q.question_text}</strong>
                    <div style={{ marginTop: '0.75rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                      {q.options.map((opt, oIdx) => (
                        <label key={oIdx} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                          <input 
                            type="radio" 
                            name={`q_${q.id}`} 
                            value={opt} 
                            checked={userAnswers[q.id] === opt} 
                            onChange={() => handleSelectOption(q.id, opt)} 
                          />
                          <span>{opt}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                ))}
                <button className="btn btn-primary" onClick={handleSubmit} disabled={loading}>
                  {loading ? "Grading..." : "Submit Assessment"}
                </button>
              </div>
            ) : (
              <div style={{ marginTop: '1.5rem' }}>
                <div style={{ background: 'rgba(16,185,129,0.15)', border: '1px solid var(--success)', padding: '1rem', borderRadius: 'var(--radius-md)' }}>
                  <h3 style={{ color: 'var(--success)' }}>Assessment Completed!</h3>
                  <h2>Score: {result.score}/{result.max_score} ({result.percentage}%)</h2>
                  <p style={{ marginTop: '0.25rem' }}>
                    Skill <strong>{result.skill_updated.skill_name}</strong> updated to <strong>{result.skill_updated.new_proficiency}%</strong> ({result.skill_updated.provenance}).
                  </p>
                </div>

                <div style={{ marginTop: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  <h4>Detailed Explanations:</h4>
                  {result.answers.map((ans, idx) => (
                    <div key={idx} style={{ background: 'var(--bg-dark)', padding: '0.75rem 1rem', borderRadius: 'var(--radius-sm)', borderLeft: `4px solid ${ans.is_correct ? 'var(--success)' : 'var(--danger)'}` }}>
                      <div><strong>Q: {ans.question_text}</strong></div>
                      <div>Your answer: {ans.selected_option} | Correct: {ans.correct_answer}</div>
                      <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>Explanation: {ans.explanation}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
