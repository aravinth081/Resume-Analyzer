import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { resumeAPI } from '../services/api';
import { FileText, Award, CheckCircle, AlertTriangle, ArrowLeft, Lightbulb } from 'lucide-react';

export default function ResumeDetailPage() {
  const { id } = useParams();
  const [resume, setResume] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    resumeAPI.get(id).then(r => setResume(r.data)).catch(() => {}).finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="page-loader"><div className="spinner"></div></div>;
  if (!resume) return <div className="page-error">Resume not found</div>;

  const parsed = resume.parsed_data || {};
  const sections = resume.section_scores || {};
  const scoreColor = (s) => s >= 70 ? 'good' : s >= 50 ? 'ok' : 'low';

  return (
    <div className="resume-detail-page">
      <Link to="/dashboard" className="back-link"><ArrowLeft size={16} /> Back to Dashboard</Link>

      <div className="detail-header">
        <div className="detail-title-row">
          <FileText size={28} />
          <div>
            <h1>{resume.title}</h1>
            <span className="detail-meta">v{resume.version} • {resume.file_type.toUpperCase()} • {new Date(resume.created_at).toLocaleDateString()}</span>
          </div>
        </div>
        {resume.overall_score != null && (
          <div className={`score-circle ${scoreColor(resume.overall_score)}`}>
            <span className="score-num">{resume.overall_score}</span>
            <span className="score-label">ATS Score</span>
          </div>
        )}
      </div>

      {/* Section Scores */}
      {Object.keys(sections).length > 0 && (
        <div className="sections-grid">
          <h2><Award size={20} /> Score Breakdown</h2>
          <div className="section-cards">
            {Object.entries(sections).map(([name, data]) => (
              <div key={name} className="section-card">
                <div className="section-header">
                  <span className="section-name">{name.replace(/_/g, ' ')}</span>
                  <span className={`section-score ${scoreColor(data.score)}`}>{data.score}</span>
                </div>
                <div className="score-bar"><div className="score-fill" style={{ width: `${data.score}%` }}></div></div>
                <p className="section-feedback">{data.feedback}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Suggestions */}
      {resume.suggestions?.length > 0 && (
        <div className="suggestions-card">
          <h2><Lightbulb size={20} /> Improvement Suggestions</h2>
          <ul>{resume.suggestions.map((s, i) => <li key={i}>{s}</li>)}</ul>
        </div>
      )}

      {/* Parsed Data */}
      <div className="parsed-grid">
        {parsed.skills?.length > 0 && (
          <div className="parsed-card">
            <h3>Skills ({parsed.skills.length})</h3>
            <div className="skill-tags">{parsed.skills.map((s, i) => <span key={i} className="skill-tag">{s}</span>)}</div>
          </div>
        )}
        {parsed.experience?.length > 0 && (
          <div className="parsed-card">
            <h3>Experience ({parsed.experience.length})</h3>
            {parsed.experience.map((e, i) => (
              <div key={i} className="exp-entry">
                <strong>{e.title}</strong> {e.company && `at ${e.company}`}
                {e.dates && <span className="exp-dates">{e.dates}</span>}
                {e.description && <p>{e.description}</p>}
              </div>
            ))}
          </div>
        )}
        {parsed.education?.length > 0 && (
          <div className="parsed-card">
            <h3>Education</h3>
            {parsed.education.map((e, i) => (
              <div key={i} className="edu-entry">
                <strong>{e.degree}</strong>
                {e.institution && <span> — {e.institution}</span>}
                {e.year && <span className="edu-year">{e.year}</span>}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
