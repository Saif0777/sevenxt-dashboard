import React, { useState } from 'react';
import { Lock, User, LogIn, Loader2 } from 'lucide-react';
import api from '../services/api';

const Login = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Send both username and password
      const response = await api.post('/api/verify-login', { 
        username: username,
        password: password 
      });

      if (response.data.success) {
        // Save token and user info
        localStorage.setItem('authToken', response.data.token);
        localStorage.setItem('userName', response.data.name);
        localStorage.setItem('userRole', response.data.role);
        
        // Pass the token up to the parent App
        onLogin(response.data.token);
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Login Failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md">
        
        <div className="text-center mb-8">
          <div className="bg-brand-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
            <Lock className="text-brand-600" size={32} />
          </div>
          <h1 className="text-2xl font-bold text-slate-800">Team Login</h1>
          <p className="text-slate-500 text-sm">Enter your credentials to access the dashboard</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          
          {/* Username Input */}
          <div>
            <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Username</label>
            <div className="relative">
              <User className="absolute left-3 top-3 text-slate-400" size={20} />
              <input 
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-slate-200 rounded-xl focus:border-brand-500 focus:ring-2 focus:ring-brand-200 outline-none transition-all"
                placeholder="e.g. victor"
                required
              />
            </div>
          </div>

          {/* Password Input */}
          <div>
            <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-3 text-slate-400" size={20} />
              <input 
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-slate-200 rounded-xl focus:border-brand-500 focus:ring-2 focus:ring-brand-200 outline-none transition-all"
                placeholder="••••••••"
                required
              />
            </div>
          </div>

          {error && (
            <div className="p-3 bg-red-50 text-red-600 text-sm rounded-lg text-center font-medium">
              {error}
            </div>
          )}

          <button 
            type="submit" 
            disabled={loading}
            className="w-full py-3 bg-brand-600 hover:bg-brand-700 text-white font-bold rounded-xl shadow-lg hover:shadow-xl transition-all flex justify-center items-center gap-2"
          >
            {loading ? <Loader2 className="animate-spin" /> : <LogIn size={20} />}
            {loading ? 'Verifying...' : 'Sign In'}
          </button>

        </form>
      </div>
    </div>
  );
};

export default Login;