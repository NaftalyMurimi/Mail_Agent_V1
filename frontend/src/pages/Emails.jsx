import { useEffect, useState } from 'react';
import { emailAPI } from '../services/api';
import { Trash2, RefreshCw } from 'lucide-react';
import toast from 'react-hot-toast';

useEffect(() => {
  load();
  const interval = setInterval(load, 30000);
  return () => clearInterval(interval);
}, [filter]);

const TYPE_COLORS = {
  job_advert:  { bg:'#1d4ed820', color:'#60a5fa', label:'Job Advert'  },
  interview:   { bg:'#d9770620', color:'#fbbf24', label:'Interview'   },
  offer:       { bg:'#16a34a20', color:'#4ade80', label:'Offer'       },
  rejection:   { bg:'#dc262620', color:'#f87171', label:'Rejection'   },
  confirmed:   { bg:'#16a34a20', color:'#4ade80', label:'Confirmed'   },
  followup:    { bg:'#7c3aed20', color:'#a78bfa', label:'Follow Up'   },
  irrelevant:  { bg:'#33415520', color:'#94a3b8', label:'Irrelevant'  },
};

export default function Emails() {
  const [emails,  setEmails]  = useState([]);
  const [filter,  setFilter]  = useState('all');
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const params = filter !== 'all' ? { email_type: filter } : {};
      const res    = await emailAPI.getAll(params);
      setEmails(res.data.emails || []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [filter]);

  const handleDelete = async (id) => {
    await emailAPI.delete(id);
    setEmails(emails.filter(e => e.id !== id));
    toast.success('Email removed');
  };

  return (
    <div>
      <div style={{ display:'flex', justifyContent:'space-between',
        alignItems:'center', marginBottom:'24px' }}>
        <h1 style={{ fontSize:'24px', fontWeight:'700', color:'#f1f5f9' }}>
          📧 Classified Emails
        </h1>
        <button onClick={load} className="btn-secondary"
          style={{ display:'flex', alignItems:'center', gap:'6px' }}>
          <RefreshCw size={14} /> Refresh
        </button>
      </div>

      {/* Filter Pills */}
      <div style={{ display:'flex', gap:'8px', marginBottom:'20px', flexWrap:'wrap' }}>
        {['all','job_advert','interview','offer','rejection','irrelevant'].map(f => (
          <button key={f}
            onClick={() => setFilter(f)}
            style={{ padding:'6px 14px', borderRadius:'20px', border:'none',
              cursor:'pointer', fontSize:'13px', fontWeight:'500',
              background: filter===f ? '#2563eb' : '#334155',
              color: filter===f ? 'white' : '#94a3b8' }}>
            {f === 'all' ? 'All' : TYPE_COLORS[f]?.label || f}
          </button>
        ))}
      </div>

      {loading ? (
        <div style={{ textAlign:'center', padding:'48px', color:'#64748b' }}>
          Loading emails...
        </div>
      ) : emails.length === 0 ? (
        <div className="card" style={{ textAlign:'center', padding:'48px' }}>
          <div style={{ fontSize:'48px', marginBottom:'16px' }}>📭</div>
          <p style={{ color:'#64748b' }}>No emails found. Try scanning your Gmail.</p>
        </div>
      ) : (
        <div style={{ display:'flex', flexDirection:'column', gap:'8px' }}>
          {emails.map(email => {
            const type = TYPE_COLORS[email.email_type] || TYPE_COLORS.irrelevant;
            return (
              <div key={email.id} className="card" style={{ padding:'16px' }}>
                <div style={{ display:'flex', justifyContent:'space-between',
                  alignItems:'flex-start' }}>
                  <div style={{ flex:1 }}>
                    <div style={{ display:'flex', alignItems:'center',
                      gap:'10px', marginBottom:'6px' }}>
                      <span style={{ padding:'3px 10px', borderRadius:'20px',
                        fontSize:'12px', fontWeight:'600',
                        background:type.bg, color:type.color }}>
                        {type.label}
                      </span>
                      {email.urgency === 'high' && (
                        <span style={{ fontSize:'12px', color:'#f87171' }}>
                          🔴 Urgent
                        </span>
                      )}
                      {email.action_required && (
                        <span style={{ fontSize:'12px', color:'#fbbf24' }}>
                          ⚡ Action Required
                        </span>
                      )}
                    </div>
                    <div style={{ fontWeight:'600', color:'#f1f5f9', marginBottom:'4px' }}>
                      {email.subject || 'No subject'}
                    </div>
                    <div style={{ fontSize:'13px', color:'#64748b', marginBottom:'6px' }}>
                      From: {email.sender}
                    </div>
                    {email.company && (
                      <div style={{ fontSize:'13px', color:'#94a3b8' }}>
                        🏢 {email.company}
                        {email.role_title && ` · ${email.role_title}`}
                        {email.location   && ` · ${email.location}`}
                      </div>
                    )}
                    {email.deadline && (
                      <div style={{ fontSize:'13px', color:'#fbbf24', marginTop:'4px' }}>
                        ⏰ Deadline: {email.deadline}
                      </div>
                    )}
                  </div>
                  <button onClick={() => handleDelete(email.id)}
                    style={{ background:'none', border:'none',
                      color:'#64748b', cursor:'pointer', padding:'4px' }}>
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}