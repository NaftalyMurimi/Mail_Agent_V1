import { useEffect, useState } from 'react';
import { emailAPI, jobAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { Mail, Briefcase, Star, AlertCircle } from 'lucide-react';

function StatCard({ icon:Icon, label, value, color }) {
  return (
    <div className="card" style={{ display:'flex', alignItems:'center', gap:'16px' }}>
      <div style={{ padding:'12px', background:`${color}20`,
        borderRadius:'10px', color }}>
        <Icon size={24} />
      </div>
      <div>
        <div style={{ fontSize:'28px', fontWeight:'700', color:'#f1f5f9' }}>
          {value}
        </div>
        <div style={{ fontSize:'14px', color:'#64748b' }}>{label}</div>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const { user }          = useAuth();
  const [stats, setStats] = useState({
    emails:0, jobs:0, topJobs:[], actionRequired:0
  });

  useEffect(() => {
    Promise.all([
      emailAPI.getAll({ limit:100 }),
      jobAPI.getAll({ limit:100 }),
    ]).then(([emailRes, jobRes]) => {
      const emails   = emailRes.data.emails || [];
      const jobs     = jobRes.data.jobs     || [];
      const topJobs  = jobs.filter(j => j.match_score >= 7).slice(0,3);
      const actions  = emails.filter(e => e.action_required).length;
      setStats({ emails:emails.length, jobs:jobs.length, topJobs, actionRequired:actions });
    }).catch(() => {});
  }, []);

  return (
    <div>
      <div style={{ marginBottom:'32px' }}>
        <h1 style={{ fontSize:'28px', fontWeight:'700', color:'#f1f5f9' }}>
          Welcome back, {user?.full_name || 'there'} 👋
        </h1>
        <p style={{ color:'#64748b', marginTop:'4px' }}>
          Here is your job search summary
        </p>
      </div>

      {/* Stats Grid */}
      <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit, minmax(200px,1fr))',
        gap:'16px', marginBottom:'32px' }}>
        <StatCard icon={Mail}        label="Emails Classified" value={stats.emails}        color="#60a5fa" />
        <StatCard icon={Briefcase}   label="Jobs Detected"     value={stats.jobs}          color="#4ade80" />
        <StatCard icon={Star}        label="High Match Jobs"   value={stats.topJobs.length} color="#fbbf24" />
        <StatCard icon={AlertCircle} label="Action Required"   value={stats.actionRequired} color="#f87171" />
      </div>

      {/* Top Jobs */}
      {stats.topJobs.length > 0 && (
        <div className="card">
          <h2 style={{ fontSize:'18px', fontWeight:'600', color:'#f1f5f9',
            marginBottom:'16px' }}>🏆 Top Job Matches</h2>
          {stats.topJobs.map(job => (
            <div key={job.id} style={{ display:'flex', alignItems:'center',
              justifyContent:'space-between', padding:'12px 0',
              borderBottom:'1px solid #334155' }}>
              <div>
                <div style={{ fontWeight:'600', color:'#f1f5f9' }}>
                  {job.role_title || 'Unknown Role'}
                </div>
                <div style={{ fontSize:'13px', color:'#64748b' }}>
                  {job.company} · {job.location || 'Location TBC'}
                </div>
              </div>
              <div style={{ display:'flex', alignItems:'center', gap:'12px' }}>
                <span style={{ fontSize:'20px', fontWeight:'700', color:'#4ade80' }}>
                  {job.match_score}/10
                </span>
                <span style={{ fontSize:'12px', padding:'4px 10px',
                  background:'#16a34a20', color:'#4ade80',
                  borderRadius:'20px', border:'1px solid #16a34a40' }}>
                  {job.apply_recommendation}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {stats.emails === 0 && (
        <div className="card" style={{ textAlign:'center', padding:'48px' }}>
          <div style={{ fontSize:'48px', marginBottom:'16px' }}>📭</div>
          <h3 style={{ color:'#f1f5f9', marginBottom:'8px' }}>No data yet</h3>
          <p style={{ color:'#64748b' }}>
            Click Scan Gmail in the sidebar to start scanning your inbox
          </p>
        </div>
      )}
    </div>
  );
}