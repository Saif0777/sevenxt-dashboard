import React, { useState } from 'react';
import { UploadCloud, FileSpreadsheet, Search, Download, Loader2, AlertCircle, CheckCircle2, Zap } from 'lucide-react';
import axios from 'axios';

const KeywordGen = () => {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('idle'); 
  const [errorMessage, setErrorMessage] = useState('');

  const handleGenerate = async () => {
    if (!file) return;
    setStatus('processing');
    setErrorMessage('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:5000/generate-keywords', formData, {
        responseType: 'blob', 
        timeout: 300000, 
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const timestamp = new Date().toISOString().split('T')[0];
      link.setAttribute('download', `SevenXT_Keywords_${timestamp}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      
      setStatus('success');
    } catch (error) {
      setStatus('error');
      setErrorMessage("Failed to process file. Ensure backend is running.");
    }
  };

  return (
    <div className="max-w-4xl mx-auto h-full flex flex-col justify-center py-10">
      <div className="bg-white rounded-2xl shadow-2xl shadow-slate-200/50 border border-slate-200 overflow-hidden">
        
        {/* Header - Dark for Contrast */}
        <div className="bg-dark-900 text-white p-10 relative overflow-hidden">
          <div className="relative z-10">
            <div className="w-12 h-12 bg-brand-600 rounded-lg flex items-center justify-center mb-4 shadow-lg shadow-brand-600/50">
                <Search className="text-white" size={24} />
            </div>
            <h3 className="text-3xl font-heading font-bold tracking-tight">Keyword Intelligence</h3>
            <p className="text-slate-400 mt-2 text-sm max-w-lg font-medium">
              Upload your seed keyword list. Our agents will scrape Amazon's autocomplete for high-volume long-tail terms.
            </p>
          </div>
          {/* Decorative */}
          <div className="absolute -top-20 -right-20 w-96 h-96 bg-brand-600/10 rounded-full blur-3xl"></div>
        </div>

        <div className="p-10 bg-slate-50/50">
           {/* Upload Zone */}
           <div className={`relative border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 group
             ${file ? 'border-brand-600 bg-brand-50/50' : 'border-slate-300 hover:border-brand-400 hover:bg-white'}`}>
             
             <input type="file" accept=".xlsx" onChange={(e) => setFile(e.target.files[0])} className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-20" />
             
             <div className="flex flex-col items-center gap-5 relative z-10">
               <div className={`w-20 h-20 rounded-2xl flex items-center justify-center transition-all shadow-sm
                 ${file ? 'bg-brand-600 text-white scale-110 shadow-brand-600/30' : 'bg-white border border-slate-200 text-slate-400 group-hover:scale-110 group-hover:border-brand-200 group-hover:text-brand-500'}`}>
                 {file ? <FileSpreadsheet size={36} /> : <UploadCloud size={36} />}
               </div>
               <div>
                 <h4 className="text-xl font-heading font-bold text-slate-900">
                    {file ? file.name : "Drop Seed Excel File"}
                 </h4>
                 <p className="text-slate-500 mt-1 text-sm font-medium">
                    {file ? "Ready for Analysis" : "Supports .xlsx format"}
                 </p>
               </div>
             </div>
           </div>

           {status === 'error' && (
             <div className="mt-6 p-4 bg-red-50 border border-red-100 text-red-700 rounded-xl flex items-center gap-3 text-sm font-medium animate-fadeIn">
                <AlertCircle size={18}/> {errorMessage}
             </div>
           )}

           <button 
             onClick={handleGenerate}
             disabled={!file || status === 'processing'}
             className={`w-full mt-8 py-5 rounded-xl font-heading font-bold text-lg text-white shadow-xl transition-all flex items-center justify-center gap-3
               ${status === 'processing' ? 'bg-dark-800 cursor-wait' : status === 'success' ? 'bg-green-600 hover:bg-green-700' : 'bg-brand-600 hover:bg-brand-700 hover:shadow-brand-600/30 hover:-translate-y-1'}`}
           >
             {status === 'processing' ? <><Loader2 className="animate-spin" /> Analysis In Progress...</> : status === 'success' ? <><Download /> Download Report</> : <><Zap size={20}/> Generate Keywords</>}
           </button>
        </div>
      </div>
    </div>
  );
};
export default KeywordGen;