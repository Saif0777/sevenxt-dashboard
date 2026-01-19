import React, { useState, useEffect } from 'react';
import Login from './components/Login';
import DashboardLayout from './layout/DashboardLayout';

// ⚠️ CHECK PATHS: Ensure these match where your files actually are!
// Based on your previous errors, KeywordGen might be in 'features/...'
import BlogPosting from './pages/BlogPosting';
import KeywordGen from './pages/KeywordGen'; // Updated to likely correct path
import SKUPrinting from './pages/SKUPrinting';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isChecking, setIsChecking] = useState(true);
  const [activeTab, setActiveTab] = useState('blog');
  
  // New State for Multi-User
  const [userName, setUserName] = useState('');
  const [userRole, setUserRole] = useState('');

  // 1. Check Login Status on Load
  useEffect(() => {
    // We now use 'authToken' to match the new Login.jsx
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

  // 2. Handle Login Success (Called by Login.jsx)
  const handleLoginSuccess = (token) => {
    setIsAuthenticated(true);
    // Refresh user data from storage immediately
    setUserName(localStorage.getItem('userName'));
    setUserRole(localStorage.getItem('userRole'));
  };

  // 3. Handle Logout
  const handleLogout = () => {
    // Remove all new keys
    localStorage.removeItem('authToken');
    localStorage.removeItem('userName');
    localStorage.removeItem('userRole');
    
    // Reset State
    setIsAuthenticated(false);
    setUserName('');
    setUserRole('');
    setActiveTab('blog'); // Reset tab
  };

  if (isChecking) return <div className="min-h-screen bg-slate-950 flex items-center justify-center text-white">Loading...</div>;

  // Show Login if not authenticated
  if (!isAuthenticated) {
    return <Login onLogin={handleLoginSuccess} />;
  }

  return (
    <DashboardLayout 
      activeTab={activeTab} 
      setActiveTab={setActiveTab} 
      onLogout={handleLogout}
      userName={userName} // Pass name to Layout (Optional: You can use this in DashboardLayout to show "Welcome Victor")
      userRole={userRole} // Pass role (Optional: Use this to hide tabs for non-admins if needed)
    >
      {/* We use 'display: none' to keep state alive when switching tabs.
         This prevents the Keyword Generator from resetting when you click 'Blog'.
      */}
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