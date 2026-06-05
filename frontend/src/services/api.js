/**
 * api.js — Service centralisé pour tous les appels au backend Django
 * Utilise Axios avec intercepteurs JWT automatiques
 */

import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// ─── INSTANCE AXIOS ──────────────────────────────────────────────────────────
const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000,
});

// Intercepteur : ajoute le token JWT à chaque requête
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Intercepteur : rafraîchit le token si expiré (401)
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      try {
        const refresh = localStorage.getItem('refresh_token');
        const { data } = await axios.post(`${API_URL}/auth/refresh/`, { refresh });
        localStorage.setItem('access_token', data.access);
        original.headers.Authorization = `Bearer ${data.access}`;
        return api(original);
      } catch {
        // Token expiré définitivement → déconnexion
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// ─── AUTH ─────────────────────────────────────────────────────────────────────
export const authAPI = {
  login: (username, password) =>
    api.post('/auth/login/', { username, password }),

  register: (data) =>
    api.post('/auth/register/', data),

  refresh: (refresh) =>
    api.post('/auth/refresh/', { refresh }),

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },
};

// ─── DASHBOARD ────────────────────────────────────────────────────────────────
export const dashboardAPI = {
  get: () => api.get('/dashboard/'),
};

// ─── TRANSACTIONS ─────────────────────────────────────────────────────────────
export const transactionAPI = {
  list: (params = {}) => api.get('/transactions/', { params }),
  create: (data) => api.post('/transactions/', data),
  update: (id, data) => api.put(`/transactions/${id}/`, data),
  delete: (id) => api.delete(`/transactions/${id}/`),
  repartir: (montant_eur) => api.post('/transactions/repartir/', { montant_eur }),
  stats: (mois, annee) => api.get('/transactions/stats/', { params: { mois, annee } }),
};

// ─── CATÉGORIES ───────────────────────────────────────────────────────────────
export const categoryAPI = {
  list: () => api.get('/categories/'),
  create: (data) => api.post('/categories/', data),
  update: (id, data) => api.put(`/categories/${id}/`, data),
  delete: (id) => api.delete(`/categories/${id}/`),
};

// ─── BUDGETS ──────────────────────────────────────────────────────────────────
export const budgetAPI = {
  list: (mois, annee) => api.get('/budgets/', { params: { mois, annee } }),
  create: (data) => api.post('/budgets/', data),
  update: (id, data) => api.put(`/budgets/${id}/`, data),
};

// ─── OBJECTIFS ────────────────────────────────────────────────────────────────
export const objectifAPI = {
  list: () => api.get('/objectifs/'),
  create: (data) => api.post('/objectifs/', data),
  update: (id, data) => api.put(`/objectifs/${id}/`, data),
  delete: (id) => api.delete(`/objectifs/${id}/`),
  alimenter: (id, montant_eur) => api.post(`/objectifs/${id}/alimenter/`, { montant_eur }),
};

// ─── RÉCURRENTES ──────────────────────────────────────────────────────────────
export const recurrenteAPI = {
  list: () => api.get('/recurrentes/'),
  create: (data) => api.post('/recurrentes/', data),
  delete: (id) => api.delete(`/recurrentes/${id}/`),
  appliquer: (id) => api.post(`/recurrentes/${id}/appliquer/`),
};

// ─── TRANSFERTS ───────────────────────────────────────────────────────────────
export const transfertAPI = {
  list: () => api.get('/transferts/'),
  create: (data) => api.post('/transferts/', data),
  simuler: (montant_eur) => api.post('/transferts/simuler/', { montant_eur }),
};

// ─── ANALYSE ──────────────────────────────────────────────────────────────────
export const analyseAPI = {
  get: (mois, annee) => api.get('/analyse/', { params: { mois, annee } }),
};

// ─── PROFIL ───────────────────────────────────────────────────────────────────
export const profileAPI = {
  get: () => api.get('/profile/'),
  update: (data) => api.put('/profile/', data),
};

export default api;
