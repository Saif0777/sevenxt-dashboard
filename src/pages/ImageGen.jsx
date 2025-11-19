import React from 'react';
import { Image as ImageIcon, Construction } from 'lucide-react';

const ImageGen = () => {
  return (
    <div className="flex flex-col items-center justify-center h-[60vh] text-center">
      <div className="w-24 h-24 bg-slate-100 rounded-full flex items-center justify-center mb-6 animate-pulse">
        <ImageIcon size={48} className="text-slate-400" />
      </div>
      <h2 className="text-3xl font-bold text-slate-800 mb-2">Image Automation</h2>
      <p className="text-slate-500 max-w-md">
        This module is currently under development. It will allow for bulk image resizing, background removal, and Amazon compliance checks.
      </p>
      <div className="mt-8 px-4 py-2 bg-brand-50 text-brand-700 rounded-full text-sm font-medium border border-brand-200 flex items-center gap-2">
        <Construction size={16} /> Coming Soon
      </div>
    </div>
  );
};
export default ImageGen;