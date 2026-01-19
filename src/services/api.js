import axios from 'axios';

// 1. Create the Axios instance
const api = axios.create({
  // Automatically detects if running on Localhost or Cloud
  baseURL: import.meta.env.VITE_API_URL || 'https://sevenxt-dashboard.onrender.com', 
  headers: {
    'Content-Type': 'application/json',
  },
});

// 2. THE INTERCEPTOR (The Magic Fix)
// Before any request is sent, this code runs automatically.
api.interceptors.request.use(
  (config) => {
    // A. Grab the token from storage
    const token = localStorage.getItem('authToken');
    
    // B. If token exists, attach it to the headers
    if (token) {
      config.headers['X-Access-Token'] = token;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default api;