import { useEffect, useState } from 'react';
import { settingsAPI } from '../services/api';
import api from '../services/api';
import toast from 'react-hot-toast';
import { CheckCircle, XCircle, Wifi } from 'lucide-react';

export default function Settings() {
  const [settings,       setSettings]       = useState(null);
  const [gmailStatus,    setGmailStatus]    = useState(null);
  const [disconnecting,  setDisconnecting]  = useState(false);

  useEffect(() => {
    settingsAPI.get().then(res => setSettings(res.data));
    api.get('/gmail/status').then(res => setGmailStatus(res.data));
  }, []);

  const handleConnect = async () => {
    try {
      const res = await api.get('/gmail/connect');
      window.location.href = res.data.auth_url;
    } catch {
      toast.error('Failed to start Gmail connection');
    }
  };

  const handleDisconnect = async () => {
    setDisconnecting(true);
    try {
      await api.delete('/gmail/disconnect');
      setGmailStatus({ connected: false });
      toast.success('Gmail disconnected');
    } catch {
      toast.error('Failed to disconnect Gmail');
    } finally {
      setDisconnecting(false);
    }
  };

  // Check if redirected back after connecting
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('gmail') === 'connected') {
      toast.success('Gmail connected successfully!');
      api.get('/gmail/status').then(res => setGmailStatus(res.data));
      window.history.replaceState({}, '', '/settings');
    }
  }, []);

  if (!settings) return (
    <div style={{ color:'#64748b', padding:'48px', textAlign:'center' }}>
      Loading settings...
    </div>
  );

  return (
    <div>
      <h1 style={{ fontSize:'24px', fontWeight:'700',
        color:'#f1f5f9', marginBottom:'24px' }}>
        ⚙️ Settings
      </h1>

      {/* Gmail Connection */}
      <div className="card" style={{ marginBottom:'16px' }}>
        <h3 style={{ color:'#f1f5f9', marginBottom:'16px' }}>
          Gmail Connection
        </h3>

        <div style={{ display:'flex', alignItems:'center',
          justifyContent:'space-between', padding:'16px',
          background:'#0f172a', borderRadius:'10px' }}>
          <div style={{ display:'flex', alignItems:'center', gap:'12px' }}>
            <Wifi size={24} style={{ color: gmailStatus?.connected
              ? '#4ade80' : '#64748b' }} />
            <div>
              <div style={{ fontWeight:'600', color:'#f1f5f9' }}>
                {gmailStatus?.connected ? 'Gmail Connected' : 'Gmail Not Connected'}
              </div>
              <div style={{ fontSize:'13px', color:'#64748b' }}>
                {gmailStatus?.connected
                  ? `Last updated: ${new Date(gmailStatus.updated_at).toLocaleDateString()}`
                  : 'Connect your Gmail to start scanning'
                }
              </div>
            </div>
          </div>

          {gmailStatus?.connected ? (
            <div style={{ display:'flex', gap:'8px' }}>
              <span style={{ display:'flex', alignItems:'center', gap:'4px',
                fontSize:'13px', color:'#4ade80' }}>
                <CheckCircle size={14} /> Connected
              </span>
              <button
                onClick={handleDisconnect}
                disabled={disconnecting}
                className="btn-secondary"
                style={{ fontSize:'13px', padding:'6px 14px' }}>
                Disconnect
              </button>
            </div>
          ) : (
            <button
              onClick={handleConnect}
              className="btn-primary"
              style={{ display:'flex', alignItems:'center', gap:'6px' }}>
              Connect Gmail
            </button>
          )}
        </div>
      </div>

      {/* Account Settings */}
      <div className="card" style={{ marginBottom:'16px' }}>
        <h3 style={{ color:'#f1f5f9', marginBottom:'16px' }}>Account</h3>
        <div style={{ display:'grid', gap:'12px' }}>
          {[
            ['Subscription', settings.subscription_tier],
            ['Scan Interval', `Every ${settings.scan_interval_minutes} minutes`],
            ['Telegram Chat ID', settings.telegram_chat_id || 'Not configured'],
          ].map(([label, value]) => (
            <div key={label} style={{ display:'flex',
              justifyContent:'space-between', padding:'10px 0',
              borderBottom:'1px solid #334155' }}>
              <span style={{ color:'#94a3b8', fontSize:'14px' }}>{label}</span>
              <span style={{ color:'#f1f5f9', fontSize:'14px',
                textTransform:'capitalize' }}>{value}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Notifications */}
      <div className="card">
        <h3 style={{ color:'#f1f5f9', marginBottom:'16px' }}>Notifications</h3>
        {Object.entries(settings.notifications || {}).map(([key, val]) => (
          <div key={key} style={{ display:'flex',
            justifyContent:'space-between', alignItems:'center',
            padding:'10px 0', borderBottom:'1px solid #334155' }}>
            <span style={{ color:'#94a3b8', fontSize:'14px',
              textTransform:'capitalize' }}>
              {key}
            </span>
            <span style={{ fontSize:'13px', padding:'3px 10px',
              borderRadius:'20px',
              background: val ? '#16a34a20' : '#33415520',
              color: val ? '#4ade80' : '#94a3b8' }}>
              {val ? 'Enabled' : 'Disabled'}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}