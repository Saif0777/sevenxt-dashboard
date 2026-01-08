import React, { useState, useEffect } from 'react';
import Login from './pages/Login';
import DashboardLayout from './layout/DashboardLayout';
import BlogPosting from './pages/BlogPosting';
import KeywordGen from './pages/KeywordGen';
import SKUPrinting from './pages/SKUPrinting';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isChecking, setIsChecking] = useState(true);
  const [activeTab, setActiveTab] = useState('blog');

  useEffect(() => {
    const token = localStorage.getItem('seven_xt_token');
    if (token) setIsAuthenticated(true);
    setIsChecking(false);
  }, []);

  // --- 🆕 NEW LOGOUT FUNCTION ---
  const handleLogout = () => {
    localStorage.removeItem('seven_xt_token'); // 1. Delete key
    setIsAuthenticated(false);                 // 2. Lock app
    // Optional: window.location.reload();     // 3. Hard refresh to clear memory
  };

  if (isChecking) return <div className="min-h-screen bg-slate-950"/>;

  if (!isAuthenticated) {
    return <Login onLoginSuccess={() => setIsAuthenticated(true)} />;
  }

  return (
    // --- PASS THE FUNCTION DOWN HERE ---
    <DashboardLayout 
      activeTab={activeTab} 
      setActiveTab={setActiveTab} 
      onLogout={handleLogout}  // <--- Add this prop!
    >
      <div style={{ display: activeTab === 'blog' ? 'block' : 'none' }}>
        <BlogPosting />
      </div>
      <div style={{ display: activeTab === 'keyword' ? 'block' : 'none' }}>
        <KeywordGen />
      </div>
      <div style={{ display: activeTab === 'sku' ? 'block' : 'none' }}>
        <SKUPrinting />
      </div>
    </DashboardLayout>
  );
}

export default App;