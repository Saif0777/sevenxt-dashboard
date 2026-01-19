import React, { useState, useEffect } from 'react';
import Login from './components/Login';
import DashboardLayout from './layout/DashboardLayout';

// 📂 EXISTING IMPORTS
import BlogPosting from './pages/BlogPosting';
import KeywordGen from './pages/KeywordGen'; // Assuming this is also in pages/ based on your message
import SKUPrinting from './pages/SKUPrinting';

// ✅ NEW IMPORT (Pointing to the 'pages' folder)
import AmazonSuggestions from './pages/AmazonSuggestions'; 

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isChecking, setIsChecking] = useState(true);
  const [activeTab, setActiveTab] = useState('blog');
  
  // Multi-User State
  const [userName, setUserName] = useState('');
  const [userRole, setUserRole] = useState('');

  // 1. Check Login Status
  useEffect(() => {
    const token = localStorage.getItem('authToken');
    const savedName = localStorage.getItem('userName');
    const savedRole = localStorage.getItem('userRole');

    if (token) {
      setIsAuthenticated(true);
      if (savedName) setUserName(savedName);
      if (savedRole) setUserRole(savedRole);
    }
    setIsChecking(false);
  }, []);

  // 2. Login Handler
  const handleLoginSuccess = (token) => {
    setIsAuthenticated(true);
    setUserName(localStorage.getItem('userName'));
    setUserRole(localStorage.getItem('userRole'));
  };

  // 3. Logout Handler
  const handleLogout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userName');
    localStorage.removeItem('userRole');
    setIsAuthenticated(false);
    setUserName('');
    setUserRole('');
    setActiveTab('blog'); 
  };

  if (isChecking) return <div className="min-h-screen bg-slate-950 flex items-center justify-center text-white">Loading...</div>;

  if (!isAuthenticated) {
    return <Login onLogin={handleLoginSuccess} />;
  }

  return (
    <DashboardLayout 
      activeTab={activeTab} 
      setActiveTab={setActiveTab} 
      onLogout={handleLogout}
      userName={userName}
      userRole={userRole}
    >
      <div style={{ display: activeTab === 'blog' ? 'block' : 'none' }}>
        <BlogPosting />
      </div>
      
      <div style={{ display: activeTab === 'keyword' ? 'block' : 'none' }}>
        <KeywordGen />
      </div>

      {/* ✅ NEW TAB: BULK SUGGESTIONS */}
      <div style={{ display: activeTab === 'suggestions' ? 'block' : 'none' }}>
        <AmazonSuggestions />
      </div>
      
      <div style={{ display: activeTab === 'sku' ? 'block' : 'none' }}>
        <SKUPrinting />
      </div>

    </DashboardLayout>
  );
}

export default App;