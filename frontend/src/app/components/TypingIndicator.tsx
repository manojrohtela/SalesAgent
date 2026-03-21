import { motion } from "motion/react";
import { Bot } from "lucide-react";

export function TypingIndicator() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex justify-start"
    >
      <div className="flex gap-3 max-w-[85%]">
        <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center flex-shrink-0">
          <Bot className="w-4 h-4" />
        </div>
        <div className="bg-[#1e293b] border border-gray-700 rounded-2xl px-4 py-3">
          <div className="flex gap-1">
            <motion.div
              className="w-2 h-2 bg-gray-500 rounded-full"
              animate={{ y: [0, -5, 0] }}
              transition={{
                duration: 0.6,
                repeat: Infinity,
                delay: 0,
              }}
            />
            <motion.div
              className="w-2 h-2 bg-gray-500 rounded-full"
              animate={{ y: [0, -5, 0] }}
              transition={{
                duration: 0.6,
                repeat: Infinity,
                delay: 0.2,
              }}
            />
            <motion.div
              className="w-2 h-2 bg-gray-500 rounded-full"
              animate={{ y: [0, -5, 0] }}
              transition={{
                duration: 0.6,
                repeat: Infinity,
                delay: 0.4,
              }}
            />
          </div>
        </div>
      </div>
    </motion.div>
  );
}
