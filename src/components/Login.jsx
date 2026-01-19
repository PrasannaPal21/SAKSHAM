import { useState } from 'react';
import { supabase } from '../supabase';

export default function Login({ onLogin }) {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [isSignUp, setIsSignUp] = useState(false);

    const handleAuth = async (e) => {
        e.preventDefault();
        setLoading(true);
        let error;

        if (isSignUp) {
            const { error: signUpError } = await supabase.auth.signUp({
                email,
                password,
            });
            if (signUpError) error = signUpError;
            else alert('Check your email for the confirmation link!');
        } else {
            const { data, error: signInError } = await supabase.auth.signInWithPassword({
                email,
                password,
            });
            if (signInError) error = signInError;
            else if (data.session) {
                onLogin(data.session);
            }
        }

        if (error) alert(error.message);
        setLoading(false);
    };

    return (
        <div className="login-wrapper" style={{
            display: 'flex', flexDirection: 'column', gap: '1.5rem', width: '100%'
        }}>
            <div className="glass-panel" style={{ padding: '2.5rem', width: '100%', maxWidth: '400px', margin: '0 auto' }}>
                <h2 style={{ textAlign: 'center', marginBottom: '0.5rem' }}>
                    {isSignUp ? 'Create Account' : 'Welcome Back'}
                </h2>
                <p style={{ textAlign: 'center', color: 'var(--text-muted)', marginBottom: '2rem', fontSize: '0.9rem' }}>
                    {isSignUp ? 'Join the secure consent network' : 'Login to manage your privacy'}
                </p>

                <form onSubmit={handleAuth} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                    <div>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>Email Address</label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="name@example.com"
                            required
                            style={{ width: '100%' }}
                        />
                    </div>
                    <div>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="••••••••"
                            required
                            style={{ width: '100%' }}
                        />
                    </div>

                    <button type="submit" disabled={loading} style={{ marginTop: '1rem' }}>
                        {loading ? 'Processing...' : (isSignUp ? 'Sign Up' : 'Sign In')}
                    </button>
                </form>

                <div style={{ marginTop: '2rem', textAlign: 'center', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                    {isSignUp ? 'Already have an account?' : "New to SAKSHAM?"}
                    <button
                        className="text-btn"
                        onClick={() => setIsSignUp(!isSignUp)}
                        style={{
                            background: 'none', border: 'none', color: 'var(--primary)',
                            fontWeight: '600', cursor: 'pointer', padding: '0 0 0 5px',
                            boxShadow: 'none', textDecoration: 'none'
                        }}
                    >
                        {isSignUp ? 'Log in' : 'Create account'}
                    </button>
                </div>
            </div>
        </div>
    );
}
