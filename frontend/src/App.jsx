import React from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink, Navigate, Outlet, useNavigate } from 'react-router-dom';
import { DashboardPage } from './pages/DashboardPage';
import { ProfilePage } from './pages/ProfilePage';
import { ResumePage } from './pages/ResumePage';
import { AssessmentsPage } from './pages/AssessmentsPage';
import { RolesPage } from './pages/RolesPage';
import { RoadmapPage } from './pages/RoadmapPage';
import { MentorPage } from './pages/MentorPage';
import { InterviewsPage } from './pages/InterviewsPage';
import { LoginPage } from './pages/LoginPage';

function ProtectedRoute({ children }) {
  const token = localStorage.getItem('access_token');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

function AppLayout() {
  const navigate = useNavigate();
  const userName = localStorage.getItem('user_name') || 'Alex Sharma';
  const userEmail = localStorage.getItem('user_email') || 'demo@placementmentor.com';

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_name');
    localStorage.removeItem('user_email');
    localStorage.removeItem('user_id');
    navigate('/login');
  };

  return (
    <div className="app-container">
      <aside className="sidebar">
        <div className="brand">
          <span>🎯</span> AI Placement Mentor
        </div>
        <ul className="nav-menu">
          <li><NavLink to="/" end className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>Dashboard</NavLink></li>
          <li><NavLink to="/profile" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>Profile & Projects</NavLink></li>
          <li><NavLink to="/resume" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>Resume Intelligence</NavLink></li>
          <li><NavLink to="/assessments" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>Skill Assessments</NavLink></li>
          <li><NavLink to="/roles" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>Target Roles</NavLink></li>
          <li><NavLink to="/roadmap" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>Adaptive Roadmap</NavLink></li>
          <li><NavLink to="/mentor" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>AI Mentor</NavLink></li>
          <li><NavLink to="/interviews" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>Mock Interviews</NavLink></li>
        </ul>

        {/* User profile & Logout at bottom of sidebar */}
        <div style={{
          marginTop: 'auto',
          paddingTop: '1.25rem',
          borderTop: '1px solid var(--border-color)',
          display: 'flex',
          flexDirection: 'column',
          gap: '0.75rem'
        }}>
          <div>
            <div style={{ fontWeight: 600, fontSize: '0.9rem', color: '#fff' }}>{userName}</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {userEmail}
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="btn btn-secondary"
            style={{ width: '100%', fontSize: '0.85rem', padding: '0.5rem 0.75rem', justifyContent: 'center' }}
          >
            Sign Out
          </button>
        </div>
      </aside>

      <main className="main-content animate-fade-in">
        <Outlet />
      </main>
    </div>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        {/* Public auth routes */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<LoginPage />} />

        {/* Protected application routes */}
        <Route path="/" element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
          <Route index element={<DashboardPage />} />
          <Route path="profile" element={<ProfilePage />} />
          <Route path="resume" element={<ResumePage />} />
          <Route path="assessments" element={<AssessmentsPage />} />
          <Route path="roles" element={<RolesPage />} />
          <Route path="roadmap" element={<RoadmapPage />} />
          <Route path="mentor" element={<MentorPage />} />
          <Route path="interviews" element={<InterviewsPage />} />
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
