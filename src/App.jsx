import { useState, useEffect } from 'react';
import { supabase } from './supabase'; // Import client to check session
// import './App.css'; // Removed in favor of global index.css
import UserDashboard from './components/UserDashboard';
import AdminDashboard from './components/AdminDashboard';
import RegulatorDashboard from './components/RegulatorDashboard';
import Login from './components/Login'; // Import Login

function App() {
  const [session, setSession] = useState(null);
  const [role, setRole] = useState("user");

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
    });

    return () => subscription.unsubscribe();
  }, []);

  if (!session) {
    return (
      <div className="app-container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', flexDirection: 'column' }}>
        <div style={{ marginBottom: '2rem', textAlign: 'center' }}>
          <h1 style={{ fontSize: '3rem', justifyContent: 'center' }}>SAKSHAM</h1>
          <p style={{ color: 'var(--accent)', letterSpacing: '2px', textTransform: 'uppercase', fontSize: '0.8rem', opacity: 0.8 }}>Secure Authorization Manager</p>
        </div>
        <Login onLogin={setSession} />
      </div>
    );
  }

  // Pass session/token to children
  const userId = session.user.id;
  const token = session.access_token;

  return (
    <div className="app-container animate-fade-in">
      <header className="glass" style={{
        marginTop: '1.5rem',
        marginBottom: '2.5rem',
        borderRadius: '16px',
        border: '1px solid var(--border-glass)',
        padding: '0 1.5rem',
        height: 'auto',
        minHeight: '70px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '1rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <h1 style={{ margin: 0, fontSize: '1.75rem', lineHeight: 1 }}>SAKSHAM</h1>
          <span className="beta" style={{ alignSelf: 'center', marginTop: '2px' }}>BETA</span>
        </div>

        <div style={{ display: 'flex', gap: '16px', alignItems: 'center', flexWrap: 'wrap' }}>
          <div className="role-switcher" style={{ display: 'flex', alignItems: 'center', background: 'rgba(0,0,0,0.3)', padding: '4px 8px 4px 12px', borderRadius: '8px', border: '1px solid var(--border-glass)' }}>
            <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginRight: '8px', fontWeight: 500 }}>VIEW MODE</span>
            <select
              value={role}
              onChange={e => setRole(e.target.value)}
              style={{
                padding: '4px 8px',
                width: 'auto',
                border: 'none',
                background: 'transparent',
                color: 'white',
                fontSize: '0.9rem',
                cursor: 'pointer',
                outline: 'none',
                boxShadow: 'none'
              }}
            >
              <option value="user">User Dashboard</option>
              <option value="admin">App Admin</option>
              <option value="regulator">Regulator</option>
            </select>
          </div>
          <div style={{ width: '1px', height: '24px', background: 'var(--border-glass)' }}></div>
          <button
            className="secondary"
            onClick={() => supabase.auth.signOut()}
            style={{ fontSize: '0.85rem', padding: '0.5rem 1rem', border: '1px solid var(--danger)', color: 'var(--danger)', background: 'rgba(239, 68, 68, 0.1)' }}
          >
            Sign Out
          </button>
        </div>
      </header>

      <main style={{ paddingBottom: '4rem' }}>
        {role === 'user' && <UserDashboard userId={userId} token={token} />}
        {role === 'admin' && <AdminDashboard userId={userId} token={token} />}
        {role === 'regulator' && <RegulatorDashboard token={token} />}
      </main>
    </div>
  );
}

export default App;
