import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '../api/client';

export function LoginPage({ onLoginSuccess }) {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [branch, setBranch] = useState('Computer Science & Engineering');
  const [graduationYear, setGraduationYear] = useState('2026');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const res = await apiClient.post('/api/auth/login', {
        email: email.trim(),
        password: password
      });

      handleAuthSuccess(res.data);
    } catch (err) {
      console.error('Login failed:', err);
      setError(err.response?.data?.detail || 'Invalid email or password. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const res = await apiClient.post('/api/auth/register', {
        email: email.trim(),
        password: password,
        full_name: fullName.trim(),
        branch: branch.trim(),
        graduation_year: parseInt(graduationYear, 10) || 2026
      });

      handleAuthSuccess(res.data);
    } catch (err) {
      console.error('Registration failed:', err);
      setError(err.response?.data?.detail || 'Failed to create account. Please check your details.');
    } finally {
      setLoading(false);
    }
  };

  const handleAuthSuccess = (data) => {
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('user_name', data.full_name);
    localStorage.setItem('user_email', data.email);
    localStorage.setItem('user_id', data.user_id);
    if (onLoginSuccess) {
      onLoginSuccess(data);
    }
    navigate('/');
  };

  const handleFillDemo = (e) => {
    e.preventDefault();
    setIsRegister(false);
    setEmail('demo@placementmentor.com');
    setPassword('password123');
    setError('');
  };

  const handleQuickDemoLogin = async () => {
    setError('');
    setLoading(true);
    try {
      const res = await apiClient.post('/api/auth/login', {
        email: 'demo@placementmentor.com',
        password: 'password123'
      });
      handleAuthSuccess(res.data);
    } catch (err) {
      console.error('Demo login failed:', err);
      setError('Demo account unavailable or server offline.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'radial-gradient(circle at top right, rgba(99, 102, 241, 0.2), transparent 50%), radial-gradient(circle at bottom left, rgba(6, 182, 212, 0.15), transparent 50%), var(--bg-dark)',
      padding: '2rem 1rem',
      position: 'relative'
    }}>
      <div style={{
        width: '100%',
        maxWidth: '480px',
        background: 'var(--bg-glass)',
        backdropFilter: 'blur(16px)',
        border: '1px solid var(--border-color)',
        borderRadius: 'var(--radius-lg)',
        padding: '2.5rem',
        boxShadow: 'var(--shadow-lg)'
      }}>
        {/* Brand header */}
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '56px',
            height: '56px',
            borderRadius: '16px',
            background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.3), rgba(139, 92, 246, 0.3))',
            border: '1px solid rgba(99, 102, 241, 0.4)',
            fontSize: '1.75rem',
            marginBottom: '1rem'
          }}>
            🎯
          </div>
          <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#fff' }}>
            AI Placement Mentor
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.35rem' }}>
            {isRegister
              ? 'Create your account to start continuous placement mentoring'
              : 'Sign in to access your personalized placement roadmap'}
          </p>
        </div>

        {/* Tab switch */}
        <div style={{
          display: 'flex',
          background: 'var(--bg-dark)',
          borderRadius: 'var(--radius-md)',
          padding: '0.3rem',
          marginBottom: '1.5rem',
          border: '1px solid var(--border-color)'
        }}>
          <button
            type="button"
            onClick={() => { setIsRegister(false); setError(''); }}
            style={{
              flex: 1,
              padding: '0.6rem',
              borderRadius: 'var(--radius-sm)',
              border: 'none',
              background: !isRegister ? 'var(--primary)' : 'transparent',
              color: !isRegister ? '#fff' : 'var(--text-muted)',
              fontWeight: 600,
              fontSize: '0.9rem',
              cursor: 'pointer',
              transition: 'var(--transition)'
            }}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => { setIsRegister(true); setError(''); }}
            style={{
              flex: 1,
              padding: '0.6rem',
              borderRadius: 'var(--radius-sm)',
              border: 'none',
              background: isRegister ? 'var(--primary)' : 'transparent',
              color: isRegister ? '#fff' : 'var(--text-muted)',
              fontWeight: 600,
              fontSize: '0.9rem',
              cursor: 'pointer',
              transition: 'var(--transition)'
            }}
          >
            Sign Up
          </button>
        </div>

        {/* Error notification */}
        {error && (
          <div style={{
            background: 'rgba(239, 68, 68, 0.15)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            color: '#f87171',
            padding: '0.75rem 1rem',
            borderRadius: 'var(--radius-sm)',
            fontSize: '0.875rem',
            marginBottom: '1.25rem'
          }}>
            {error}
          </div>
        )}

        <form onSubmit={isRegister ? handleRegister : handleLogin}>
          {isRegister && (
            <>
              <div className="form-group">
                <label className="form-label">Full Name</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. Alex Sharma"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  required
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '0.75rem' }}>
                <div className="form-group">
                  <label className="form-label">Branch / Major</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g. CSE / IT / ECE"
                    value={branch}
                    onChange={(e) => setBranch(e.target.value)}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Grad Year</label>
                  <input
                    type="number"
                    className="form-input"
                    placeholder="2026"
                    value={graduationYear}
                    onChange={(e) => setGraduationYear(e.target.value)}
                    required
                  />
                </div>
              </div>
            </>
          )}

          <div className="form-group">
            <label className="form-label">Email Address</label>
            <input
              type="email"
              className="form-input"
              placeholder="student@college.edu"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              type="password"
              className="form-input"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', marginTop: '0.75rem', padding: '0.85rem' }}
            disabled={loading}
          >
            {loading ? 'Processing...' : (isRegister ? 'Create Account' : 'Sign In')}
          </button>
        </form>

        {/* Demo Fast Login Divider */}
        <div style={{
          position: 'relative',
          textAlign: 'center',
          margin: '1.75rem 0 1.25rem 0'
        }}>
          <div style={{
            position: 'absolute',
            top: '50%',
            left: 0,
            right: 0,
            height: '1px',
            background: 'var(--border-color)'
          }} />
          <span style={{
            position: 'relative',
            background: 'var(--bg-card)',
            padding: '0 0.75rem',
            color: 'var(--text-dim)',
            fontSize: '0.8rem',
            textTransform: 'uppercase',
            letterSpacing: '0.5px'
          }}>
            Quick Testing
          </span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={handleQuickDemoLogin}
            disabled={loading}
            style={{ width: '100%' }}
          >
            🚀 One-Click Demo Student Login
          </button>

          <button
            type="button"
            onClick={handleFillDemo}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-muted)',
              fontSize: '0.8rem',
              cursor: 'pointer',
              textDecoration: 'underline'
            }}
          >
            Prefill demo credentials (demo@placementmentor.com / password123)
          </button>
        </div>
      </div>
    </div>
  );
}
