import { motion } from "motion/react";
import { Database, LucideIcon } from "lucide-react";
import { IconContainer } from "./ui/IconContainer";

interface DatasetCardProps {
  name: string;
  description: string;
  rows: number;
  columns: number;
  icon: LucideIcon;
  onSelect: () => void;
  delay?: number;
}

export function DatasetCard({
  name,
  description,
  rows,
  columns,
  icon,
  onSelect,
  delay = 0,
}: DatasetCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
      whileHover={{ y: -8, scale: 1.02 }}
      className="bg-[#1e293b] rounded-xl p-6 border border-gray-700 hover:border-indigo-500 transition-all duration-300 cursor-pointer shadow-xl hover:shadow-indigo-500/20 group"
      onClick={onSelect}
    >
      <div className="flex items-center mb-4">
        <div className="w-12 h-12 bg-indigo-500/10 rounded-lg flex items-center justify-center group-hover:bg-indigo-500/20 transition-all duration-300">
          {icon && <icon className="w-6 h-6 text-indigo-400" />}
        </div>
      </div>

      <h3 className="text-xl font-semibold mb-2">{name}</h3>
      <p className="text-gray-400 text-sm mb-6 min-h-[40px]">{description}</p>

      <div className="flex items-center gap-4 mb-6 text-sm text-gray-500">
        <div className="flex items-center gap-1">
          <Database className="w-4 h-4" />
          <span>{rows.toLocaleString()} rows</span>
        </div>
        <div className="flex items-center gap-1">
          <span>•</span>
          <span>{columns} columns</span>
        </div>
      </div>

      <button className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-700 rounded-lg font-medium transition-all duration-300 group-hover:shadow-lg group-hover:shadow-indigo-500/30">
        Use this data
      </button>
    </motion.div>
  );
}
