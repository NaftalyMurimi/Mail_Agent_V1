import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

export default function Login() {
  const [form, setForm]       = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const { login }             = useAuth();
  const navigate              = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(form.email, form.password);
      toast.success('Welcome back!');
      navigate('/dashboard');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight:'100vh', display:'flex',
      alignItems:'center', justifyContent:'center', padding:'20px' }}>
      <div className="card" style={{ width:'100%', maxWidth:'400px' }}>

        <div style={{ textAlign:'center', marginBottom:'32px' }}>
          <div style={{ fontSize:'40px', marginBottom:'8px' }}>📧</div>
          <h1 style={{ fontSize:'24px', fontWeight:'700', color:'#f1f5f9' }}>
            Email Manager Agent
          </h1>
          <p style={{ color:'#94a3b8', marginTop:'4px' }}>Sign in to your account</p>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom:'16px' }}>
            <label style={{ display:'block', marginBottom:'6px',
              fontSize:'14px', color:'#94a3b8' }}>Email</label>
            <input
              type="email"
              value={form.email}
              onChange={e => setForm({...form, email: e.target.value})}
              required
              style={{ width:'100%', padding:'10px 12px',
                background:'#0f172a', border:'1px solid #334155',
                borderRadius:'8px', color:'#f1f5f9', fontSize:'14px',
                outline:'none', boxSizing:'border-box' }}
              placeholder="you@example.com"
            />
          </div>

          <div style={{ marginBottom:'24px' }}>
            <label style={{ display:'block', marginBottom:'6px',
              fontSize:'14px', color:'#94a3b8' }}>Password</label>
            <input
              type="password"
              value={form.password}
              onChange={e => setForm({...form, password: e.target.value})}
              required
              style={{ width:'100%', padding:'10px 12px',
                background:'#0f172a', border:'1px solid #334155',
                borderRadius:'8px', color:'#f1f5f9', fontSize:'14px',
                outline:'none', boxSizing:'border-box' }}
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn-primary"
            style={{ width:'100%', padding:'12px' }}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <p style={{ textAlign:'center', marginTop:'20px',
          fontSize:'14px', color:'#94a3b8' }}>
          No account?{' '}
          <Link to="/signup" style={{ color:'#60a5fa' }}>Sign up</Link>
        </p>
      </div>
    </div>
  );
}