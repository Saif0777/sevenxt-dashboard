import axios from 'axios';

// Create an axios instance
const api = axios.create({
  // Use VITE_API_URL if available (for production), else localhost
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000', 
  headers: {
    'Content-Type': 'application/json',
  },
});

// --- INTERCEPTOR: ADD PASSWORD TO EVERY REQUEST ---
api.interceptors.request.use((config) => {
  // 1. Get token from LocalStorage (Saved after login)
  const token = localStorage.getItem('seven_xt_token');
  
  // 2. If token exists, attach it to headers
  if (token) {
    config.headers['X-Access-Token'] = token;
  }
  return config;
});

// Error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API Error:", error);
    // Optional: If 401 Unauthorized, force logout
    if (error.response && error.response.status === 401) {
        localStorage.removeItem('seven_xt_token');
        window.location.reload(); 
    }
    return Promise.reject(error);
  }
);

export default api;