import { useState, useEffect } from 'react';

const API_URL = "http://127.0.0.1:8000";

export default function RegulatorDashboard({ token }) {
    const [events, setEvents] = useState([]);
    const [verification, setVerification] = useState(null);
    const [loading, setLoading] = useState(false);

    const fetchLogs = async () => {
        setLoading(true);
        const res = await fetch(`${API_URL}/audit/events?limit=20`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        setEvents(data);
        setLoading(false);
    };

    const verifyChain = async () => {
        const res = await fetch(`${API_URL}/audit/verify-chain`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await res.json();
        setVerification(data);
    };

    const simulateTamper = async () => {
        if (!confirm("⚠️ SIMULATION WARNING\n\nThis will deliberately corrupt the latest ledger entry in the database to test the Verification Engine.\n\nProceed?")) return;

        const res = await fetch(`${API_URL}/audit/tamper`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
            alert("ATTACK SIMULATED: Valid hash replaced with 'DEADBEEF...'.\n\nNow click 'Verify Hash Chain' to detect the intrusion.");
        }
    };

    useEffect(() => {
        fetchLogs();
    }, []);

    return (
        <div className="dashboard-view">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                <div>
                    <h2>Regulatory Oversight</h2>
                    <p style={{ color: 'var(--text-muted)' }}>Real-time audit of consent ledger.</p>
                </div>
                <div style={{ display: 'flex', gap: '1rem' }}>
                    <button className="secondary" onClick={simulateTamper} style={{ borderColor: 'var(--danger)', color: 'var(--danger)' }}>
                        ⚠️ Simulate Attack
                    </button>
                    <button className="secondary" onClick={fetchLogs} disabled={loading}>{loading ? 'Syncing...' : 'Refresh Logs'}</button>
                    <button onClick={verifyChain}>Verify Hash Chain</button>
                </div>
            </div>

            {verification && (
                <div className={`glass-panel ${verification.status === 'VALID' ? 'success' : 'error'}`} style={{ marginBottom: '2rem', padding: '1rem 1.5rem', background: verification.status === 'VALID' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <span style={{ fontSize: '1.5rem' }}>{verification.status === 'VALID' ? '✅' : '❌'}</span>
                        <div>
                            <strong style={{ display: 'block', color: verification.status === 'VALID' ? 'var(--success)' : 'var(--danger)' }}>
                                Chain Integrity: {verification.status}
                            </strong>
                            <span style={{ fontSize: '0.9rem', opacity: 0.8 }}>
                                Helper Verified {verification.verified_count} blocks.
                                {verification.status === 'VALID' ? ' No tampering detected.' : ` FAILURE: ${verification.violations.length} violations found.`}
                            </span>
                        </div>
                    </div>
                </div>
            )}

            <div className="glass-panel" style={{ padding: '0', overflow: 'hidden' }}>
                <table className="audit-table">
                    <thead style={{ background: 'rgba(255,255,255,0.02)' }}>
                        <tr>
                            <th>Details</th>
                            <th>Actor</th>
                            <th>Event Type</th>
                            <th>Proof (Hash)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {events.map(ev => (
                            <tr key={ev.event_id}>
                                <td style={{ minWidth: '150px' }}>
                                    <div style={{ fontSize: '0.9rem', fontWeight: '500' }}>{new Date(ev.timestamp).toLocaleTimeString()}</div>
                                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{new Date(ev.timestamp).toLocaleDateString()}</div>
                                </td>
                                <td>
                                    <span style={{
                                        padding: '2px 8px', borderRadius: '4px', fontSize: '0.75rem', fontWeight: '600',
                                        background: ev.actor_type === 'USER' ? 'rgba(59, 130, 246, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                                        color: ev.actor_type === 'USER' ? 'var(--primary)' : 'var(--warning)'
                                    }}>
                                        {ev.actor_type}
                                    </span>
                                    <div style={{ fontSize: '0.75rem', marginTop: '4px', opacity: 0.7 }}>{ev.actor_id?.substring(0, 8)}...</div>
                                </td>
                                <td>
                                    <div style={{ fontWeight: '500' }}>{ev.event_type}</div>
                                </td>
                                <td>
                                    <div className="mono" style={{ fontSize: '0.75rem', color: 'var(--accent)', background: 'rgba(0,0,0,0.3)', padding: '4px', borderRadius: '4px', display: 'inline-block' }}>
                                        {ev.hash_current.substring(0, 16)}...
                                    </div>
                                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '2px' }}>PREV: {ev.hash_prev.substring(0, 8)}...</div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
