import React, { useState } from 'react';
import { UploadCloud, FileDown, Loader2, Search } from 'lucide-react';
import api from '../services/api';

const AmazonSuggestions = () => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setDownloadUrl(null);
  };

  const handleUpload = async () => {
    if (!file) return alert("Please select an Excel file first");
    
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    // 1. Get the Token (Password) from Local Storage
    const token = localStorage.getItem('authToken');

    try {
      const response = await api.post('/api/bulk-suggestions', formData, {
        headers: { 
            'Content-Type': 'multipart/form-data',
            'X-Access-Token': token  // <--- ✅ THIS WAS MISSING
        }
      });

      if (response.data.success) {
        setDownloadUrl(response.data.download_url);
      }
    } catch (error) {
      console.error(error);
      // specific error message handling
      const msg = error.response?.data?.error || error.response?.data?.message || "Processing failed";
      
      if (error.response?.status === 401) {
          alert("⛔ Session Expired. Please Logout and Login again.");
      } else {
          alert("Error: " + msg);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-8">
      <div className="bg-white rounded-2xl shadow-xl border border-slate-200 overflow-hidden">
        
        {/* Header */}
        <div className="bg-slate-900 text-white p-8">
            <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-orange-500 rounded-lg">
                    <Search size={24} className="text-white" />
                </div>
                <h2 className="text-2xl font-bold">Bulk Amazon Auto-Complete</h2>
            </div>
            <p className="text-slate-400">
                Upload a list of products (Excel) to extract Amazon's exact search suggestions.
            </p>
        </div>

        <div className="p-8">
            {/* Upload Area */}
            <div className="border-2 border-dashed border-slate-300 rounded-xl p-10 text-center bg-slate-50 hover:bg-slate-100 transition-colors">
                <input 
                    type="file" 
                    accept=".xlsx, .xls"
                    onChange={handleFileChange}
                    className="hidden" 
                    id="suggestion-upload"
                />
                <label htmlFor="suggestion-upload" className="cursor-pointer flex flex-col items-center">
                    <UploadCloud size={48} className="text-slate-400 mb-4" />
                    <span className="text-lg font-bold text-slate-700">
                        {file ? file.name : "Click to Upload Excel File"}
                    </span>
                    <span className="text-xs text-slate-400 mt-2">
                        Supported: .xlsx (Column A should contain product names)
                    </span>
                </label>
            </div>

            {/* Actions */}
            <div className="mt-6 flex justify-end">
                <button 
                    onClick={handleUpload}
                    disabled={!file || loading}
                    className="px-6 py-3 bg-slate-900 text-white font-bold rounded-xl hover:bg-slate-800 disabled:bg-slate-300 transition-all flex items-center gap-2"
                >
                    {loading ? <Loader2 className="animate-spin" /> : <Search size={20} />}
                    {loading ? "Scraping Amazon..." : "Start Scraping"}
                </button>
            </div>

            {/* Success / Download */}
            {downloadUrl && (
                <div className="mt-8 p-4 bg-green-50 border border-green-200 rounded-xl flex justify-between items-center animate-pulse">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-green-100 rounded-lg">
                            <FileDown size={24} className="text-green-700" />
                        </div>
                        <div>
                            <h4 className="text-sm font-bold text-green-800">Scraping Complete!</h4>
                            <p className="text-xs text-green-600">Your keyword file is ready.</p>
                        </div>
                    </div>
                    
                    <a 
                        href={downloadUrl}
                        className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-bold rounded-lg shadow flex items-center gap-2"
                    >
                        Download Excel <FileDown size={16} />
                    </a>
                </div>
            )}
        </div>
      </div>
    </div>
  );
};

export default AmazonSuggestions;