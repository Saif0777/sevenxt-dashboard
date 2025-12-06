import React, { useState } from 'react';
import DashboardLayout from './layout/DashboardLayout';
import BlogPosting from './pages/BlogPosting';
import KeywordGen from './pages/KeywordGen';
import SKUPrinting from './pages/SKUPrinting';


function App() {
  const [activeTab, setActiveTab] = useState('blog');

  const renderContent = () => {
    switch (activeTab) {
      case 'blog': return <BlogPosting />;
      case 'keyword': return <KeywordGen />;
      case 'sku': return <SKUPrinting />;
      default: return <BlogPosting />;
    }
  };

  return (
    <DashboardLayout activeTab={activeTab} setActiveTab={setActiveTab}>
      {renderContent()}
    </DashboardLayout>
  );
}

export default App;