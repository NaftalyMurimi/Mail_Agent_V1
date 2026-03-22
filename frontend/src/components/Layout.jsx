import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LayoutDashboard, Mail, Briefcase, FileText,
         Settings, LogOut, Zap } from 'lucide-react';
import api from '../services/api';
import { scanAPI } from '../services/api';
import toast from 'react-hot-toast';
import { useState } from 'react';

const navItems = [
  { to:'/dashboard', icon:LayoutDashboard, label:'Dashboard' },
  { to:'/emails',    icon:Mail,            label:'Emails'    },
  { to:'/jobs',      icon:Briefcase,       label:'Jobs'      },
  { to:'/cv',        icon:FileText,        label:'CV Upload' },
  { to:'/settings',  icon:Settings,        label:'Settings'  },
];

export default function Layout({ children }) {
  const { user, logout } = useAuth();
  const navigate         = useNavigate();
  const [scanning, setScanning] = useState(false);

 const handleScan = async () => {
  setScanning(true);
  try {
    const res = await scanAPI.trigger();
    const taskId = res.data.task_id;
    toast.success('Scan started! Checking progress...');

    // Poll for task completion every 3 seconds
    const interval = setInterval(async () => {
      try {
        const status = await api.get(`/scan/status/${taskId}`);
        const { status: taskStatus, result } = status.data;

        if (taskStatus === 'SUCCESS') {
          clearInterval(interval);
          setScanning(false);
          toast.success(
            `Scan complete! Found ${result?.emails_classified || 0} emails, ${result?.jobs_detected || 0} jobs.`
          );
        } else if (taskStatus === 'FAILURE') {
          clearInterval(interval);
          setScanning(false);
          toast.error('Scan failed. Check your Gmail connection.');
        }
      } catch {
        clearInterval(interval);
        setScanning(false);
      }
    }, 3000);

    // Stop polling after 3 minutes regardless
    setTimeout(() => {
      clearInterval(interval);
      setScanning(false);
    }, 180000);

  } catch (err) {
    toast.error(err.response?.data?.detail || 'Scan failed to start');
    setScanning(false);
  }
};

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div style={{ display:'flex', minHeight:'100vh' }}>

      {/* Sidebar */}
      <aside style={{ width:'240px', background:'#1e293b',
        borderRight:'1px solid #334155', display:'flex',
        flexDirection:'column', padding:'24px 0', flexShrink:0 }}>

        {/* Logo */}
        <div style={{ padding:'0 24px 24px', borderBottom:'1px solid #334155' }}>
          <div style={{ display:'flex', alignItems:'center', gap:'10px' }}>
            <span style={{ fontSize:'24px' }}>📧</span>
            <span style={{ fontWeight:'700', fontSize:'15px', color:'#f1f5f9' }}>
              Mail Agent
            </span>
          </div>
          <div style={{ fontSize:'12px', color:'#64748b', marginTop:'4px' }}>
            {user?.email}
          </div>
        </div>

        {/* Scan Button */}
        <div style={{ padding:'16px 24px' }}>
          <button
            onClick={handleScan}
            disabled={scanning}
            style={{ width:'100%', display:'flex', alignItems:'center',
              gap:'8px', padding:'10px 14px', background:'#2563eb',
              border:'none', borderRadius:'8px', color:'white',
              cursor:'pointer', fontSize:'14px', fontWeight:'500' }}>
            <Zap size={16} />
            {scanning ? 'Scanning...' : 'Scan Gmail'}
          </button>
        </div>

        {/* Nav Links */}
        <nav style={{ flex:1, padding:'0 12px' }}>
          {navItems.map(({ to, icon:Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              style={({ isActive }) => ({
                display:'flex', alignItems:'center', gap:'10px',
                padding:'10px 12px', borderRadius:'8px', marginBottom:'4px',
                textDecoration:'none', fontSize:'14px', fontWeight:'500',
                color: isActive ? '#60a5fa' : '#94a3b8',
                background: isActive ? '#1d4ed820' : 'transparent',
                transition:'all 0.2s',
              })}>
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>

        {/* Logout */}
        <div style={{ padding:'16px 24px', borderTop:'1px solid #334155' }}>
          <button
            onClick={handleLogout}
            style={{ width:'100%', display:'flex', alignItems:'center',
              gap:'8px', padding:'10px 14px', background:'transparent',
              border:'1px solid #334155', borderRadius:'8px', color:'#94a3b8',
              cursor:'pointer', fontSize:'14px' }}>
            <LogOut size={16} />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main style={{ flex:1, overflow:'auto', padding:'32px' }}>
        {children}
      </main>
    </div>
  );
}