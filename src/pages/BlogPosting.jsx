import React, { useState, useRef, useEffect } from 'react';
import { Send, CheckCircle2, Globe, Terminal, Loader2, PenTool, AlertTriangle, FileText, Image as ImageIcon, ChevronDown, ChevronUp, Layout } from 'lucide-react';
import axios from 'axios';

const platformsList = [
  "WordPress", "Ghost", "Medium", "LinkedIn", "Reddit", "Quora", 
  "Facebook Page", "Twitter", "Discord", "Telegram", "Pinterest", "Substack"
];

const BlogPosting = () => {
  const [formData, setFormData] = useState({ title: '', desc: '' });
  const [selectedPlatforms, setSelectedPlatforms] = useState([]);
  const [status, setStatus] = useState('idle'); 
  const [logs, setLogs] = useState([]);
  const [preview, setPreview] = useState(null);
  const [isExpanded, setIsExpanded] = useState(false);
  const logsEndRef = useRef(null);

  // FIX: Only scroll if we are actively processing, preventing jump on load
  useEffect(() => { 
    if (status === 'processing') {
        logsEndRef.current?.scrollIntoView({ behavior: "smooth" }); 
    }
  }, [logs, status]);

  const handleToggle = (p) => {
    setSelectedPlatforms(prev => prev.includes(p) ? prev.filter(i => i !== p) : [...prev, p]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.title || selectedPlatforms.length === 0) return;
    
    setStatus('processing');
    setPreview(null); 
    setIsExpanded(false);
    setLogs(["Initializing System...", "Connecting to AI Agent..."]);

    try {
      const response = await axios.post('http://localhost:5000/publish-blog', {
        title: formData.title,
        desc: formData.desc,
        platforms: selectedPlatforms
      });
      
      if(response.data.log) setLogs(prev => [...prev, ...response.data.log]);
      
      if(response.data.status === 'success') {
         setStatus('success');
         if (response.data.preview) {
            setPreview(response.data.preview);
         }
      } else {
         setStatus('error');
      }

    } catch (err) {
      setLogs(prev => [...prev, "❌ Network Error: Ensure backend is running on port 5000."]);
      setStatus('error');
    }
  };

  return (
    <div className="grid grid-cols-1 xl:grid-cols-12 gap-8 pb-20 font-sans">
      
      {/* LEFT COLUMN */}
      <div className="xl:col-span-7 flex flex-col gap-6">
        
        {/* Input Form */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
          <div className="p-6 border-b border-slate-100 flex items-center gap-3 bg-white">
            <div className="p-2 bg-brand-50 rounded-lg text-brand-600">
                <PenTool size={20}/>
            </div>
            <div>
                <h3 className="text-lg font-heading font-bold text-slate-900">Content Studio</h3>
                <p className="text-xs text-slate-500">AI-Powered Generation</p>
            </div>
          </div>
          <div className="p-6 space-y-6">
            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">Blog Topic</label>
              <input 
                type="text" 
                value={formData.title}
                onChange={e => setFormData({...formData, title: e.target.value})}
                className="w-full p-4 bg-slate-50 border border-slate-200 rounded-lg focus:ring-2 focus:ring-brand-600 focus:border-transparent outline-none transition-all font-medium text-slate-900 placeholder:text-slate-400"
                placeholder="e.g., The Future of 8K Televisions"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">Context & Keywords</label>
              <textarea 
                rows="5"
                value={formData.desc}
                onChange={e => setFormData({...formData, desc: e.target.value})}
                className="w-full p-4 bg-slate-50 border border-slate-200 rounded-lg focus:ring-2 focus:ring-brand-600 focus:border-transparent outline-none transition-all text-slate-700 placeholder:text-slate-400"
                placeholder="Add specific details, tone, or mandatory keywords..."
              ></textarea>
            </div>
          </div>
        </div>

        {/* RESULT: Content Preview Card */}
        {preview && (
            <div className="bg-white rounded-xl shadow-xl border border-brand-100 overflow-hidden animate-fadeIn">
                <div className="bg-brand-600 p-4 text-white flex justify-between items-center">
                    <h3 className="font-heading font-bold flex items-center gap-2"><FileText size={18}/> Generated Content</h3>
                    <span className="text-xs font-bold bg-black/20 px-3 py-1 rounded-full border border-white/10">{preview.word_count || 0} Words</span>
                </div>
                
                {/* Image Preview */}
                <div className="w-full h-72 bg-slate-900 relative overflow-hidden group">
                    <img 
                      src={preview.image || "https://via.placeholder.com/800x400?text=No+Image"} 
                      className="w-full h-full object-cover opacity-90" 
                      alt="Generated Asset" 
                    />
                    <div className="absolute bottom-0 left-0 w-full h-20 bg-gradient-to-t from-black/80 to-transparent"></div>
                    <div className="absolute bottom-4 left-4 text-white flex items-center gap-2 text-xs font-medium px-3 py-1.5 bg-white/10 backdrop-blur-md rounded-full border border-white/20">
                        <ImageIcon size={12}/> AI Selected Visual
                    </div>
                </div>

                <div className="p-8">
                    <h1 className="text-3xl font-heading font-bold text-slate-900 mb-6 leading-tight">{preview.title}</h1>
                    <div className={`prose prose-slate max-w-none text-slate-600 leading-relaxed ${isExpanded ? '' : 'max-h-[200px] overflow-hidden relative'}`}>
                        {preview.content}
                        {!isExpanded && <div className="absolute bottom-0 left-0 w-full h-32 bg-gradient-to-t from-white to-transparent"></div>}
                    </div>
                    <div className="mt-8 pt-6 border-t border-slate-100 text-center">
                        <button onClick={() => setIsExpanded(!isExpanded)} className="inline-flex items-center gap-2 text-brand-600 font-bold text-sm hover:text-brand-700 hover:bg-brand-50 px-6 py-2 rounded-full transition-colors">
                          {isExpanded ? <><ChevronUp size={16}/> Show Less</> : <><ChevronDown size={16}/> Read Full Article</>}
                        </button>
                    </div>
                </div>
            </div>
        )}
      </div>

      {/* RIGHT COLUMN */}
      <div className="xl:col-span-5 flex flex-col gap-6">
        
        {/* Platform Selector */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 flex flex-col overflow-hidden h-full max-h-[600px]">
          <div className="p-6 border-b border-slate-100 flex items-center gap-3 bg-white">
            <div className="p-2 bg-brand-50 rounded-lg text-brand-600">
                <Globe size={20}/>
            </div>
            <div>
                <h3 className="text-lg font-heading font-bold text-slate-900">Distribution</h3>
                <p className="text-xs text-slate-500">Select Channels</p>
            </div>
          </div>
          <div className="p-6 grid grid-cols-1 sm:grid-cols-2 gap-3 overflow-y-auto custom-scrollbar flex-1">
              {platformsList.map(p => (
                <div key={p} onClick={() => handleToggle(p)}
                  className={`p-3 rounded-lg border cursor-pointer flex items-center justify-between transition-all duration-200 select-none group
                    ${selectedPlatforms.includes(p) 
                        ? 'bg-brand-50 border-brand-600 shadow-sm' 
                        : 'border-slate-200 hover:border-brand-300 hover:bg-slate-50'}`}
                >
                  <span className={`text-sm font-medium ${selectedPlatforms.includes(p) ? 'text-brand-700 font-bold' : 'text-slate-600'}`}>{p}</span>
                  <div className={`w-5 h-5 rounded-full flex items-center justify-center transition-all ${selectedPlatforms.includes(p) ? 'bg-brand-600 text-white' : 'bg-slate-100 text-slate-300 group-hover:bg-slate-200'}`}>
                    {selectedPlatforms.includes(p) && <CheckCircle2 size={12} />}
                  </div>
                </div>
              ))}
          </div>
          <div className="p-6 border-t border-slate-100 bg-slate-50">
            <button 
              onClick={handleSubmit}
              disabled={status === 'processing' || !formData.title || selectedPlatforms.length === 0}
              className={`w-full py-4 rounded-xl font-heading font-bold text-white shadow-lg shadow-brand-900/10 transition-all flex items-center justify-center gap-3
                ${status === 'processing' ? 'bg-slate-800 cursor-not-allowed' : 'bg-brand-600 hover:bg-brand-700 hover:shadow-brand-600/20 hover:-translate-y-0.5'}`}
            >
              {status === 'processing' ? <><Loader2 className="animate-spin"/> Automating...</> : <><Send size={18}/> Launch Campaign</>}
            </button>
          </div>
        </div>

        {/* Terminal Log */}
        <div className="bg-dark-900 rounded-xl shadow-lg border border-dark-800 overflow-hidden flex flex-col h-[300px]">
           <div className="bg-black px-4 py-3 flex items-center justify-between border-b border-dark-800">
             <div className="flex items-center gap-2">
               <Terminal size={14} className="text-brand-500" />
               <span className="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider">System Operations</span>
             </div>
             <div className="flex gap-1.5">
                <div className="w-2 h-2 rounded-full bg-dark-700"></div>
                <div className="w-2 h-2 rounded-full bg-dark-700"></div>
             </div>
           </div>
           <div className="p-4 overflow-y-auto font-mono text-xs space-y-2 flex-1 custom-scrollbar text-slate-300">
             {logs.length === 0 && <span className="text-slate-600 italic">// Waiting for input...</span>}
             {logs.map((log, i) => (
               <div key={i} className={`pl-3 border-l-2 py-0.5 ${log.includes('Error') || log.includes('Failed') ? 'border-red-500 text-red-400 bg-red-500/5' : log.includes('Success') ? 'border-brand-500 text-brand-400 bg-brand-500/5' : 'border-slate-700'}`}>
                 {log}
               </div>
             ))}
             <div ref={logsEndRef} />
           </div>
        </div>

      </div>
    </div>
  );
};
export default BlogPosting;