import { useEffect, useState } from 'react';
import { settingsAPI } from '../services/api';
import api from '../services/api';
import toast from 'react-hot-toast';
import { CheckCircle, Wifi, Bell, Send } from 'lucide-react';

export default function Settings() {
  const [settings,      setSettings]      = useState(null);
  const [gmailStatus,   setGmailStatus]   = useState(null);
  const [telegramId,    setTelegramId]    = useState('');
  const [pushEnabled,   setPushEnabled]   = useState(false);
  const [saving,        setSaving]        = useState(false);
  const [testing,       setTesting]       = useState(false);

  useEffect(() => {
    settingsAPI.get().then(res => {
      setSettings(res.data);
      setTelegramId(res.data.telegram_chat_id || '');
      setPushEnabled(res.data.notifications?.browser || false);
    });
    api.get('/gmail/status').then(res => setGmailStatus(res.data));
  }, []);

  // Check if returning from Gmail connect
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('gmail') === 'connected') {
      toast.success('Gmail connected successfully!');
      api.get('/gmail/status').then(res => setGmailStatus(res.data));
      window.history.replaceState({}, '', '/settings');
    }
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
    try {
      await api.delete('/gmail/disconnect');
      setGmailStatus({ connected: false });
      toast.success('Gmail disconnected');
    } catch {
      toast.error('Failed to disconnect Gmail');
    }
  };

  const saveTelegram = async () => {
    if (!telegramId.trim()) {
      toast.error('Please enter your Telegram chat ID');
      return;
    }
    setSaving(true);
    try {
      await api.post(`/settings/telegram?chat_id=${telegramId.trim()}`);
      toast.success('Telegram configured!');
    } catch {
      toast.error('Failed to save Telegram ID');
    } finally {
      setSaving(false);
    }
  };

  const testTelegram = async () => {
    setTesting(true);
    try {
      const res = await api.post('/settings/telegram/test');
      if (res.data.success) {
        toast.success('Test message sent to Telegram!');
      } else {
        toast.error(res.data.message);
      }
    } finally {
      setTesting(false);
    }
  };

  const togglePush = async () => {
    if (!('Notification' in window)) {
      toast.error('Browser push not supported in this browser');
      return;
    }

    if (!pushEnabled) {
      // Enable push
      const permission = await Notification.requestPermission();
      if (permission !== 'granted') {
        toast.error('Notification permission denied');
        return;
      }

      try {
        const vapidKey = import.meta.env.VITE_VAPID_PUBLIC_KEY;
        const reg      = await navigator.serviceWorker.register('/sw.js');
        const sub      = await reg.pushManager.subscribe({
          userVisibleOnly:      true,
          applicationServerKey: vapidKey,
        });
        await api.post('/settings/push/subscribe', sub.toJSON());
        setPushEnabled(true);
        toast.success('Browser push notifications enabled!');
      } catch (e) {
        toast.error('Failed to enable push notifications');
        console.error(e);
      }
    } else {
      // Disable push
      await api.delete('/settings/push/unsubscribe');
      setPushEnabled(false);
      toast.success('Push notifications disabled');
    }
  };

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
        <h3 style={{ color:'#f1f5f9', marginBottom:'16px' }}>Gmail Connection</h3>
        <div style={{ display:'flex', alignItems:'center',
          justifyContent:'space-between', padding:'16px',
          background:'#0f172a', borderRadius:'10px' }}>
          <div style={{ display:'flex', alignItems:'center', gap:'12px' }}>
            <Wifi size={24} style={{ color: gmailStatus?.connected ? '#4ade80' : '#64748b' }} />
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
            <div style={{ display:'flex', gap:'8px', alignItems:'center' }}>
              <span style={{ fontSize:'13px', color:'#4ade80', display:'flex',
                alignItems:'center', gap:'4px' }}>
                <CheckCircle size={14} /> Connected
              </span>
              <button onClick={handleDisconnect} className="btn-secondary"
                style={{ fontSize:'13px', padding:'6px 14px' }}>
                Disconnect
              </button>
            </div>
          ) : (
            <button onClick={handleConnect} className="btn-primary"
              style={{ display:'flex', alignItems:'center', gap:'6px' }}>
              Connect Gmail
            </button>
          )}
        </div>
      </div>

      {/* Telegram */}
      <div className="card" style={{ marginBottom:'16px' }}>
        <h3 style={{ color:'#f1f5f9', marginBottom:'8px' }}>
          📱 Telegram Notifications
        </h3>
        <p style={{ color:'#64748b', fontSize:'13px', marginBottom:'16px' }}>
          Get instant job alerts on your phone via Telegram.
          Send /start to your bot to get your Chat ID.
        </p>
        <div style={{ display:'flex', gap:'8px', marginBottom:'12px' }}>
          <input
            type="text"
            value={telegramId}
            onChange={e => setTelegramId(e.target.value)}
            placeholder="Your Telegram Chat ID e.g. 123456789"
            style={{ flex:1, padding:'10px 12px', background:'#0f172a',
              border:'1px solid #334155', borderRadius:'8px',
              color:'#f1f5f9', fontSize:'14px', outline:'none' }}
          />
          <button onClick={saveTelegram} disabled={saving}
            className="btn-primary" style={{ whiteSpace:'nowrap' }}>
            {saving ? 'Saving...' : 'Save'}
          </button>
        </div>
        {telegramId && (
          <button onClick={testTelegram} disabled={testing}
            style={{ display:'flex', alignItems:'center', gap:'6px',
              background:'none', border:'1px solid #334155',
              borderRadius:'8px', padding:'8px 14px', color:'#94a3b8',
              cursor:'pointer', fontSize:'13px' }}>
            <Send size={14} />
            {testing ? 'Sending...' : 'Send Test Message'}
          </button>
        )}
      </div>

      {/* Browser Push */}
      <div className="card" style={{ marginBottom:'16px' }}>
        <div style={{ display:'flex', alignItems:'center',
          justifyContent:'space-between' }}>
          <div>
            <h3 style={{ color:'#f1f5f9', marginBottom:'4px' }}>
              🔔 Browser Push Notifications
            </h3>
            <p style={{ color:'#64748b', fontSize:'13px' }}>
              Get notified in your browser when a scan completes.
            </p>
          </div>
          <button onClick={togglePush}
            style={{ padding:'8px 20px', borderRadius:'8px', border:'none',
              cursor:'pointer', fontWeight:'600', fontSize:'14px',
              background: pushEnabled ? '#16a34a' : '#334155',
              color: 'white', transition:'all 0.2s' }}>
            {pushEnabled ? 'Enabled ✅' : 'Enable'}
          </button>
        </div>
      </div>

      {/* Account Info */}
      <div className="card">
        <h3 style={{ color:'#f1f5f9', marginBottom:'16px' }}>Account</h3>
        {[
          ['Subscription', settings.subscription_tier],
          ['Scan Interval', `Every ${settings.scan_interval_minutes} minutes`],
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
  );
}