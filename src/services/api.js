import axios from 'axios';

// Create an axios instance
const api = axios.create({
  // This points to your Python Flask Server
  baseURL: 'http://localhost:5000', 
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a response interceptor to handle errors globally (Optional but good)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API Error:", error);
    return Promise.reject(error);
  }
);

// --- THIS WAS THE MISSING LINE CAUSING YOUR ERROR ---
export default api;