import React, { useState, useEffect } from 'react';
import { apiClient } from '../api/client';

export function MentorPage() {
  const [messages, setMessages] = useState([
    { sender: 'mentor', text: "Hello! I am your Placement Mentor. How can I help you prepare for your target engineering role today?" }
  ]);
  const [inputMsg, setInputMsg] = useState('');
  const [facts, setFacts] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchMemoryFacts();
  }, []);

  const fetchMemoryFacts = async () => {
    try {
      const res = await apiClient.get('/api/mentor/memory-facts');
      setFacts(res.data || []);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!inputMsg.trim()) return;

    const userText = inputMsg;
    setMessages(prev => [...prev, { sender: 'user', text: userText }]);
    setInputMsg('');
    setLoading(true);

    try {
      const res = await apiClient.post('/api/mentor/chat', { message: userText });
      setMessages(prev => [...prev, { sender: 'mentor', text: res.data.reply }]);
      fetchMemoryFacts();
    } catch (err) {
      setMessages(prev => [...prev, { sender: 'mentor', text: "Apologies, I encountered an error connecting to the mentor service." }]);
    } finally {
      setLoading(false);
    }
  };

  const deleteFact = async (factId) => {
    try {
      await apiClient.delete(`/api/mentor/memory-facts/${factId}`);
      fetchMemoryFacts();
    } catch (err) {
      alert("Failed to delete memory fact.");
    }
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem' }}>
      {/* Chat Area */}
      <div className="card" style={{ display: 'flex', flexDirection: 'column', height: '75vh' }}>
        <h3>AI Placement Mentor Chat</h3>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          Conversations are grounded in your profile data. Memory facts are extracted into your profile instead of replaying raw transcripts.
        </p>

        <div style={{ flex: 1, overflowY: 'auto', padding: '1rem 0', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {messages.map((m, idx) => (
            <div key={idx} style={{
              alignSelf: m.sender === 'user' ? 'flex-end' : 'flex-start',
              maxWidth: '80%',
              background: m.sender === 'user' ? 'linear-gradient(135deg, var(--primary), var(--accent))' : 'var(--bg-card-hover)',
              padding: '0.75rem 1.25rem',
              borderRadius: 'var(--radius-md)',
              color: '#fff'
            }}>
              {m.text}
            </div>
          ))}
          {loading && <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Mentor is thinking...</div>}
        </div>

        <form onSubmit={handleSend} style={{ display: 'flex', gap: '0.5rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
          <input className="form-input" placeholder="Ask your mentor a question..." value={inputMsg} onChange={e => setInputMsg(e.target.value)} />
          <button type="submit" className="btn btn-primary" disabled={loading}>Send</button>
        </form>
      </div>

      {/* Memory Facts Sidebar */}
      <div className="card">
        <h4>Extracted Memory Facts ({facts.length})</h4>
        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
          These facts inform mentor guidance. You can view or delete any fact anytime.
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {facts.map(f => (
            <div key={f.id} style={{ background: 'var(--bg-card-hover)', padding: '0.75rem', borderRadius: 'var(--radius-sm)', position: 'relative' }}>
              <div style={{ fontSize: '0.85rem' }}>{f.fact_text}</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginTop: '0.25rem' }}>Category: {f.category}</div>
              <button 
                style={{ position: 'absolute', top: '0.5rem', right: '0.5rem', background: 'none', border: 'none', color: 'var(--danger)', cursor: 'pointer', fontSize: '0.8rem' }}
                onClick={() => deleteFact(f.id)}
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
