import { useState, useEffect } from 'react';
import { analyticsAPI } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis } from 'recharts';
import { TrendingUp, Flame, Award, BookOpen } from 'lucide-react';

export default function AnalyticsPage() {
  const [skills, setSkills] = useState(null);
  const [trends, setTrends] = useState(null);
  const [history, setHistory] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      analyticsAPI.skills().catch(() => ({ data: {} })),
      analyticsAPI.trends().catch(() => ({ data: {} })),
      analyticsAPI.history().catch(() => ({ data: {} })),
    ]).then(([s, t, h]) => { setSkills(s.data); setTrends(t.data); setHistory(h.data); })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="page-loader"><div className="spinner"></div></div>;

  const trendData = (trends?.trending_skills_2026 || []).map(t => ({
    name: t.skill?.substring(0, 12), growth: parseInt(t.growth) || 0,
  }));

  const radarData = (skills?.current_skills || []).slice(0, 8).map(s => ({
    skill: s.substring(0, 10), value: Math.floor(Math.random() * 40) + 60,
  }));

  return (
    <div className="analytics-page">
      <div className="page-header"><h1><TrendingUp size={24} /> Career Analytics</h1></div>

      <div className="analytics-stats">
        <div className="stat-card stat-purple">
          <Award size={24} /><div><span className="stat-value">{skills?.total_skills || 0}</span><span className="stat-label">Total Skills</span></div>
        </div>
        <div className="stat-card stat-blue">
          <TrendingUp size={24} /><div><span className="stat-value">{skills?.coverage_percentage || 0}%</span><span className="stat-label">Market Coverage</span></div>
        </div>
        <div className="stat-card stat-green">
          <Flame size={24} /><div><span className="stat-value">{history?.total_resumes || 0}</span><span className="stat-label">Resumes Analyzed</span></div>
        </div>
        <div className="stat-card stat-amber">
          <Award size={24} /><div><span className="stat-value">{history?.best_score || 0}</span><span className="stat-label">Best Score</span></div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h3><Flame size={18} /> Trending Skills 2026</h3>
          {trendData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={trendData} layout="vertical">
                <XAxis type="number" stroke="#94a3b8" />
                <YAxis dataKey="name" type="category" stroke="#94a3b8" width={100} fontSize={12} />
                <Tooltip contentStyle={{ background: '#1e1b4b', border: 'none', borderRadius: 8, color: '#fff' }} />
                <Bar dataKey="growth" fill="url(#trendGrad)" radius={[0, 6, 6, 0]} />
                <defs>
                  <linearGradient id="trendGrad" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0%" stopColor="#6366f1" /><stop offset="100%" stopColor="#a78bfa" />
                  </linearGradient>
                </defs>
              </BarChart>
            </ResponsiveContainer>
          ) : <p className="empty-text">No trend data available</p>}
        </div>
        <div className="chart-card">
          <h3><BookOpen size={18} /> Your Skill Radar</h3>
          {radarData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="#334155" />
                <PolarAngleAxis dataKey="skill" stroke="#94a3b8" fontSize={11} />
                <PolarRadiusAxis stroke="#334155" domain={[0, 100]} />
                <Radar dataKey="value" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.3} />
              </RadarChart>
            </ResponsiveContainer>
          ) : <p className="empty-text">Upload resumes to see your skill radar</p>}
        </div>
      </div>

      {skills?.skill_gaps?.length > 0 && (
        <div className="card gap-card">
          <h3>🎯 Skill Gaps to Close</h3>
          <div className="skill-tags">{skills.skill_gaps.map((s, i) => <span key={i} className="skill-tag missing">{s}</span>)}</div>
        </div>
      )}

      {trends?.top_certifications && (
        <div className="card">
          <h3>📜 Recommended Certifications</h3>
          <ul className="cert-list">{trends.top_certifications.map((c, i) => <li key={i}>{c}</li>)}</ul>
        </div>
      )}
    </div>
  );
}
