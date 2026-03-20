import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

export default function Signup() {
  const [form, setForm]       = useState({ email:'', password:'', full_name:'' });
  const [loading, setLoading] = useState(false);
  const { login }             = useAuth();
  const navigate              = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await authAPI.signup(form);
      await login(form.email, form.password);
      toast.success('Account created!');
      navigate('/dashboard');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Signup failed');
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
            Create Account
          </h1>
          <p style={{ color:'#94a3b8', marginTop:'4px' }}>
            Start automating your job search
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          {[
            { key:'full_name', label:'Full Name',   type:'text',     placeholder:'Naftali Murimi' },
            { key:'email',     label:'Email',        type:'email',    placeholder:'you@example.com' },
            { key:'password',  label:'Password',     type:'password', placeholder:'••••••••' },
          ].map(({ key, label, type, placeholder }) => (
            <div key={key} style={{ marginBottom:'16px' }}>
              <label style={{ display:'block', marginBottom:'6px',
                fontSize:'14px', color:'#94a3b8' }}>{label}</label>
              <input
                type={type}
                value={form[key]}
                onChange={e => setForm({...form, [key]: e.target.value})}
                required
                placeholder={placeholder}
                style={{ width:'100%', padding:'10px 12px',
                  background:'#0f172a', border:'1px solid #334155',
                  borderRadius:'8px', color:'#f1f5f9', fontSize:'14px',
                  outline:'none', boxSizing:'border-box' }}
              />
            </div>
          ))}

          <button
            type="submit"
            disabled={loading}
            className="btn-primary"
            style={{ width:'100%', padding:'12px', marginTop:'8px' }}>
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>

        <p style={{ textAlign:'center', marginTop:'20px',
          fontSize:'14px', color:'#94a3b8' }}>
          Already have an account?{' '}
          <Link to="/login" style={{ color:'#60a5fa' }}>Sign in</Link>
        </p>
      </div>
    </div>
  );
}