import React, { useState, useEffect } from 'react';
import { apiClient } from '../api/client';

export function RolesPage() {
  const [roles, setRoles] = useState([]);
  const [selectedRole, setSelectedRole] = useState(null);
  const [msg, setMsg] = useState('');

  useEffect(() => {
    fetchRoles();
  }, []);

  const fetchRoles = async () => {
    try {
      const res = await apiClient.get('/api/roles');
      setRoles(res.data || []);
    } catch (err) {
      console.error(err);
    }
  };

  const viewRoleDetails = async (id) => {
    try {
      const res = await apiClient.get(`/api/roles/${id}`);
      setSelectedRole(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const selectTargetRole = async (roleId) => {
    try {
      const res = await apiClient.post('/api/roles/select', { role_id: roleId });
      setMsg(res.data.message);
    } catch (err) {
      alert("Failed to set target role.");
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div className="card">
        <h3>Target Role Archetypes</h3>
        <p style={{ color: 'var(--text-muted)' }}>
          Curated job archetypes with essential & optional skill requirements. Selecting a role drives skill-gap analysis & adaptive roadmaps.
        </p>

        {msg && <div style={{ marginTop: '1rem', color: 'var(--success)' }}>{msg}</div>}

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: '1.5rem' }}>
          {roles.map(r => (
            <div key={r.id} style={{ background: 'var(--bg-card-hover)', padding: '1.25rem', borderRadius: 'var(--radius-md)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <span className="badge badge-primary">{r.typical_experience_level}</span>
                <h4 style={{ marginTop: '0.5rem' }}>{r.title}</h4>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>{r.description}</p>
              </div>
              <div style={{ marginTop: '1rem', display: 'flex', gap: '0.5rem' }}>
                <button className="btn btn-primary" onClick={() => selectTargetRole(r.id)}>Select as Target Role</button>
                <button className="btn btn-secondary" onClick={() => viewRoleDetails(r.id)}>View Required Skills</button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {selectedRole && (
        <div className="card animate-fade-in">
          <h3>Required Skills for {selectedRole.title}</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '1rem' }}>
            {selectedRole.required_skills.map((sk, idx) => (
              <div key={idx} style={{ background: 'var(--bg-card-hover)', padding: '0.75rem 1rem', borderRadius: 'var(--radius-sm)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <strong>{sk.name}</strong> <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>({sk.category})</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <span>Required: <strong>{sk.required_proficiency}%</strong></span>
                  <span className={`badge badge-${sk.is_essential ? 'danger' : 'warning'}`}>
                    {sk.is_essential ? 'Essential' : 'Optional'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
