import { useState } from 'react';

const API_URL = "https://saksham-api.vercel.app";

export default function AdminDashboard({ userId: currentUserId, token }) {
    const [appId, setAppId] = useState("app-demo-v1");
    const [userId, setUserId] = useState(currentUserId);
    const [purposes, setPurposes] = useState("CORE_FUNCTION");
    const [lastReceipt, setLastReceipt] = useState(null);
    const [loading, setLoading] = useState(false);

    const requestConsent = async () => {
        setLoading(true);
        const payload = {
            app_id: appId,
            user_id: userId,
            purposes: [
                { purpose_code: purposes, data_categories: ["email", "profile"] }
            ],
            expiry_hours: 24
        };

        try {
            const res = await fetch(`${API_URL}/consent/grant`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            setLastReceipt(data);
        } catch (e) {
            alert("Error requesting consent");
        }
        setLoading(false);
    };

    return (
        <div className="dashboard-view" style={{ maxWidth: '800px', margin: '0 auto' }}>
            <h2 style={{ marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ fontSize: '2rem' }}>⚡️</span> App Developer Console
            </h2>

            <div className="glass-panel" style={{ padding: '2rem', marginBottom: '2rem' }}>
                <h3 style={{ marginBottom: '1.5rem', color: 'var(--primary)', textTransform: 'uppercase', fontSize: '0.9rem', letterSpacing: '1px' }}>
                    Initiate Consent Flow
                </h3>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '1.5rem' }}>
                    <div className="form-group">
                        <label>Application ID</label>
                        <input value={appId} onChange={e => setAppId(e.target.value)} />
                    </div>
                    <div className="form-group">
                        <label>Target User ID</label>
                        <input value={userId} onChange={e => setUserId(e.target.value)} />
                    </div>
                </div>

                <div className="form-group">
                    <label>Requested Purpose</label>
                    <select value={purposes} onChange={e => setPurposes(e.target.value)}>
                        <option value="CORE_FUNCTION">Core Functionality (Contractual)</option>
                        <option value="ANALYTICS">Analytics & Performance</option>
                        <option value="MARKETING">Marketing & Promotions</option>
                    </select>
                </div>

                <button onClick={requestConsent} disabled={loading} style={{ width: '100%', marginTop: '1rem' }}>
                    {loading ? 'Processing...' : 'Request Consent & Generate Receipt'}
                </button>
            </div>

            {lastReceipt && (
                <div className="glass-panel" style={{ padding: '2rem', borderColor: 'var(--success)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                        <h3 style={{ color: 'var(--success)', margin: 0 }}>Consent Receipt Generated</h3>
                        <span style={{ background: 'rgba(16, 185, 129, 0.2)', color: 'var(--success)', padding: '2px 8px', borderRadius: '4px', fontSize: '0.8rem' }}>
                            SIGNED & VERIFIABLE
                        </span>
                    </div>
                    <pre className="receipt" style={{ maxHeight: '300px', overflowY: 'auto' }}>
                        {JSON.stringify(lastReceipt, null, 2)}
                    </pre>
                </div>
            )}
        </div>
    );
}
