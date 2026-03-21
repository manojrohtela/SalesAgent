import { motion } from "motion/react";
import { Upload } from "lucide-react";
import { useRef } from "react";

interface UploadSectionProps {
  delay?: number;
  onFileSelect?: (file: File) => void;
}

export function UploadSection({ delay = 0.2, onFileSelect }: UploadSectionProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && onFileSelect) {
      onFileSelect(file);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file && onFileSelect) {
      onFileSelect(file);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay }}
    >
      <div 
        className="bg-[#1e293b] rounded-2xl p-12 border-2 border-dashed border-gray-600 hover:border-indigo-500 transition-all duration-300 cursor-pointer group"
        onClick={handleClick}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
      >
        <div className="flex flex-col items-center justify-center text-center">
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileChange} 
            accept=".csv"
            className="hidden" 
          />
          <div className="w-20 h-20 bg-indigo-500/10 rounded-full flex items-center justify-center mb-6 group-hover:bg-indigo-500/20 transition-all duration-300">
            <Upload className="w-10 h-10 text-indigo-400" />
          </div>
          <h3 className="text-2xl font-semibold mb-2">Upload CSV</h3>
          <p className="text-gray-400 mb-6">
            Drag and drop your file here, or click to browse
          </p>
          <button className="px-8 py-3 bg-indigo-600 hover:bg-indigo-700 rounded-lg font-medium transition-all duration-300 hover:scale-105 shadow-lg shadow-indigo-500/30">
            Choose File
          </button>
          <p className="text-sm text-gray-500 mt-4">
            Works with any CSV dataset
          </p>
        </div>
      </div>
    </motion.div>
  );
}
