import React, { useState } from 'react';
import { Link, Copy, RefreshCw, Loader2, ExternalLink, Zap } from 'lucide-react';
import api from '../services/api';

const KeywordGen = () => {
  const [asin, setAsin] = useState('');
  const [mainProduct, setMainProduct] = useState('');
  const [generatedLinks, setGeneratedLinks] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleAiGenerate = async () => {
    if (!asin || !mainProduct) return;
    setLoading(true);
    setGeneratedLinks([]);

    try {
        const response = await api.post('/generate-seo-links', {
            product: mainProduct,
            asin: asin
        });

        if (response.data.success) {
            setGeneratedLinks(response.data.data);
        }
    } catch (error) {
        console.error(error);
        alert("Failed to generate keywords. Check backend.");
    } finally {
        setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    // You can add a toast notification here
  };

  return (
    <div className="max-w-6xl mx-auto py-8 px-6">
      <div className="bg-white rounded-2xl shadow-xl border border-slate-200 overflow-hidden">
        
        {/* Header */}
        <div className="bg-slate-900 text-white p-8">
            <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-brand-600 rounded-lg">
                    <Zap size={24} className="text-white" />
                </div>
                <h2 className="text-2xl font-bold">AI SEO Link Generator</h2>
            </div>
            <p className="text-slate-400">
                Generates highly optimized Amazon URLs based on SevenXT Strategy (Use Case, Features, Competitors).
            </p>
        </div>

        <div className="p-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
            
            {/* LEFT: INPUTS */}
            <div className="lg:col-span-4 space-y-6">
                <div className="bg-slate-50 p-6 rounded-xl border border-slate-200">
                    <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Product ASIN</label>
                    <input 
                        type="text" 
                        value={asin}
                        onChange={e => setAsin(e.target.value.toUpperCase())}
                        placeholder="e.g. B0FQP89TTD"
                        className="w-full p-3 border border-slate-300 rounded-lg focus:border-brand-500 outline-none font-mono font-bold text-slate-700"
                    />
                </div>

                <div className="bg-slate-50 p-6 rounded-xl border border-slate-200">
                    <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Main Product Name</label>
                    <textarea 
                        value={mainProduct}
                        onChange={e => setMainProduct(e.target.value)}
                        placeholder="e.g. Mini UPS for WiFi Router"
                        className="w-full p-3 border border-slate-300 rounded-lg focus:border-brand-500 outline-none h-32 resize-none text-slate-700"
                    />
                    <p className="text-[10px] text-slate-400 mt-2">
                        Tip: Be specific. Instead of "UPS", use "Mini UPS for 12v Router".
                    </p>
                </div>

                <button 
                    onClick={handleAiGenerate}
                    disabled={loading || !asin || !mainProduct}
                    className="w-full py-4 bg-brand-600 hover:bg-brand-700 text-white font-bold rounded-xl shadow-lg transition-all flex justify-center items-center gap-2 disabled:bg-slate-300 disabled:cursor-not-allowed"
                >
                    {loading ? <Loader2 className="animate-spin"/> : <RefreshCw size={18}/>}
                    {loading ? "Analyzing Market..." : "Generate SEO Links"}
                </button>
            </div>

            {/* RIGHT: OUTPUTS */}
            <div className="lg:col-span-8">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="font-bold text-slate-700 flex items-center gap-2">
                        <Link size={18} className="text-brand-600"/> Generated Campaigns
                    </h3>
                    {generatedLinks.length > 0 && (
                        <span className="bg-green-100 text-green-700 text-xs font-bold px-2 py-1 rounded-full">
                            {generatedLinks.length} Links Ready
                        </span>
                    )}
                </div>
                
                <div className="bg-slate-50 rounded-xl p-6 border border-slate-200 min-h-[400px] max-h-[600px] overflow-y-auto custom-scrollbar">
                    {generatedLinks.length === 0 ? (
                        <div className="h-full flex flex-col items-center justify-center text-slate-400">
                            <Zap size={48} className="mb-4 opacity-20"/>
                            <p>Enter Product Details to Start</p>
                        </div>
                    ) : (
                        <div className="space-y-3">
                          {generatedLinks.map((item, idx) => (
                              <div key={idx} className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm hover:border-brand-300 transition-all group">
                                  <div className="flex justify-between items-start mb-1">
                                      {/* DISPLAY STRATEGY NAME */}
                                      <span className="text-[10px] font-bold text-white bg-slate-800 px-2 py-1 rounded uppercase tracking-wider mb-2 block">
                                          {item.strategy}
                                      </span>
                                      
                                      <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                          <button onClick={() => copyToClipboard(item.url)} className="p-1 hover:bg-slate-100 rounded text-slate-500 hover:text-brand-600">
                                              <Copy size={16}/>
                                          </button>
                                          <a href={item.url} target="_blank" rel="noreferrer" className="p-1 hover:bg-slate-100 rounded text-slate-500 hover:text-brand-600">
                                              <ExternalLink size={16}/>
                                          </a>
                                      </div>
                                  </div>
                                  
                                  <p className="text-brand-700 font-bold text-sm mb-1">{item.keyword}</p>
                                  <p className="text-[10px] text-slate-400 font-mono break-all line-clamp-1">{item.url}</p>
                              </div>
                          ))}
                        </div>
                    )}
                </div>
            </div>

        </div>
      </div>
    </div>
  );
};

export default KeywordGen;