import React, { useState, useRef, useEffect } from 'react';
import { Send, CheckCircle2, Globe, Loader2, ShoppingBag, ArrowRight } from 'lucide-react';
import api from '../services/api';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const platformsList = ["WordPress", "Reddit", "Dev.to", 'Pinterest', 'Medium', 'Facebook Page'];

const BlogPosting = () => {
  const [amazonUrl, setAmazonUrl] = useState('');
  const [productData, setProductData] = useState(null);
  const [loadingProduct, setLoadingProduct] = useState(false);
  
  const [selectedPlatforms, setSelectedPlatforms] = useState([]);
  const [status, setStatus] = useState('idle'); 
  const [logs, setLogs] = useState([]);
  const [preview, setPreview] = useState(null);
  const [isExpanded, setIsExpanded] = useState(false); 
  const logsEndRef = useRef(null);

  useEffect(() => { logsEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [logs]);

  const handleToggle = (p) => setSelectedPlatforms(prev => prev.includes(p) ? prev.filter(i => i !== p) : [...prev, p]);

  // Fetch Amazon Data
  const fetchProduct = async () => {
    if(!amazonUrl) return;
    setLoadingProduct(true);
    setProductData(null);
    try {
        const res = await api.post('/api/amazon-details', { url: amazonUrl });
        if(res.data.error) {
            alert(res.data.error);
        } else {
            setProductData(res.data);
        }
    } catch (e) {
        alert("Failed to fetch product. Check backend.");
    } finally {
        setLoadingProduct(false);
    }
  };

  const handleSubmit = async () => {
    if (!productData || selectedPlatforms.length === 0) return;
    setStatus('processing');
    setPreview(null);
    setLogs(["🚀 Starting Amazon Product Automation..."]);

    try {
      const response = await api.post('/publish-blog', {
        title: productData.title, 
        desc: productData.description, 
        product_image: productData.image_url, 
        product_link: amazonUrl, 
        brand: productData.brand, 
        platforms: selectedPlatforms
      });
      
      if(response.data.log) setLogs(prev => [...prev, ...response.data.log]);
      if(response.data.status === 'success') {
         setStatus('success');
         setPreview(response.data.preview);
      } else {
         setStatus('error');
      }
    } catch (err) {
      setLogs(prev => [...prev, "❌ Error connecting to server."]);
      setStatus('error');
    }
  };

  return (
    <div className="grid grid-cols-1 xl:grid-cols-12 gap-8 pb-20 p-6 max-w-7xl mx-auto">
      
      {/* LEFT: INPUTS */}
      <div className="xl:col-span-7 flex flex-col gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
          <div className="p-6 bg-slate-900 text-white flex items-center gap-3">
             <ShoppingBag className="text-brand-500" />
             <h3 className="font-bold">Amazon Product Input</h3>
          </div>

          <div className="p-6 space-y-4">
            <label className="block text-xs font-bold text-slate-500 uppercase">Paste Amazon Product Link</label>
            <div className="flex gap-2">
                <input 
                    type="text" 
                    value={amazonUrl}
                    onChange={(e) => setAmazonUrl(e.target.value)}
                    placeholder="https://www.amazon.in/dp/B0..."
                    className="flex-1 p-3 border border-slate-200 rounded-lg outline-none focus:border-brand-500"
                />
                <button onClick={fetchProduct} disabled={loadingProduct} className="bg-slate-800 text-white px-4 rounded-lg font-bold hover:bg-slate-700">
                    {loadingProduct ? <Loader2 className="animate-spin"/> : <ArrowRight />}
                </button>
            </div>

            {/* PRODUCT PREVIEW CARD */}
            {productData && (
                <div className="mt-4 p-4 border border-green-200 bg-green-50 rounded-xl flex gap-4 items-start animate-in fade-in slide-in-from-top-2">
                    <img src={productData.image_url} className="w-20 h-20 object-contain bg-white rounded-md border border-slate-200"/>
                    <div>
                        <h4 className="font-bold text-slate-800 text-sm line-clamp-2">{productData.title}</h4>
                        <p className="text-xs text-slate-500 mt-1 font-mono">ASIN: {productData.asin}</p>
                        <p className="text-xs text-brand-600 font-bold mt-1">Brand: {productData.brand}</p>
                        <div className="mt-2 flex gap-2">
                            <span className="text-[10px] bg-white border px-2 py-1 rounded text-slate-600">Image Loaded ✅</span>
                            <span className="text-[10px] bg-white border px-2 py-1 rounded text-slate-600">Details Loaded ✅</span>
                        </div>
                    </div>
                </div>
            )}
          </div>
        </div>

        {/* PREVIEW CARD */}
        {preview && (
            <div className="bg-white rounded-xl shadow-xl border border-brand-100 overflow-hidden">
                  <div className="bg-brand-600 p-4 text-white flex justify-between items-center">
                    <h3 className="font-bold flex items-center gap-2"><CheckCircle2 size={18}/> Published</h3>
                    {preview.link && preview.link !== "#" && (
                        <a href={preview.link} target="_blank" rel="noreferrer" className="text-xs bg-white/20 px-3 py-1 rounded-full hover:bg-white/30 flex items-center gap-1 font-bold">
                            View Live Post <ArrowRight size={12}/>
                        </a>
                    )}
                  </div>
                  <div className="w-full h-64 bg-slate-100 relative group overflow-hidden">
                    <img src={preview.image} className="w-full h-full object-cover transition-transform group-hover:scale-105"/>
                  </div>
                  <div className="p-6">
                    <h1 className="text-2xl font-bold mb-4 text-slate-800">{preview.title}</h1>
                    
                    {/* --- FIXED FORMATTING FOR MARKDOWN --- */}
                    <div className={`prose prose-lg prose-slate max-w-none text-slate-600 ${isExpanded ? '' : 'max-h-[300px] overflow-hidden relative'}`}>
                        <ReactMarkdown 
                            remarkPlugins={[remarkGfm]}
                            components={{
                                // Spacing for paragraphs
                                p: ({node, ...props}) => <p className="mb-6 leading-relaxed" {...props} />,
                                // Headings
                                h1: ({node, ...props}) => <h1 className="text-3xl font-bold mt-8 mb-4 text-slate-900" {...props} />,
                                h2: ({node, ...props}) => <h2 className="text-2xl font-bold mt-8 mb-4 text-slate-800 border-b pb-2" {...props} />,
                                h3: ({node, ...props}) => <h3 className="text-xl font-semibold mt-6 mb-3 text-slate-800" {...props} />,
                                // Lists
                                ul: ({node, ...props}) => <ul className="list-disc pl-6 mb-6 space-y-2" {...props} />,
                                ol: ({node, ...props}) => <ol className="list-decimal pl-6 mb-6 space-y-2" {...props} />,
                                li: ({node, ...props}) => <li className="pl-1" {...props} />,
                            }}
                        >
                            {preview.content}
                        </ReactMarkdown>
                        {!isExpanded && <div className="absolute bottom-0 left-0 w-full h-24 bg-gradient-to-t from-white to-transparent"></div>}
                    </div>
                    
                    <button onClick={() => setIsExpanded(!isExpanded)} className="mt-4 text-brand-600 font-bold text-sm w-full text-center uppercase hover:underline">
                        {isExpanded ? "Collapse" : "Read Full Article"}
                    </button>
                  </div>
            </div>
        )}

        {/* LOGS */}
        <div className="bg-slate-900 rounded-xl shadow-lg border border-slate-800 p-4 h-[250px] overflow-y-auto font-mono text-xs text-slate-300">
            {logs.map((l,i) => <div key={i} className="mb-1 border-l-2 border-brand-500 pl-2">{l}</div>)}
            <div ref={logsEndRef}/>
        </div>
      </div>

      {/* RIGHT: PLATFORMS */}
      <div className="xl:col-span-5 flex flex-col gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <h3 className="font-bold mb-4">Distribute To</h3>
            <div className="space-y-2">
                {platformsList.map(p => (
                    <div key={p} onClick={() => handleToggle(p)} className={`p-3 rounded-lg border cursor-pointer flex justify-between items-center transition-all ${selectedPlatforms.includes(p) ? 'bg-brand-50 border-brand-500 shadow-sm' : 'hover:bg-slate-50'}`}>
                        <span className="text-sm font-bold text-slate-700">{p}</span>
                        {selectedPlatforms.includes(p) && <CheckCircle2 size={16} className="text-brand-600"/>}
                    </div>
                ))}
            </div>
            <button onClick={handleSubmit} disabled={!productData || status === 'processing'} className="w-full mt-6 py-4 bg-brand-600 hover:bg-brand-700 text-white font-bold rounded-xl shadow-lg disabled:bg-slate-300 transition-all flex justify-center items-center gap-2">
                {status === 'processing' ? <Loader2 className="animate-spin"/> : <Send size={18}/>}
                {status === 'processing' ? "Automating..." : "Launch Campaign"}
            </button>
        </div>
      </div>

    </div>
  );
};
export default BlogPosting; 