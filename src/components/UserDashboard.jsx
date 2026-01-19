import { useState, useEffect } from 'react';

const API_URL = "http://127.0.0.1:8000";

export default function UserDashboard({ userId, token }) {
    const [auditLog, setAuditLog] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchHistory();
    }, []);

    const fetchHistory = async () => {
        setLoading(true);
        try {
            const res = await fetch(`${API_URL}/audit/events?user_id=${userId}&limit=10`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.status === 401) { alert("Session expired or invalid"); return; }
            const data = await res.json();
            setAuditLog(data);
        } catch (e) {
            console.error(e);
        }
        setLoading(false);
    };

    const handleRevoke = async (consentId) => {
        if (!confirm("Are you sure you want to revoke this consent? This action is irreversible.")) return;

        const res = await fetch(`${API_URL}/consent/revoke`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ consent_id: consentId, reason: "User Interface Revocation" })
        });
        if (res.ok) {
            fetchHistory();
        } else {
            alert("Failed to revoke");
        }
    };

    return (
        <div className="dashboard-view">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <div>
                    <h2>My Privacy Vault</h2>
                    <p style={{ color: 'var(--text-muted)' }}>Manage your active consents and review history.</p>
                </div>
                <div className="glass" style={{ padding: '0.5rem 1rem', borderRadius: '8px', fontSize: '0.85rem' }}>
                    User ID: <span className="mono" style={{ color: 'var(--accent)' }}>{userId.substring(0, 8)}...</span>
                </div>
            </div>

            {loading ? (
                <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>Loading records...</div>
            ) : (
                <div className="dashboard-grid">
                    {auditLog.length === 0 && <p>No consent history found.</p>}
                    {auditLog.map(event => {
                        const isGrant = event.event_type === 'CONSENT_GRANTED';
                        const isRevoke = event.event_type === 'CONSENT_REVOKED';
                        return (
                            <div key={event.event_id} className="glass-panel card" style={{ position: 'relative', overflow: 'hidden' }}>
                                <div style={{
                                    position: 'absolute', top: 0, left: 0, width: '4px', height: '100%',
                                    background: isGrant ? 'var(--success)' : (isRevoke ? 'var(--danger)' : 'var(--warning)')
                                }} />

                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                                    <span style={{
                                        fontSize: '0.75rem', fontWeight: 'bold', textTransform: 'uppercase',
                                        color: isGrant ? 'var(--success)' : (isRevoke ? 'var(--danger)' : 'var(--warning)'),
                                        background: isGrant ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                                        padding: '2px 8px', borderRadius: '4px'
                                    }}>
                                        {event.event_type.replace('CONSENT_', '')}
                                    </span>
                                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                                        {new Date(event.timestamp).toLocaleString()}
                                    </span>
                                </div>

                                <div style={{ marginBottom: '1rem' }}>
                                    {isGrant ? (
                                        <>
                                            <h3 style={{ marginBottom: '0.5rem', color: 'white' }}>
                                                {event.event_payload.purposes?.[0]?.purpose || 'General Consent'}
                                            </h3>
                                            <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                                                Granted to App: <span style={{ color: 'var(--text-main)' }}>{event.event_payload.app_id}</span>
                                            </p>
                                        </>
                                    ) : (
                                        <>
                                            <h3 style={{ marginBottom: '0.5rem', color: 'white' }}>Revocation Event</h3>
                                            <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                                                Action: <span style={{ color: 'var(--text-main)' }}>{event.event_payload.action}</span>
                                            </p>
                                        </>
                                    )}
                                </div>

                                <div style={{ background: 'rgba(0,0,0,0.3)', padding: '0.5rem', borderRadius: '4px', marginBottom: '1rem' }}>
                                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '4px' }}>VERIFIABLE HASH</div>
                                    <div className="mono" style={{ fontSize: '0.7rem', wordBreak: 'break-all', color: 'var(--accent)' }}>
                                        {event.hash_current.substring(0, 24)}...
                                    </div>
                                </div>

                                {isGrant && (
                                    <button
                                        onClick={() => handleRevoke(event.event_payload.consent_id)}
                                        style={{
                                            width: '100%', background: 'transparent', border: '1px solid var(--danger)',
                                            color: 'var(--danger)', fontSize: '0.9rem'
                                        }}
                                        className="hover-danger"
                                    >
                                        Revoke Access
                                    </button>
                                )}
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}
