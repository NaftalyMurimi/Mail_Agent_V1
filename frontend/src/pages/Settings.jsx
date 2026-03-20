import { useEffect, useState } from 'react';
import { settingsAPI } from '../services/api';
import toast from 'react-hot-toast';

export default function Settings() {
  const [settings, setSettings] = useState(null);

  useEffect(() => {
    settingsAPI.get().then(res => setSettings(res.data));
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

      <div className="card">
        <h3 style={{ color:'#f1f5f9', marginBottom:'16px' }}>Notifications</h3>
        {Object.entries(settings.notifications || {}).map(([key, val]) => (
          <div key={key} style={{ display:'flex',
            justifyContent:'space-between', alignItems:'center',
            padding:'10px 0', borderBottom:'1px solid #334155' }}>
            <span style={{ color:'#94a3b8', fontSize:'14px', textTransform:'capitalize' }}>
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