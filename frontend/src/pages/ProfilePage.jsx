import React, { useState, useEffect } from 'react';
import { apiClient } from '../api/client';

export function ProfilePage() {
  const [profile, setProfile] = useState(null);
  const [projects, setProjects] = useState([]);
  const [newProj, setNewProj] = useState({
    name: '',
    one_line_summary: '',
    role: '',
    tech_stack: '',
    architectural_decisions: '',
    challenges_faced: '',
    tradeoffs_made: ''
  });
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchProfileData();
  }, []);

  const fetchProfileData = async () => {
    try {
      const res = await apiClient.get('/api/profile');
      setProfile(res.data);
      setProjects(res.data.projects || []);
    } catch (err) {
      console.error("Error fetching profile:", err);
    }
  };

  const handleCreateProject = async (e) => {
    e.preventDefault();
    try {
      const techList = newProj.tech_stack.split(',').map(s => s.trim()).filter(Boolean);
      await apiClient.post('/api/profile/projects', {
        ...newProj,
        tech_stack: techList
      });
      setMessage("Project created successfully!");
      setNewProj({
        name: '',
        one_line_summary: '',
        role: '',
        tech_stack: '',
        architectural_decisions: '',
        challenges_faced: '',
        tradeoffs_made: ''
      });
      fetchProfileData();
    } catch (err) {
      setMessage("Failed to create project.");
    }
  };

  const handleExportData = async () => {
    try {
      const res = await apiClient.get('/api/profile/export');
      const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(res.data, null, 2));
      const downloadAnchor = document.createElement('a');
      downloadAnchor.setAttribute("href", dataStr);
      downloadAnchor.setAttribute("download", "my_placement_mentor_data.json");
      document.body.appendChild(downloadAnchor);
      downloadAnchor.click();
      downloadAnchor.remove();
    } catch (err) {
      alert("Failed to export data.");
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div className="card">
        <h3>Student Profile</h3>
        {profile && (
          <div style={{ marginTop: '1rem', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div><strong>Full Name:</strong> {profile.full_name}</div>
            <div><strong>Email:</strong> {profile.email}</div>
            <div><strong>Branch:</strong> {profile.branch || 'Not set'}</div>
            <div><strong>Graduation Year:</strong> {profile.graduation_year || 'Not set'}</div>
          </div>
        )}
        <div style={{ marginTop: '1.5rem', display: 'flex', gap: '1rem' }}>
          <button className="btn btn-secondary" onClick={handleExportData}>Export Machine-Readable Data (JSON)</button>
        </div>
      </div>

      {/* Structured Project Intake (FR-43, Section 6.2) */}
      <div className="card">
        <h3>Structured Project Intake</h3>
        <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
          Structured project entries are required to unlock Project Defense Mock Interview mode.
        </p>

        <form onSubmit={handleCreateProject} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label">Project Name</label>
              <input className="form-input" value={newProj.name} onChange={e => setNewProj({...newProj, name: e.target.value})} required />
            </div>
            <div className="form-group">
              <label className="form-label">Your Role</label>
              <input className="form-input" value={newProj.role} onChange={e => setNewProj({...newProj, role: e.target.value})} required />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">One-Line Summary</label>
            <input className="form-input" value={newProj.one_line_summary} onChange={e => setNewProj({...newProj, one_line_summary: e.target.value})} required />
          </div>

          <div className="form-group">
            <label className="form-label">Tech Stack (comma separated)</label>
            <input className="form-input" value={newProj.tech_stack} onChange={e => setNewProj({...newProj, tech_stack: e.target.value})} placeholder="Python, FastAPI, React, PostgreSQL" required />
          </div>

          <div className="form-group">
            <label className="form-label">Key Architectural / Design Decisions</label>
            <textarea className="form-textarea" rows={2} value={newProj.architectural_decisions} onChange={e => setNewProj({...newProj, architectural_decisions: e.target.value})} required />
          </div>

          <div className="form-group">
            <label className="form-label">Challenges Faced</label>
            <textarea className="form-textarea" rows={2} value={newProj.challenges_faced} onChange={e => setNewProj({...newProj, challenges_faced: e.target.value})} required />
          </div>

          <div className="form-group">
            <label className="form-label">Trade-offs Made</label>
            <textarea className="form-textarea" rows={2} value={newProj.tradeoffs_made} onChange={e => setNewProj({...newProj, tradeoffs_made: e.target.value})} required />
          </div>

          <button type="submit" className="btn btn-primary">Save Project Entry</button>
        </form>

        {message && <div style={{ marginTop: '1rem', color: 'var(--success)' }}>{message}</div>}

        <div style={{ marginTop: '2rem' }}>
          <h4>Your Saved Projects ({projects.length})</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1rem' }}>
            {projects.map(p => (
              <div key={p.id} style={{ background: 'var(--bg-card-hover)', padding: '1rem', borderRadius: 'var(--radius-sm)' }}>
                <strong>{p.name}</strong> <span style={{ color: 'var(--text-muted)' }}>({p.role})</span>
                <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>{p.one_line_summary}</p>
                <div style={{ marginTop: '0.5rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                  {(p.tech_stack || []).map((tech, idx) => (
                    <span key={idx} className="badge badge-primary">{tech}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
