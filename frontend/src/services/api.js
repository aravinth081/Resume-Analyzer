import axios from 'axios';

// The base URL routes to the proxy prefix defined in the app configuration
const API_BASE = import.meta.env.VITE_API_URL || '/_/backend/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Automatically inject JWT tokens into the headers of outgoing requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('resumeiq_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ── Auth API ──
export const authAPI = {
  register: async (data) => {
    return apiClient.post('/auth/register', {
      email: data.email,
      password: data.password,
      full_name: data.full_name,
      role: data.role || 'individual'
    });
  },
  login: async (email, password) => {
    return apiClient.post('/auth/login', {
      email,
      password,
    });
  },
  me: async () => {
    return apiClient.get('/auth/me');
  },
};

// ── Resumes API ──
export const resumeAPI = {
  upload: async (file, title) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title || 'Untitled Resume');
    return apiClient.post('/resumes/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  list: async () => {
    return apiClient.get('/resumes');
  },
  get: async (id) => {
    return apiClient.get(`/resumes/${id}`);
  },
  score: async (id) => {
    return apiClient.get(`/resumes/${id}/score`);
  },
  delete: async (id) => {
    return apiClient.delete(`/resumes/${id}`);
  },
};

// ── Jobs API ──
export const jobAPI = {
  create: async (data) => {
    return apiClient.post('/jobs', {
      title: data.title,
      company: data.company || '',
      description: data.description,
      experience_years: data.experience_years || '',
    });
  },
  list: async () => {
    return apiClient.get('/jobs');
  },
  get: async (id) => {
    return apiClient.get(`/jobs/${id}`);
  },
};

// ── Matching API ──
export const matchAPI = {
  match: async (data) => {
    return apiClient.post('/matching/match', {
      resume_id: data.resume_id,
      job_id: data.job_id,
    });
  },
  rank: async (data) => {
    return apiClient.post('/matching/rank', {
      job_id: data.job_id,
      resume_ids: data.resume_ids,
    });
  },
};

// ── Chat API ──
export const chatAPI = {
  send: async (message) => {
    return apiClient.post('/chat/message', {
      message: message,
    });
  },
  history: async () => {
    return apiClient.get('/chat/history');
  },
};

// ── Analytics API ──
export const analyticsAPI = {
  skills: async () => {
    return apiClient.get('/analytics/skills');
  },
  history: async () => {
    return apiClient.get('/analytics/history');
  },
  trends: async () => {
    return apiClient.get('/analytics/trends');
  },
};

export default { authAPI, resumeAPI, jobAPI, matchAPI, chatAPI, analyticsAPI };
