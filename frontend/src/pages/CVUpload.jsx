import { useEffect, useState } from 'react';
import { cvAPI } from '../services/api';
import { Upload, Trash2, FileText } from 'lucide-react';
import toast from 'react-hot-toast';

export default function CVUpload() {
  const [cvs,      setCvs]      = useState([]);
  const [dragging, setDragging] = useState(false);
  const [loading,  setLoading]  = useState(false);

  const load = async () => {
    const res = await cvAPI.getAll();
    setCvs(res.data.cvs || []);
  };

  useEffect(() => { load(); }, []);

  const handleUpload = async (file) => {
    if (!file || !file.name.endsWith('.pdf')) {
      toast.error('Please upload a PDF file');
      return;
    }
    setLoading(true);
    try {
      await cvAPI.upload(file);
      toast.success('CV uploaded successfully!');
      load();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    await cvAPI.delete(id);
    setCvs(cvs.filter(c => c.id !== id));
    toast.success('CV deleted');
  };

  return (
    <div>
      <h1 style={{ fontSize:'24px', fontWeight:'700',
        color:'#f1f5f9', marginBottom:'24px' }}>
        📄 CV Upload
      </h1>

      {/* Drop Zone */}
      <div
        onDragOver={e => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={e => {
          e.preventDefault(); setDragging(false);
          handleUpload(e.dataTransfer.files[0]);
        }}
        onClick={() => document.getElementById('cvInput').click()}
        style={{ border:`2px dashed ${dragging ? '#2563eb' : '#334155'}`,
          borderRadius:'12px', padding:'48px', textAlign:'center',
          cursor:'pointer', marginBottom:'24px',
          background: dragging ? '#1d4ed810' : 'transparent',
          transition:'all 0.2s' }}>
        <Upload size={40} style={{ color:'#334155', marginBottom:'12px' }} />
        <div style={{ color:'#94a3b8', marginBottom:'4px' }}>
          Drag and drop your CV here or click to browse
        </div>
        <div style={{ fontSize:'13px', color:'#64748b' }}>PDF files only</div>
        <input
          id="cvInput" type="file" accept=".pdf" hidden
          onChange={e => handleUpload(e.target.files[0])}
        />
      </div>

      {loading && (
        <div style={{ textAlign:'center', color:'#60a5fa',
          marginBottom:'16px' }}>
          Uploading and parsing CV...
        </div>
      )}

      {/* CV List */}
      {cvs.map(cv => (
        <div key={cv.id} className="card"
          style={{ display:'flex', alignItems:'center',
            justifyContent:'space-between', marginBottom:'8px' }}>
          <div style={{ display:'flex', alignItems:'center', gap:'12px' }}>
            <FileText size={20} style={{ color:'#60a5fa' }} />
            <div>
              <div style={{ fontWeight:'600', color:'#f1f5f9' }}>{cv.filename}</div>
              <div style={{ fontSize:'12px', color:'#64748b' }}>
                Uploaded: {new Date(cv.uploaded_at).toLocaleDateString()}
              </div>
            </div>
          </div>
          <button onClick={() => handleDelete(cv.id)}
            style={{ background:'none', border:'none',
              color:'#64748b', cursor:'pointer' }}>
            <Trash2 size={16} />
          </button>
        </div>
      ))}
    </div>
  );
}