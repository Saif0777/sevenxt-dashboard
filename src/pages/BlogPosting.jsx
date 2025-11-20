import React, { useState, useRef, useEffect } from 'react';
import { Send, CheckCircle2, Globe, Terminal, Loader2, PenTool, TrendingUp, Sparkles, RefreshCw } from 'lucide-react';
import axios from 'axios';

const platformsList = ["WordPress", "Reddit", "Dev.to",'Pinterest', 'Medium', 'Facebook Page', 'Instagram'];

const BlogPosting = () => {
  const [formData, setFormData] = useState({ title: '', desc: '' });
  const [trendingTopics, setTrendingTopics] = useState([]);
  const [loadingTrends, setLoadingTrends] = useState(false);
  const [selectedPlatforms, setSelectedPlatforms] = useState([]);
  const [status, setStatus] = useState('idle'); 
  const [logs, setLogs] = useState([]);
  const [preview, setPreview] = useState(null);
  const [isExpanded, setIsExpanded] = useState(false);
  const logsEndRef = useRef(null);

  useEffect(() => { 
    if (status === 'processing') logsEndRef.current?.scrollIntoView({ behavior: "smooth" }); 
  }, [logs, status]);

  // FETCH TRENDS FUNCTION
  const fetchTrends = async () => {
    setLoadingTrends(true);
    try {
        // Default to 'Electronics' if input is empty
        const category = formData.title || "Electronics"; 
        // We use the backend endpoint we created in generate_blog.py
        // Note: You need to ensure your server.py exposes this endpoint
        // If not, we can mock it or call the function directly via a new route.
        // For now, let's assume the endpoint exists or we fallback.
        
        // HACK: Since we didn't explicitly add a /trending route in server.py yet,
        // let's quickly add it or assume it exists. 
        // If you haven't added it, check the "server.py" Update below.
        const response = await axios.get(`http://localhost:5000/api/trending/${category}`);
        
        if (response.data.success) {
            setTrendingTopics(response.data.topics);
        }
    } catch (e) {
        console.error("Trend Fetch Error", e);
        // Fallback for demo
        setTrendingTopics(["Wireless Chargers", "GaN Adapters", "Mechanical Keyboards", "Smart Home Hubs"]);
    } finally {
        setLoadingTrends(false);
    }
  };

  const handleToggle = (p) => {
    setSelectedPlatforms(prev => prev.includes(p) ? prev.filter(i => i !== p) : [...prev, p]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.title || selectedPlatforms.length === 0) return;
    
    setStatus('processing');
    setPreview(null); 
    setIsExpanded(false);
    setLogs(["Initializing SevenXT Automation...", "Fetching Real-Time Data..."]);

    try {
      const response = await axios.post('http://localhost:5000/publish-blog', {
        title: formData.title,
        desc: formData.desc,
        platforms: selectedPlatforms
      });
      
      if(response.data.log) setLogs(prev => [...prev, ...response.data.log]);
      
      if(response.data.status === 'success') {
         setStatus('success');
         if (response.data.preview) setPreview(response.data.preview);
      } else {
         setStatus('error');
      }
    } catch (err) {
      setLogs(prev => [...prev, "❌ Connection Error."]);
      setStatus('error');
    }
  };

  return (
    <div className="grid grid-cols-1 xl:grid-cols-12 gap-8 pb-20 font-sans">
      
      {/* LEFT COLUMN */}
      <div className="xl:col-span-7 flex flex-col gap-6">
        
        {/* Input Form */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden relative">
          <div className="p-6 border-b border-slate-100 flex items-center justify-between bg-white">
            <div className="flex items-center gap-3">
                <div className="p-2 bg-brand-50 rounded-lg text-brand-600">
                    <PenTool size={20}/>
                </div>
                <div>
                    <h3 className="text-lg font-heading font-bold text-slate-900">Content Studio</h3>
                    <p className="text-xs text-slate-500">AI-Powered Generation</p>
                </div>
            </div>
            {/* Trend Button */}
            <button 
                onClick={fetchTrends}
                className="text-xs flex items-center gap-2 bg-slate-50 hover:bg-brand-50 text-slate-600 hover:text-brand-600 px-3 py-1.5 rounded-full border border-slate-200 transition-all"
            >
                {loadingTrends ? <Loader2 size={12} className="animate-spin"/> : <Sparkles size={12}/>}
                {loadingTrends ? "Analyzing..." : "Suggest Trends"}
            </button>
          </div>

          <div className="p-6 space-y-6">
            
            {/* Trending Chips */}
            {trendingTopics.length > 0 && (
                <div className="flex flex-wrap gap-2 animate-fadeIn">
                    <span className="text-xs font-bold text-slate-400 uppercase tracking-wider mr-2 flex items-center"><TrendingUp size={12} className="mr-1"/> Trending:</span>
                    {trendingTopics.map((topic, i) => (
                        <button 
                            key={i}
                            onClick={() => setFormData({...formData, title: topic})}
                            className="text-xs bg-green-50 text-green-700 border border-green-200 px-2 py-1 rounded-md hover:bg-green-100 transition-colors"
                        >
                            {topic}
                        </button>
                    ))}
                </div>
            )}

            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">Blog Topic</label>
              <input 
                type="text" 
                value={formData.title}
                onChange={e => setFormData({...formData, title: e.target.value})}
                className="w-full p-4 bg-slate-50 border border-slate-200 rounded-lg focus:ring-2 focus:ring-brand-600 focus:border-transparent outline-none transition-all font-medium text-slate-900 placeholder:text-slate-400"
                placeholder="e.g., Electronics"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">Context</label>
              <textarea 
                rows="5"
                value={formData.desc}
                onChange={e => setFormData({...formData, desc: e.target.value})}
                className="w-full p-4 bg-slate-50 border border-slate-200 rounded-lg focus:ring-2 focus:ring-brand-600 focus:border-transparent outline-none transition-all text-slate-700 placeholder:text-slate-400"
                placeholder="Optional: Add specific details (e.g. 'Focus on durability and price')..."
              ></textarea>
            </div>
          </div>
        </div>
        
        {/* Preview Card (Same as before, keeping it concise here) */}
        {preview && (
            <div className="bg-white rounded-xl shadow-xl border border-brand-100 overflow-hidden animate-fadeIn">
                 {/* ... (Preview content logic stays the same as previous working version) ... */}
                 <div className="bg-brand-600 p-4 text-white flex justify-between items-center">
                    <h3 className="font-heading font-bold flex items-center gap-2"><CheckCircle2 size={18}/> Content Ready</h3>
                 </div>
                 <div className="w-full h-64 bg-slate-100 relative">
                    <img src={preview.image} className="w-full h-full object-cover"/>
                 </div>
                 <div className="p-6">
                    <h1 className="text-2xl font-bold mb-4">{preview.title}</h1>
                    <div className={`prose text-slate-600 ${isExpanded ? '' : 'max-h-[150px] overflow-hidden'}`}>
                        {preview.content}
                    </div>
                    <button onClick={() => setIsExpanded(!isExpanded)} className="mt-4 text-brand-600 font-bold text-sm">
                        {isExpanded ? "Show Less" : "Read Full Article"}
                    </button>
                 </div>
            </div>
        )}
      </div>

      {/* RIGHT COLUMN (Same as before) */}
      <div className="xl:col-span-5 flex flex-col gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 flex flex-col overflow-hidden h-full max-h-[600px]">
          {/* ... (Platform Selector Code) ... */}
          <div className="p-6 border-b border-slate-100 bg-slate-50/50">
            <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Globe className="text-brand-600" size={20}/> Channels
            </h3>
          </div>
          <div className="p-6 grid grid-cols-1 sm:grid-cols-2 gap-3 overflow-y-auto custom-scrollbar flex-1">
              {platformsList.map(p => (
                <div key={p} onClick={() => handleToggle(p)}
                  className={`p-3 rounded-lg border cursor-pointer flex items-center justify-between transition-all ${selectedPlatforms.includes(p) ? 'bg-brand-50 border-brand-600' : 'hover:bg-slate-50'}`}
                >
                  <span className="text-sm font-medium">{p}</span>
                  {selectedPlatforms.includes(p) && <CheckCircle2 size={16} className="text-brand-600" />}
                </div>
              ))}
          </div>
          <div className="p-6 border-t border-slate-100 bg-slate-50">
            <button 
              onClick={handleSubmit}
              disabled={status === 'processing' || !formData.title || selectedPlatforms.length === 0}
              className="w-full py-4 rounded-xl font-heading font-bold text-white bg-brand-600 hover:bg-brand-700 shadow-lg transition-all flex items-center justify-center gap-3 disabled:bg-slate-300"
            >
              {status === 'processing' ? <><Loader2 className="animate-spin"/> Automating...</> : <><Send size={18}/> Launch Campaign</>}
            </button>
          </div>
        </div>
        
        {/* Logs (Same as before) */}
        <div className="bg-dark-900 rounded-xl shadow-lg border border-dark-800 overflow-hidden flex flex-col h-[300px]">
           <div className="bg-black px-4 py-3 border-b border-dark-800">
             <span className="text-xs font-mono font-bold text-slate-400">SYSTEM LOGS</span>
           </div>
           <div className="p-4 overflow-y-auto font-mono text-xs space-y-2 flex-1 custom-scrollbar text-slate-300">
             {logs.map((log, i) => (
               <div key={i} className="border-l-2 border-slate-700 pl-2">{log}</div>
             ))}
             <div ref={logsEndRef} />
           </div>
        </div>
      </div>
    </div>
  );
};
export default BlogPosting;