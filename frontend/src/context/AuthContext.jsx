import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // On mount, check if a token exists and fetch user profile
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('resumeiq_token');
      if (token) {
        try {
          const res = await authAPI.me();
          setUser(res.data);
        } catch (err) {
          console.error('Session restoration failed:', err);
          logout();
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email, password) => {
    setLoading(true);
    try {
      const res = await authAPI.login(email, password);
      const { access_token } = res.data;
      localStorage.setItem('resumeiq_token', access_token);
      
      const profileRes = await authAPI.me();
      setUser(profileRes.data);
      return profileRes.data;
    } catch (err) {
      localStorage.removeItem('resumeiq_token');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const register = async (data) => {
    setLoading(true);
    try {
      const res = await authAPI.register(data);
      const { access_token } = res.data;
      localStorage.setItem('resumeiq_token', access_token);
      
      const profileRes = await authAPI.me();
      setUser(profileRes.data);
      return profileRes.data;
    } catch (err) {
      localStorage.removeItem('resumeiq_token');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('resumeiq_token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
