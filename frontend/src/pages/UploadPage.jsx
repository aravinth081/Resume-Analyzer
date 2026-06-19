import { useState, useCallback } from 'react';
import { resumeAPI } from '../services/api';
import { useNavigate } from 'react-router-dom';
import { Upload, FileText, CheckCircle, AlertCircle, Loader } from 'lucide-react';

export default function UploadPage() {
  const [file, setFile] = useState(null);
  const [title, setTitle] = useState('');
  const [dragOver, setDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files[0];
    if (f && (f.name.endsWith('.pdf') || f.name.endsWith('.docx'))) {
      setFile(f);
      if (!title) setTitle(f.name.replace(/\.(pdf|docx)$/i, ''));
    } else {
      setError('Please upload a PDF or DOCX file');
    }
  }, [title]);

  const handleFileSelect = (e) => {
    const f = e.target.files[0];
    if (f) {
      setFile(f);
      if (!title) setTitle(f.name.replace(/\.(pdf|docx)$/i, ''));
      setError('');
    }
  };

  const handleUpload = async () => {
    if (!file) return setError('Please select a file');
    setUploading(true);
    setError('');
    try {
      const res = await resumeAPI.upload(file, title || 'Untitled Resume');
      setResult(res.data);
      setTimeout(() => navigate(`/resume/${res.data.id}`), 2000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="upload-page">
      <div className="page-header">
        <h1>Upload Resume</h1>
        <p>Upload your resume for AI-powered analysis and scoring</p>
      </div>

      <div className={`drop-zone ${dragOver ? 'drag-over' : ''} ${file ? 'has-file' : ''}`}
        onDragOver={e => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => document.getElementById('file-input').click()}>
        <input id="file-input" type="file" accept=".pdf,.docx" onChange={handleFileSelect} hidden />
        {file ? (
          <div className="file-preview">
            <FileText size={48} className="file-icon" />
            <span className="file-name">{file.name}</span>
            <span className="file-size">{(file.size / 1024).toFixed(1)} KB</span>
          </div>
        ) : (
          <div className="drop-content">
            <Upload size={48} className="upload-icon" />
            <h3>Drag & drop your resume here</h3>
            <p>or click to browse • PDF, DOCX up to 10MB</p>
          </div>
        )}
      </div>

      <div className="upload-form">
        <div className="input-group">
          <input type="text" placeholder="Resume Title (optional)" value={title}
            onChange={e => setTitle(e.target.value)} />
        </div>
        {error && <div className="form-error"><AlertCircle size={16} /> {error}</div>}
        {result && (
          <div className="upload-success">
            <CheckCircle size={20} /> Resume analyzed! Redirecting...
          </div>
        )}
        <button className="btn-primary btn-lg" onClick={handleUpload} disabled={!file || uploading}>
          {uploading ? <><Loader size={18} className="spin" /> Analyzing...</> : <><Upload size={18} /> Upload & Analyze</>}
        </button>
      </div>

      <div className="upload-info-cards">
        <div className="info-card"><span className="info-icon">🔍</span><h4>Smart Parsing</h4><p>AI extracts skills, experience, and education automatically</p></div>
        <div className="info-card"><span className="info-icon">📊</span><h4>ATS Scoring</h4><p>Get a detailed score breakdown with improvement tips</p></div>
        <div className="info-card"><span className="info-icon">🎯</span><h4>Job Matching</h4><p>Match your resume against job descriptions instantly</p></div>
      </div>
    </div>
  );
}
