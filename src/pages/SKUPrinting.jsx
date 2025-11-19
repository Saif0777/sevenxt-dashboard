import React, { useState, useRef, useEffect } from 'react';
import { UploadCloud, FileSpreadsheet, Printer, Terminal, Box, Loader2, FileCode, Check, Layers } from 'lucide-react';
import axios from 'axios';

const SKUPrinting = () => {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('idle'); 
  const [logs, setLogs] = useState([]);
  const [printedImages, setPrintedImages] = useState([]);
  const logsEndRef = useRef(null);

  useEffect(() => { logsEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [logs]);

  const handlePrint = async () => {
    if (!file) return;
    setStatus('processing');
    setLogs(["Initializing connection to SevenXT Print Server...", "Uploading manifest..."]);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:5000/print-sku', formData);
      const { log, printed_images } = response.data;
      setLogs(log);
      setPrintedImages(printed_images);
      setStatus('success');
    } catch (error) {
      setLogs(prev => [...prev, "❌ CONNECTION ERROR: Ensure Backend is running."]);
      setStatus('error');
    }
  };

  return (
    <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 h-[calc(100vh-140px)] min-h-[600px]">
      
      {/* Left: Controls (4 Cols) */}
      <div className="xl:col-span-4 flex flex-col gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <div className="flex items-center gap-3 mb-6 border-b border-slate-100 pb-4">
                <div className="bg-brand-50 p-2 rounded-lg text-brand-600">
                    <Printer size={20}/>
                </div>
                <div>
                    <h3 className="text-base font-heading font-bold text-slate-900">SKU Operations</h3>
                    <p className="text-[10px] text-slate-500 uppercase tracking-wider">Queue Manager</p>
                </div>
            </div>
            
            <div className={`relative border-2 border-dashed rounded-xl p-6 text-center transition-all group
              ${file ? 'border-brand-600 bg-brand-50/30' : 'border-slate-300 hover:border-brand-400'}`}>
                <input type="file" accept=".xlsx, .csv" onChange={(e) => setFile(e.target.files[0])} className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" />
                <div className="flex flex-col items-center gap-2">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center transition-colors ${file ? 'bg-brand-600 text-white' : 'bg-slate-100 text-slate-400 group-hover:bg-slate-200'}`}>
                    {file ? <FileSpreadsheet size={20} /> : <UploadCloud size={20} />}
                  </div>
                  <p className="text-sm font-bold text-slate-700 font-heading">{file ? file.name : "Upload Manifest"}</p>
                </div>
            </div>
            <button onClick={handlePrint} disabled={!file || status === 'processing'} className="w-full mt-6 py-3 rounded-lg bg-brand-600 text-white font-heading font-bold text-sm shadow-lg hover:bg-brand-700 disabled:bg-dark-800 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2">
              {status === 'processing' ? <><Loader2 className="animate-spin" size={16}/> Processing...</> : 'Start Print Job'}
            </button>
        </div>
        
        {/* Logs */}
        <div className="flex-1 bg-dark-900 rounded-xl shadow-lg border border-dark-800 p-4 overflow-hidden flex flex-col min-h-[200px]">
           <div className="font-mono text-[10px] text-slate-500 mb-3 uppercase font-bold flex items-center gap-2">
                <Terminal size={12}/> System Terminal
           </div>
           <div className="overflow-y-auto font-mono text-[10px] space-y-1 flex-1 custom-scrollbar text-slate-300">
             {logs.map((log, i) => (
                 <div key={i} className={`truncate ${log.includes('ERROR') || log.includes('FAILED') ? 'text-red-400' : log.includes('Found') || log.includes('Match') ? 'text-green-400' : ''}`}>
                     <span className="opacity-30 mr-2">›</span>{log}
                 </div>
             ))}
             <div ref={logsEndRef} />
           </div>
        </div>
      </div>

      {/* Right: Preview (8 Cols) */}
      <div className="xl:col-span-8 bg-white rounded-xl shadow-sm border border-slate-200 flex flex-col overflow-hidden">
        <div className="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
            <h3 className="text-base font-heading font-bold text-slate-900 flex items-center gap-2">
                <Box className="text-brand-600" size={18}/> Live Queue
            </h3>
            <span className="bg-white border border-slate-200 text-slate-600 px-3 py-1 rounded-full text-xs font-bold shadow-sm">{printedImages.length} Files Processed</span>
        </div>
        
        <div className="flex-1 p-5 overflow-y-auto custom-scrollbar bg-slate-50/30">
            {printedImages.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-slate-300 border-2 border-dashed border-slate-200 rounded-xl">
                    <Printer size={40} className="mb-3 opacity-20" />
                    <p className="text-sm font-medium">Queue is empty</p>
                </div>
            ) : (
                // UPDATED: Medium Sized Grid (3 Cols)
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 content-start">
                {printedImages.map((itemStr, idx) => {
                    // Parse the string "FILE_ICON:filename.lbl|5"
                    const parts = itemStr.split('|');
                    const rawFile = parts[0];
                    const quantity = parts[1] || '1'; // Default to 1 if missing
                    
                    const isLabel = rawFile.startsWith("FILE_ICON:");
                    const displayName = isLabel ? rawFile.replace("FILE_ICON:", "") : "SKU Image";

                    return (
                        <div key={idx} className="group relative bg-white border border-slate-200 rounded-xl p-4 flex flex-col items-center hover:border-brand-300 hover:shadow-md transition-all">
                            
                            {/* Quantity Badge */}
                            <div className="absolute top-3 right-3 z-10 flex items-center gap-1 bg-brand-50 text-brand-700 px-2 py-1 rounded-md border border-brand-100">
                                <Layers size={12} />
                                <span className="text-xs font-bold">{quantity} Copies</span>
                            </div>

                            {/* Icon */}
                            <div className="w-16 h-16 bg-slate-50 rounded-xl flex items-center justify-center mb-4 text-slate-400 group-hover:text-brand-500 group-hover:bg-brand-50 transition-colors mt-2">
                                {isLabel ? <FileCode size={32} /> : <img src={`http://localhost:5000/${itemStr}`} className="w-full h-full object-contain" />}
                            </div>
                            
                            {/* Filename */}
                            <div className="w-full text-center px-1">
                                <p className="text-sm font-bold text-slate-800 truncate w-full" title={displayName}>
                                    {displayName.split('.')[0]}
                                </p>
                                <p className="text-[10px] text-slate-400 uppercase tracking-wider mt-1">
                                    {displayName.split('.').pop()} FILE
                                </p>
                            </div>
                            
                            {/* Index Number */}
                            <div className="absolute top-3 left-3 text-[10px] text-slate-300 font-mono">#{idx + 1}</div>
                            
                            {/* Sent Status */}
                            <div className="mt-4 w-full flex items-center justify-center gap-1.5 text-[10px] font-bold text-green-600 bg-green-50 py-1.5 rounded-lg">
                                <Check size={12} strokeWidth={3}/> SENT TO PRINTER
                            </div>
                        </div>
                    );
                })}
                </div>
            )}
        </div>
      </div>
    </div>
  );
};
export default SKUPrinting;