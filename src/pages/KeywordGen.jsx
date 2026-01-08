import React, { useState } from 'react';
import { Link, Copy, RefreshCw, Loader2, ExternalLink, Zap, TrendingUp, BrainCircuit, FileDown, ArrowDownCircle } from 'lucide-react';
import api from '../services/api';

const KeywordGen = () => {
  const [asin, setAsin] = useState('');
  const [mainProduct, setMainProduct] = useState('');
  const [productSpecs, setProductSpecs] = useState('');
  const [generatedLinks, setGeneratedLinks] = useState([]);
  const [downloadUrl, setDownloadUrl] = useState(null); // ✅ NEW: Store the URL here
  
  const [loading, setLoading] = useState(false);         // For Keyword Generation
  const [fetchLoading, setFetchLoading] = useState(false); // For Auto-Fill

  // --- AUTO-FETCH FUNCTION ---
  const handleFetchDetails = async () => {
    if (!asin) {
        alert("Please enter an ASIN first.");
        return;
    }
    setFetchLoading(true);
    try {
        const response = await api.post('/api/amazon-details', {
            url: `https://www.amazon.in/dp/${asin}`
        });

        if (response.data.error) {
            alert("Error fetching data: " + response.data.error);
        } else {
            setMainProduct(response.data.title);
            setProductSpecs(response.data.description);
        }
    } catch (error) {
        console.error(error);
        alert("Failed to connect to backend.");
    } finally {
        setFetchLoading(false);
    }
  };

  const handleAiGenerate = async () => {
    if (!asin || !mainProduct || !productSpecs) return;
    setLoading(true);
    setGeneratedLinks([]);
    setDownloadUrl(null); // Reset previous download

    try {
        const response = await api.post('/generate-seo-links', {
            product: mainProduct,
            asin: asin,
            specs: productSpecs
        });

        if (response.data.success) {
            setGeneratedLinks(response.data.data);
            
            // ✅ UPDATED: Save the URL state instead of auto-clicking
            if (response.data.download_url) {
                setDownloadUrl(response.data.download_url);
            }
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
                Generates 12 highly optimized Amazon URLs using <strong>Real-Time Market Data</strong> & <strong>Product Specs Verification</strong>.
            </p>
        </div>

        <div className="p-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
            
            {/* LEFT: INPUTS */}
            <div className="lg:col-span-4 space-y-6">
                
                {/* 1. ASIN INPUT + FETCH BUTTON */}
                <div className="bg-slate-50 p-6 rounded-xl border border-slate-200">
                    <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Product ASIN</label>
                    <div className="flex gap-2">
                        <input 
                            type="text" 
                            value={asin}
                            onChange={e => setAsin(e.target.value.toUpperCase())}
                            placeholder="e.g. B0FQP89TTD"
                            className="w-full p-3 border border-slate-300 rounded-lg focus:border-brand-500 outline-none font-mono font-bold text-slate-700"
                        />
                        <button 
                            onClick={handleFetchDetails}
                            disabled={fetchLoading || !asin}
                            className="bg-slate-800 text-white px-3 rounded-lg hover:bg-slate-700 disabled:bg-slate-300 transition-colors"
                            title="Auto-Fill Details from Amazon"
                        >
                            {fetchLoading ? <Loader2 className="animate-spin" size={20}/> : <ArrowDownCircle size={20}/>}
                        </button>
                    </div>
                    <p className="text-[10px] text-slate-400 mt-2">
                        Click the arrow to auto-fetch Title & Specs.
                    </p>
                </div>

                {/* 2. TITLE INPUT */}
                <div className="bg-slate-50 p-6 rounded-xl border border-slate-200">
                    <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Main Product Name</label>
                    <textarea 
                        value={mainProduct}
                        onChange={e => setMainProduct(e.target.value)}
                        placeholder="e.g. Mini UPS for WiFi Router"
                        className="w-full p-3 border border-slate-300 rounded-lg focus:border-brand-500 outline-none h-24 resize-none text-slate-700 text-sm"
                    />
                </div>

                {/* 3. SPECS INPUT (Auto-Filled) */}
                <div className="bg-slate-50 p-6 rounded-xl border border-slate-200">
                    <label className="block text-xs font-bold text-slate-500 uppercase mb-2">About This Item (Specs)</label>
                    <textarea 
                        value={productSpecs}
                        onChange={e => setProductSpecs(e.target.value)}
                        placeholder="Specs will appear here..."
                        className="w-full p-3 border border-slate-300 rounded-lg focus:border-brand-500 outline-none h-32 resize-none text-slate-700 text-sm"
                    />
                    <p className="text-[10px] text-slate-400 mt-2">
                        AI uses this to reject misleading keywords (e.g. "Voice" if not supported).
                    </p>
                </div>

                <button 
                    onClick={handleAiGenerate}
                    disabled={loading || !asin || !mainProduct || !productSpecs}
                    className="w-full py-4 bg-brand-600 hover:bg-brand-700 text-white font-bold rounded-xl shadow-lg transition-all flex justify-center items-center gap-2 disabled:bg-slate-300 disabled:cursor-not-allowed"
                >
                    {loading ? <Loader2 className="animate-spin"/> : <RefreshCw size={18}/>}
                    {loading ? "Verifying & Generating..." : "Generate SEO Links"}
                </button>
            </div>

            {/* RIGHT: OUTPUTS */}
            <div className="lg:col-span-8">
                
                {/* ✅ NEW: DOWNLOAD BANNER (Appears when file is ready) */}
                {downloadUrl && (
                    <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-xl flex justify-between items-center shadow-sm animate-pulse">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-green-100 rounded-lg">
                                <FileDown size={24} className="text-green-700" />
                            </div>
                            <div>
                                <h4 className="text-sm font-bold text-green-800">Excel Report Ready</h4>
                                <p className="text-xs text-green-600">Click to download your campaign file.</p>
                            </div>
                        </div>
                        
                        <a 
                            href={downloadUrl}
                            download="Amazon_SEO_Report.xlsx"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-bold rounded-lg shadow transition-colors flex items-center gap-2"
                        >
                            Download <FileDown size={16} />
                        </a>
                    </div>
                )}

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
                                    <div className="flex justify-between items-start mb-2">
                                        <div className="flex flex-wrap gap-2 items-center">
                                            <span className="text-[10px] font-bold text-white bg-slate-800 px-2 py-1 rounded uppercase tracking-wider">
                                                {item.strategy}
                                            </span>
                                            {item.source.includes("Market") ? (
                                                <span className="text-[10px] font-bold text-green-700 bg-green-50 px-2 py-1 rounded border border-green-200 flex items-center gap-1">
                                                    <TrendingUp size={12}/> {item.source}
                                                </span>
                                            ) : (
                                                <span className="text-[10px] font-bold text-blue-700 bg-blue-50 px-2 py-1 rounded border border-blue-200 flex items-center gap-1">
                                                    <BrainCircuit size={12}/> {item.source}
                                                </span>
                                            )}
                                        </div>
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