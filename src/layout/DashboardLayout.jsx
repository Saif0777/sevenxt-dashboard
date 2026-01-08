import React, { useState } from 'react';
import { BookOpen, Printer, Search, Menu, ChevronRight, LogOut, ShieldCheck } from 'lucide-react';
import logoAsset from '../assets/logo.jpg'; 

const DashboardLayout = ({ activeTab, setActiveTab, children }) => {
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  const menuItems = [
    { id: 'blog', label: 'Amazon Blog Engine', icon: <BookOpen size={20} />, desc: 'Product to Post' },
    { id: 'keyword', label: 'SEO Link Generator', icon: <Search size={20} />, desc: 'ASIN & Keywords' },
    { id: 'sku', label: 'SKU Print Ops', icon: <Printer size={20} />, desc: 'Label Management' },
  ];

  // --- 🆕 LOGOUT LOGIC ---
  const handleLogout = () => {
    // 1. Remove the security token
    localStorage.removeItem('seven_xt_token');
    // 2. Reload the page (App.jsx will see no token -> Show Login)
    window.location.reload();
  };

  return (
    <div className="flex h-screen bg-[#F2F4F7] text-slate-900 font-sans selection:bg-brand-100 selection:text-brand-900">
      
      {/* Sidebar */}
      <aside className={`${isMobileOpen ? 'translate-x-0' : '-translate-x-full'} md:translate-x-0 w-80 bg-dark-900 text-slate-300 shadow-2xl fixed md:relative z-50 h-full transition-transform duration-300 ease-in-out flex flex-col border-r border-dark-800`}>
        
        {/* Brand Header */}
        <div className="p-6 border-b border-dark-800 flex flex-col gap-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-white rounded-lg flex items-center justify-center overflow-hidden p-1 shadow-lg shadow-brand-900/20">
               <img src={logoAsset} alt="SevenXT" className="w-full h-full object-contain" />
            </div>
            <div>
               <h1 className="font-heading font-bold text-white text-lg tracking-wide leading-tight">SEVENXT</h1>
               <span className="text-[10px] font-bold text-brand-600 uppercase tracking-widest">Electronics</span>
            </div>
          </div>
          <p className="text-[10px] text-slate-500 font-medium uppercase tracking-wide border-t border-dark-700 pt-3 mt-1">
            SevenXT Electronics Pvt Ltd
          </p>
        </div>
        
        {/* Navigation */}
        <nav className="mt-6 px-4 space-y-2 flex-1">
          <p className="px-4 text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3">Modules</p>
          {menuItems.map((item) => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => { setActiveTab(item.id); setIsMobileOpen(false); }}
                className={`group w-full flex items-center justify-between px-4 py-4 rounded-xl transition-all duration-300 border
                  ${isActive 
                    ? 'bg-brand-600 text-white shadow-lg shadow-brand-600/20 border-brand-500' 
                    : 'bg-transparent border-transparent hover:bg-dark-800 hover:text-white hover:border-dark-700'}`}
              >
                <div className="flex items-center gap-4">
                  <div className={`${isActive ? 'text-white' : 'text-slate-500 group-hover:text-brand-500'} transition-colors`}>
                    {item.icon}
                  </div>
                  <div className="text-left">
                    <span className={`block text-sm font-heading font-bold ${isActive ? 'text-white' : 'text-slate-300 group-hover:text-white'}`}>{item.label}</span>
                    <span className={`block text-[10px] ${isActive ? 'text-brand-100' : 'text-slate-600 group-hover:text-slate-400'}`}>{item.desc}</span>
                  </div>
                </div>
                {isActive && <ChevronRight size={16} className="text-brand-200" />}
              </button>
            )
          })}
        </nav>

        {/* Footer (LOGOUT BUTTON) */}
        <div className="p-4 border-t border-dark-800 bg-dark-950/30">
          
          {/* Added onClick here 👇 */}
          <div 
            onClick={handleLogout} 
            className="flex items-center gap-3 p-3 rounded-xl hover:bg-red-500/10 hover:border-red-500/50 transition-all cursor-pointer group border border-transparent"
            title="Secure Logout"
          >
            <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-brand-600 to-brand-800 flex items-center justify-center text-white font-bold font-heading border-2 border-dark-700 group-hover:border-red-500 transition-all">
              SX
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-bold text-white truncate font-heading group-hover:text-red-400 transition-colors">Admin Console</p>
              <div className="flex items-center gap-1.5">
                 <ShieldCheck size={10} className="text-green-500" />
                 <p className="text-[10px] text-slate-500 truncate">System Operational</p>
              </div>
            </div>
            <LogOut size={16} className="text-slate-600 group-hover:text-red-500 transition-colors" />
          </div>

        </div>

      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden relative bg-[#F2F4F7]">
        {/* Header */}
        <header className="bg-white h-20 border-b border-slate-200 flex items-center justify-between px-8 sticky top-0 z-40 shadow-sm">
          <div className="flex items-center gap-4">
            <button onClick={() => setIsMobileOpen(!isMobileOpen)} className="md:hidden p-2 text-slate-600 hover:bg-slate-100 rounded-lg">
              <Menu />
            </button>
            <div>
               <h2 className="text-2xl font-heading font-bold text-slate-800 tracking-tight flex items-center gap-2">
                {menuItems.find(i => i.id === activeTab)?.label}
                <span className="text-brand-600">.</span>
               </h2>
            </div>
          </div>
          <div className="flex items-center gap-6">
              <div className="text-right hidden md:block">
                 <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Current Session</p>
                 <p className="text-xs font-medium text-slate-700">admin@sevenxt.com</p>
              </div>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-6 md:p-10 scroll-smooth">
          <div className="max-w-7xl mx-auto animate-fadeIn">
            {children}
          </div>
        </div>
      </main>
    </div>
  );
};

export default DashboardLayout;