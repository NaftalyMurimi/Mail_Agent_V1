import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
});

// ── Attach token to every request ─────────────────────
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ── Auto logout on 401 ────────────────────────────────
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ── Auth ──────────────────────────────────────────────
export const authAPI = {
  signup: (data) => api.post('/auth/signup', data),
  login:  (data) => api.post('/auth/login',  data),
  logout: ()     => api.post('/auth/logout'),
};

// ── User ──────────────────────────────────────────────
export const userAPI = {
  getMe:    ()     => api.get('/users/me'),
  updateMe: (data) => api.put('/users/me', data),
};

// ── Emails ────────────────────────────────────────────
export const emailAPI = {
  getAll: (params) => api.get('/emails', { params }),
  getOne: (id)     => api.get(`/emails/${id}`),
  delete: (id)     => api.delete(`/emails/${id}`),
};

// ── Jobs ──────────────────────────────────────────────
export const jobAPI = {
  getAll:       (params) => api.get('/jobs', { params }),
  getOne:       (id)     => api.get(`/jobs/${id}`),
  updateStatus: (id, status) => api.put(`/jobs/${id}`, { status }),
};

// ── CV ────────────────────────────────────────────────
export const cvAPI = {
  upload: (file) => {
    const form = new FormData();
    form.append('file', file);
    return api.post('/cv/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  getAll: () => api.get('/cv'),
  delete: (id) => api.delete(`/cv/${id}`),
};

// ── Scan ──────────────────────────────────────────────
export const scanAPI = {
  trigger: () => api.post('/scan'),
};

// ── Settings ──────────────────────────────────────────
export const settingsAPI = {
  get:    ()     => api.get('/settings'),
  update: (data) => api.put('/settings', data),
};

export default api;