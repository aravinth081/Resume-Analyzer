import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { Sparkles, Mail, Lock, User, ArrowRight } from 'lucide-react';

export default function LoginPage() {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (isRegister) {
        await register({ email, password, full_name: fullName });
      } else {
        await login(email, password);
      }
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-bg-effects">
        <div className="bg-orb bg-orb-1"></div>
        <div className="bg-orb bg-orb-2"></div>
        <div className="bg-orb bg-orb-3"></div>
      </div>
      <div className="login-container">
        <div className="login-hero">
          <div className="hero-content">
            <div className="hero-logo"><Sparkles size={40} /> ResumeIQ</div>
            <h1>AI-Powered Resume Intelligence</h1>
            <p>Analyze, score, and match resumes with cutting-edge NLP. Get hired faster.</p>
            <div className="hero-features">
              <div className="hero-feature"><span className="dot"></span> ATS Scoring (0-100)</div>
              <div className="hero-feature"><span className="dot"></span> BERT Semantic Matching</div>
              <div className="hero-feature"><span className="dot"></span> AI Career Copilot</div>
            </div>
          </div>
        </div>
        <div className="login-form-section">
          <form onSubmit={handleSubmit} className="login-form">
            <h2>{isRegister ? 'Create Account' : 'Welcome Back'}</h2>
            <p className="form-subtitle">
              {isRegister ? 'Start your career journey today' : 'Sign in to your dashboard'}
            </p>
            {error && <div className="form-error">{error}</div>}
            {isRegister && (
              <div className="input-group">
                <User size={18} />
                <input type="text" placeholder="Full Name" value={fullName}
                  onChange={e => setFullName(e.target.value)} required />
              </div>
            )}
            <div className="input-group">
              <Mail size={18} />
              <input type="email" placeholder="Email Address" value={email}
                onChange={e => setEmail(e.target.value)} required />
            </div>
            <div className="input-group">
              <Lock size={18} />
              <input type="password" placeholder="Password" value={password}
                onChange={e => setPassword(e.target.value)} required minLength={8} />
            </div>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Please wait...' : (isRegister ? 'Create Account' : 'Sign In')}
              <ArrowRight size={18} />
            </button>
            <p className="form-toggle">
              {isRegister ? 'Already have an account?' : "Don't have an account?"}
              <button type="button" onClick={() => { setIsRegister(!isRegister); setError(''); }}>
                {isRegister ? 'Sign In' : 'Sign Up'}
              </button>
            </p>
          </form>
        </div>
      </div>
    </div>
  );
}
