import { useState, useEffect } from 'react';
import { resumeAPI, analyticsAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Upload, TrendingUp, Target, Brain, FileText, Zap } from 'lucide-react';

const COLORS = ['#6366f1', '#8b5cf6', '#a78bfa', '#c4b5fd', '#818cf8', '#7c3aed'];

export default function DashboardPage() {
  const { user } = useAuth();
  const [resumes, setResumes] = useState([]);
  const [skillData, setSkillData] = useState(null);
  const [historyData, setHistoryData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      resumeAPI.list().catch(() => ({ data: [] })),
      analyticsAPI.skills().catch(() => ({ data: {} })),
      analyticsAPI.history().catch(() => ({ data: { entries: [] } })),
    ]).then(([r, s, h]) => {
      setResumes(r.data);
      setSkillData(s.data);
      setHistoryData(h.data);
    }).finally(() => setLoading(false));
  }, []);

  const latestScore = resumes.find(r => r.overall_score)?.overall_score || 0;
  const totalResumes = resumes.length;
  const completedResumes = resumes.filter(r => r.status === 'completed').length;

  const scoreHistory = (historyData?.entries || []).map(e => ({
    name: e.title?.substring(0, 15) || 'Resume',
    score: e.score || 0,
  }));

  const skillPie = (skillData?.current_skills || []).slice(0, 6).map((s, i) => ({
    name: s, value: Math.random() * 50 + 50,
  }));

  if (loading) return <div className="page-loader"><div className="spinner"></div></div>;

  return (
    <div className="dashboard-page">
      <div className="page-header">
        <div>
          <h1>Welcome back, {user?.full_name?.split(' ')[0]} 👋</h1>
          <p>Here's your career intelligence overview</p>
        </div>
        <Link to="/upload" className="btn-primary"><Upload size={18} /> Upload Resume</Link>
      </div>

      <div className="stats-grid">
        <div className="stat-card stat-purple">
          <div className="stat-icon"><Zap size={24} /></div>
          <div className="stat-info">
            <span className="stat-value">{latestScore}</span>
            <span className="stat-label">ATS Score</span>
          </div>
        </div>
        <div className="stat-card stat-blue">
          <div className="stat-icon"><FileText size={24} /></div>
          <div className="stat-info">
            <span className="stat-value">{totalResumes}</span>
            <span className="stat-label">Resumes</span>
          </div>
        </div>
        <div className="stat-card stat-green">
          <div className="stat-icon"><Target size={24} /></div>
          <div className="stat-info">
            <span className="stat-value">{skillData?.total_skills || 0}</span>
            <span className="stat-label">Skills Found</span>
          </div>
        </div>
        <div className="stat-card stat-amber">
          <div className="stat-icon"><TrendingUp size={24} /></div>
          <div className="stat-info">
            <span className="stat-value">{skillData?.coverage_percentage || 0}%</span>
            <span className="stat-label">Market Coverage</span>
          </div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h3>Score History</h3>
          {scoreHistory.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={scoreHistory}>
                <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} />
                <YAxis stroke="#94a3b8" fontSize={12} domain={[0, 100]} />
                <Tooltip contentStyle={{ background: '#1e1b4b', border: 'none', borderRadius: 8, color: '#fff' }} />
                <Bar dataKey="score" fill="url(#gradient)" radius={[6, 6, 0, 0]} />
                <defs>
                  <linearGradient id="gradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#8b5cf6" />
                    <stop offset="100%" stopColor="#6366f1" />
                  </linearGradient>
                </defs>
              </BarChart>
            </ResponsiveContainer>
          ) : <p className="empty-text">Upload resumes to see score trends</p>}
        </div>
        <div className="chart-card">
          <h3>Skill Distribution</h3>
          {skillPie.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie data={skillPie} dataKey="value" nameKey="name" cx="50%" cy="50%"
                  innerRadius={60} outerRadius={100} paddingAngle={3}>
                  {skillPie.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip contentStyle={{ background: '#1e1b4b', border: 'none', borderRadius: 8, color: '#fff' }} />
              </PieChart>
            </ResponsiveContainer>
          ) : <p className="empty-text">No skill data yet</p>}
        </div>
      </div>

      {resumes.length > 0 && (
        <div className="recent-section">
          <h3>Recent Resumes</h3>
          <div className="resume-list">
            {resumes.slice(0, 5).map(r => (
              <Link key={r.id} to={`/resume/${r.id}`} className="resume-item">
                <FileText size={20} />
                <div className="resume-item-info">
                  <span className="resume-title">{r.title}</span>
                  <span className="resume-meta">{r.status} • v{r.version}</span>
                </div>
                {r.overall_score && (
                  <div className={`score-badge ${r.overall_score >= 70 ? 'good' : r.overall_score >= 50 ? 'ok' : 'low'}`}>
                    {r.overall_score}
                  </div>
                )}
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
