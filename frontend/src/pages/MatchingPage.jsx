import { useState, useEffect } from 'react';
import { resumeAPI, jobAPI, matchAPI } from '../services/api';
import { Target, Plus, Search, Briefcase } from 'lucide-react';

export default function MatchingPage() {
  const [resumes, setResumes] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [selectedResume, setSelectedResume] = useState('');
  const [selectedJob, setSelectedJob] = useState('');
  const [result, setResult] = useState(null);
  const [showCreate, setShowCreate] = useState(false);
  const [jd, setJd] = useState({ title: '', company: '', description: '', experience_years: '' });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    resumeAPI.list().then(r => setResumes(r.data.filter(x => x.status === 'completed'))).catch(() => {});
    jobAPI.list().then(r => setJobs(r.data)).catch(() => {});
  }, []);

  const createJob = async () => {
    if (!jd.title || jd.description.length < 50) return;
    setLoading(true);
    try {
      const res = await jobAPI.create(jd);
      setJobs(prev => [res.data, ...prev]);
      setSelectedJob(res.data.id);
      setShowCreate(false);
      setJd({ title: '', company: '', description: '', experience_years: '' });
    } catch (err) { alert(err.response?.data?.detail || 'Error'); }
    finally { setLoading(false); }
  };

  const runMatch = async () => {
    if (!selectedResume || !selectedJob) return;
    setLoading(true);
    try {
      const res = await matchAPI.match({ resume_id: selectedResume, job_id: selectedJob });
      setResult(res.data);
    } catch (err) { alert(err.response?.data?.detail || 'Error'); }
    finally { setLoading(false); }
  };

  const suitColor = { strong_match: '#22c55e', good_match: '#6366f1', moderate_match: '#f59e0b', weak_match: '#ef4444' };

  return (
    <div className="matching-page">
      <div className="page-header">
        <h1><Target size={24} /> Job Matching</h1>
        <button className="btn-secondary" onClick={() => setShowCreate(!showCreate)}>
          <Plus size={18} /> Add Job Description
        </button>
      </div>

      {showCreate && (
        <div className="create-job-form card">
          <h3>New Job Description</h3>
          <input placeholder="Job Title" value={jd.title} onChange={e => setJd({...jd, title: e.target.value})} />
          <input placeholder="Company (optional)" value={jd.company} onChange={e => setJd({...jd, company: e.target.value})} />
          <textarea placeholder="Full job description (min 50 chars)" rows={6} value={jd.description}
            onChange={e => setJd({...jd, description: e.target.value})} />
          <input placeholder="Experience required (e.g., 3+ years)" value={jd.experience_years}
            onChange={e => setJd({...jd, experience_years: e.target.value})} />
          <button className="btn-primary" onClick={createJob} disabled={loading}>Create & Analyze</button>
        </div>
      )}

      <div className="match-controls card">
        <div className="match-selectors">
          <div className="selector">
            <label>Select Resume</label>
            <select value={selectedResume} onChange={e => setSelectedResume(e.target.value)}>
              <option value="">Choose a resume...</option>
              {resumes.map(r => <option key={r.id} value={r.id}>{r.title} (Score: {r.overall_score || 'N/A'})</option>)}
            </select>
          </div>
          <div className="selector">
            <label>Select Job</label>
            <select value={selectedJob} onChange={e => setSelectedJob(e.target.value)}>
              <option value="">Choose a job...</option>
              {jobs.map(j => <option key={j.id} value={j.id}>{j.title}{j.company ? ` — ${j.company}` : ''}</option>)}
            </select>
          </div>
        </div>
        <button className="btn-primary btn-lg" onClick={runMatch} disabled={!selectedResume || !selectedJob || loading}>
          <Search size={18} /> {loading ? 'Matching...' : 'Run Match'}
        </button>
      </div>

      {result && (
        <div className="match-result card">
          <div className="match-score-hero">
            <div className="match-circle" style={{ borderColor: suitColor[result.role_suitability] || '#6366f1' }}>
              <span className="match-pct">{result.match_percentage}%</span>
              <span className="match-label">Match</span>
            </div>
            <span className="suit-badge" style={{ background: suitColor[result.role_suitability] }}>
              {result.role_suitability?.replace(/_/g, ' ')}
            </span>
          </div>
          <div className="match-details">
            <div className="match-col">
              <h4>✅ Matching Skills</h4>
              <div className="skill-tags">{result.matching_skills?.map((s, i) => <span key={i} className="skill-tag match">{s}</span>)}</div>
            </div>
            <div className="match-col">
              <h4>❌ Missing Skills</h4>
              <div className="skill-tags">{result.missing_skills?.map((s, i) => <span key={i} className="skill-tag missing">{s}</span>)}</div>
            </div>
          </div>
          {result.recommendations?.length > 0 && (
            <div className="recommendations">
              <h4>💡 Recommendations</h4>
              <ul>{result.recommendations.map((r, i) => <li key={i}>{r}</li>)}</ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
