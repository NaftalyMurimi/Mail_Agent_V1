import { useEffect, useState } from 'react';
import { jobAPI } from '../services/api';
import toast from 'react-hot-toast';

const STATUSES = ['detected','considering','applied','interview','offer','rejected'];

const STATUS_STYLE = {
  detected:    { bg:'#33415520', color:'#94a3b8' },
  considering: { bg:'#1d4ed820', color:'#60a5fa' },
  applied:     { bg:'#7c3aed20', color:'#a78bfa' },
  interview:   { bg:'#d9770620', color:'#fbbf24' },
  offer:       { bg:'#16a34a20', color:'#4ade80' },
  rejected:    { bg:'#dc262620', color:'#f87171' },
};

export default function Jobs() {
  const [jobs,    setJobs]    = useState([]);
  const [loading, setLoading] = useState(true);
  const [minScore, setMinScore] = useState('');

  const load = async () => {
    setLoading(true);
    try {
      const params = {};
      if (minScore) params.min_score = minScore;
      const res = await jobAPI.getAll(params);
      setJobs(res.data.jobs || []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const updateStatus = async (id, status) => {
    try {
      await jobAPI.updateStatus(id, status);
      setJobs(jobs.map(j => j.id === id ? {...j, status} : j));
      toast.success(`Status updated to ${status}`);
    } catch {
      toast.error('Failed to update status');
    }
  };

  const scoreColor = (score) => {
    if (!score) return '#94a3b8';
    if (score >= 8)  return '#4ade80';
    if (score >= 6)  return '#fbbf24';
    return '#f87171';
  };

  return (
    <div>
      <div style={{ display:'flex', justifyContent:'space-between',
        alignItems:'center', marginBottom:'24px' }}>
        <h1 style={{ fontSize:'24px', fontWeight:'700', color:'#f1f5f9' }}>
          💼 Job Tracker
        </h1>
        <div style={{ display:'flex', gap:'8px', alignItems:'center' }}>
          <input
            type="number" placeholder="Min score"
            value={minScore}
            onChange={e => setMinScore(e.target.value)}
            style={{ padding:'8px 12px', background:'#1e293b',
              border:'1px solid #334155', borderRadius:'8px',
              color:'#f1f5f9', width:'110px', outline:'none' }}
          />
          <button onClick={load} className="btn-primary">Filter</button>
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign:'center', padding:'48px', color:'#64748b' }}>
          Loading jobs...
        </div>
      ) : jobs.length === 0 ? (
        <div className="card" style={{ textAlign:'center', padding:'48px' }}>
          <div style={{ fontSize:'48px', marginBottom:'16px' }}>💼</div>
          <p style={{ color:'#64748b' }}>
            No jobs found yet. Scan your Gmail to detect job adverts.
          </p>
        </div>
      ) : (
        <div style={{ display:'flex', flexDirection:'column', gap:'12px' }}>
          {jobs.map(job => (
            <div key={job.id} className="card">
              <div style={{ display:'flex', justifyContent:'space-between',
                alignItems:'flex-start', marginBottom:'12px' }}>
                <div>
                  <h3 style={{ fontSize:'17px', fontWeight:'600',
                    color:'#f1f5f9', marginBottom:'4px' }}>
                    {job.role_title || 'Unknown Role'}
                  </h3>
                  <div style={{ fontSize:'14px', color:'#64748b' }}>
                    {job.company}
                    {job.location && ` · ${job.location}`}
                    {job.salary   && ` · ${job.salary}`}
                  </div>
                </div>
                <div style={{ textAlign:'right' }}>
                  <div style={{ fontSize:'28px', fontWeight:'700',
                    color: scoreColor(job.match_score) }}>
                    {job.match_score ? `${job.match_score}/10` : 'N/A'}
                  </div>
                  <div style={{ fontSize:'12px', color:'#64748b' }}>
                    {job.apply_recommendation}
                  </div>
                </div>
              </div>

              {job.match_reasons && (
                <div style={{ fontSize:'13px', color:'#94a3b8',
                  marginBottom:'8px', padding:'10px', background:'#0f172a',
                  borderRadius:'8px' }}>
                  ✅ {job.match_reasons}
                </div>
              )}

              {job.gaps && (
                <div style={{ fontSize:'13px', color:'#94a3b8',
                  marginBottom:'8px' }}>
                  ⚠️ Gap: {job.gaps}
                </div>
              )}

              {job.personalized_tip && (
                <div style={{ fontSize:'13px', color:'#60a5fa',
                  marginBottom:'12px', padding:'10px', background:'#1d4ed810',
                  borderRadius:'8px', borderLeft:'3px solid #2563eb' }}>
                  💡 {job.personalized_tip}
                </div>
              )}

              {job.deadline && (
                <div style={{ fontSize:'13px', color:'#fbbf24', marginBottom:'12px' }}>
                  ⏰ Deadline: {job.deadline}
                </div>
              )}

              {/* Status Selector */}
              <div style={{ display:'flex', gap:'6px', flexWrap:'wrap' }}>
                {STATUSES.map(s => {
                  const st = STATUS_STYLE[s];
                  return (
                    <button key={s}
                      onClick={() => updateStatus(job.id, s)}
                      style={{ padding:'4px 12px', borderRadius:'20px',
                        border: job.status===s ? `2px solid ${st.color}` : '1px solid #334155',
                        background: job.status===s ? st.bg : 'transparent',
                        color: job.status===s ? st.color : '#64748b',
                        cursor:'pointer', fontSize:'12px', fontWeight:'500' }}>
                      {s.charAt(0).toUpperCase() + s.slice(1)}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}