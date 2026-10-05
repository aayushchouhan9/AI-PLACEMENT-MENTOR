import React, { useState, useEffect } from 'react';
import { apiClient } from '../api/client';

export function RoadmapPage() {
  const [tasks, setTasks] = useState([]);
  const [newTitle, setNewTitle] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [msg, setMsg] = useState('');

  useEffect(() => {
    fetchRoadmap();
  }, []);

  const fetchRoadmap = async () => {
    try {
      const res = await apiClient.get('/api/roadmap');
      setTasks(res.data || []);
    } catch (err) {
      console.error(err);
    }
  };

  const handleRegenerate = async () => {
    try {
      const res = await apiClient.post('/api/roadmap/generate');
      setMsg(res.data.message);
      fetchRoadmap();
    } catch (err) {
      alert("Failed to regenerate roadmap.");
    }
  };

  const updateStatus = async (taskId, newStatus) => {
    try {
      await apiClient.put(`/api/roadmap/tasks/${taskId}`, { status: newStatus });
      fetchRoadmap();
    } catch (err) {
      alert("Failed to update status.");
    }
  };

  const handleAddTask = async (e) => {
    e.preventDefault();
    if (!newTitle.trim()) return;
    try {
      await apiClient.post('/api/roadmap/tasks', { title: newTitle, description: newDesc });
      setNewTitle('');
      setNewDesc('');
      fetchRoadmap();
    } catch (err) {
      alert("Failed to add task.");
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h3>Adaptive Preparation Roadmap</h3>
            <p style={{ color: 'var(--text-muted)' }}>
              Personalized roadmap derived from your skill gaps. You retain 100% control: accept, skip, or reorder tasks.
            </p>
          </div>
          <button className="btn btn-primary" onClick={handleRegenerate}>Regenerate Roadmap</button>
        </div>

        {msg && <div style={{ marginTop: '1rem', color: 'var(--success)' }}>{msg}</div>}

        <div style={{ marginTop: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {tasks.map(t => (
            <div key={t.id} style={{ background: 'var(--bg-card-hover)', padding: '1rem 1.25rem', borderRadius: 'var(--radius-sm)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <strong style={{ color: '#fff', textDecoration: t.status === 'completed' ? 'line-through' : 'none' }}>{t.title}</strong>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>{t.description}</p>
                <div style={{ marginTop: '0.4rem', display: 'flex', gap: '0.5rem' }}>
                  <span className={`badge badge-${t.status === 'completed' ? 'success' : (t.status === 'skipped_by_student' ? 'danger' : 'warning')}`}>
                    {t.status}
                  </span>
                  <span className="badge badge-primary">{t.priority} priority</span>
                </div>
              </div>

              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <button className="btn btn-secondary" style={{ fontSize: '0.8rem' }} onClick={() => updateStatus(t.id, 'completed')}>Done</button>
                <button className="btn btn-secondary" style={{ fontSize: '0.8rem' }} onClick={() => updateStatus(t.id, 'in_progress')}>In Progress</button>
                <button className="btn btn-secondary" style={{ fontSize: '0.8rem', color: 'var(--danger)' }} onClick={() => updateStatus(t.id, 'skipped_by_student')}>Skip</button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <h4>Add Custom Roadmap Task</h4>
        <form onSubmit={handleAddTask} style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
          <input className="form-input" placeholder="Task Title" value={newTitle} onChange={e => setNewTitle(e.target.value)} required />
          <input className="form-input" placeholder="Description" value={newDesc} onChange={e => setNewDesc(e.target.value)} />
          <button type="submit" className="btn btn-primary" style={{ whiteSpace: 'nowrap' }}>Add Task</button>
        </form>
      </div>
    </div>
  );
}
