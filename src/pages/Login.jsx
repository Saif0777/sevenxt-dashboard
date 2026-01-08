import React, { useState } from 'react';
import { Lock, ArrowRight, ShieldCheck } from 'lucide-react';
import api from '../services/api';

const Login = ({ onLoginSuccess }) => {
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Call the verification endpoint
      const response = await api.post('/api/verify-login', { password });
      
      if (response.data.success) {
        // Save token and notify App.jsx
        localStorage.setItem('seven_xt_token', password);
        onLoginSuccess();
      }
    } catch (err) {
      setError('⛔ Access Denied: Invalid Security Code');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl overflow-hidden w-full max-w-md">
        <div className="bg-brand-600 p-8 text-center">
          <div className="bg-white/20 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 backdrop-blur-sm">
            <Lock className="text-white" size={32} />
          </div>
          <h1 className="text-2xl font-bold text-white tracking-wider">SEVEN XT</h1>
          <p className="text-brand-100 text-sm mt-1">Enterprise Automation Dashboard</p>
        </div>

        <div className="p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase mb-2">
                Security Access Code
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full p-4 border border-slate-300 rounded-xl focus:border-brand-500 focus:ring-2 focus:ring-brand-200 outline-none text-slate-800 font-mono text-lg text-center"
                placeholder="Enter PIN..."
                autoFocus
              />
            </div>

            {error && (
              <div className="p-3 bg-red-50 text-red-600 text-sm rounded-lg text-center font-medium border border-red-100">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading || !password}
              className="w-full py-4 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded-xl transition-all flex justify-center items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Verifying...' : (
                <>Authenticate <ArrowRight size={18} /></>
              )}
            </button>
          </form>
          
          <div className="mt-6 text-center">
            <p className="text-[10px] text-slate-400 flex items-center justify-center gap-1">
              <ShieldCheck size={12} /> Secure Environment v1.2
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;