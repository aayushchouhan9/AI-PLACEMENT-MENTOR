import React, { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import { ScoreBreakdown } from '../components/ScoreBreakdown';

export function ResumePage() {
  const [analysis, setAnalysis] = useState(null);
  const [pasteText, setPasteText] = useState('');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState('');

  useEffect(() => {
    fetchLatestAnalysis();
  }, []);

  const fetchLatestAnalysis = async () => {
    try {
      const res = await apiClient.get('/api/resume/latest');
      if (res.data.has_resume) {
        setAnalysis(res.data);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    setMsg('');
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await apiClient.post('/api/resume/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setAnalysis(res.data);
      setMsg("Resume analyzed successfully!");
    } catch (err) {
      setMsg(err.response?.data?.detail || "File parse failed. Please use text paste fallback below.");
    } finally {
      setLoading(false);
    }
  };

  const handlePasteSubmit = async (e) => {
    e.preventDefault();
    if (!pasteText.strip()) return;
    setLoading(true);
    setMsg('');
    try {
      const res = await apiClient.post('/api/resume/paste', { raw_text: pasteText });
      setAnalysis(res.data);
      setMsg("Pasted resume analyzed successfully!");
    } catch (err) {
      setMsg(err.response?.data?.detail || "Parsing failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div className="card">
        <h3>Resume Intelligence & Quality Analysis</h3>
        <p style={{ color: 'var(--text-muted)' }}>
          Upload your PDF or DOCX resume, or use plain-text paste. Extracted skills update your profile with source traceability.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginTop: '1.5rem' }}>
          {/* File Upload Form */}
          <form onSubmit={handleFileUpload} style={{ background: 'var(--bg-card-hover)', padding: '1.25rem', borderRadius: 'var(--radius-md)' }}>
            <h4>Option A: File Upload (PDF / DOCX)</h4>
            <div className="form-group" style={{ marginTop: '1rem' }}>
              <input type="file" accept=".pdf,.docx" onChange={e => setFile(e.target.files[0])} />
            </div>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? "Analyzing..." : "Upload & Analyze Resume"}
            </button>
          </form>

          {/* Plain Text Paste Fallback */}
          <form onSubmit={handlePasteSubmit} style={{ background: 'var(--bg-card-hover)', padding: '1.25rem', borderRadius: 'var(--radius-md)' }}>
            <h4>Option B: Plain Text Paste Fallback</h4>
            <div className="form-group" style={{ marginTop: '1rem' }}>
              <textarea className="form-textarea" rows={3} value={pasteText} onChange={e => setPasteText(e.target.value)} placeholder="Paste your raw resume text here..." />
            </div>
            <button type="submit" className="btn btn-secondary" disabled={loading}>
              {loading ? "Analyzing..." : "Analyze Pasted Text"}
            </button>
          </form>
        </div>

        {msg && <div style={{ marginTop: '1rem', color: msg.includes('failed') ? 'var(--danger)' : 'var(--success)' }}>{msg}</div>}
      </div>

      {analysis && (
        <div className="card animate-fade-in">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h2>Resume Quality Score: <span style={{ color: 'var(--primary)' }}>{analysis.overall_score}/100</span></h2>
              <p style={{ color: 'var(--text-muted)' }}>{analysis.file_name || 'Analyzed Resume'}</p>
            </div>
          </div>

          <ScoreBreakdown factorBreakdown={analysis.factor_breakdown} />

          {/* Opt-in AI Bullet Rewrites */}
          <div style={{ marginTop: '2rem' }}>
            <h4>Opt-in AI Suggested Bullet Rewrites</h4>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
              Suggestions rephrase existing achievements without introducing ungrounded facts. Review each individually (no auto-apply).
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {(analysis.suggested_rewrites || []).map((rw, idx) => (
                <div key={idx} style={{ background: 'var(--bg-card-hover)', padding: '1rem', borderRadius: 'var(--radius-sm)', borderLeft: '4px solid var(--accent)' }}>
                  <div><strong>Original:</strong> {rw.original_bullet}</div>
                  <div style={{ color: 'var(--success)', marginTop: '0.5rem' }}><strong>Suggested:</strong> {rw.suggested_rewrite}</div>
                  <div style={{ marginTop: '0.75rem', display: 'flex', gap: '0.5rem' }}>
                    <button className="btn btn-primary" style={{ padding: '0.25rem 0.75rem', fontSize: '0.8rem' }} onClick={() => alert("Accepted suggestion!")}>Accept</button>
                    <button className="btn btn-secondary" style={{ padding: '0.25rem 0.75rem', fontSize: '0.8rem' }} onClick={() => alert("Rejected suggestion.")}>Reject</button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
