import { Bot, X } from "lucide-react";

interface ChatPanelHeaderProps {
  onClose?: () => void;
}

export function ChatPanelHeader({ onClose }: ChatPanelHeaderProps) {
  return (
    <div className="border-b border-gray-800/80 px-5 py-4">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-cyan-500 via-indigo-500 to-fuchsia-500 rounded-full flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <Bot className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-lg text-white">AI Assistant</h3>
            <p className="text-sm text-slate-400">Ask for charts, trends, comparisons, or quick insights</p>
          </div>
        </div>
        {onClose ? (
          <button
            type="button"
            onClick={onClose}
            className="rounded-full border border-white/10 bg-white/5 p-2 text-slate-300 transition-colors hover:bg-white/10 hover:text-white"
            aria-label="Close chat"
          >
            <X className="h-4 w-4" />
          </button>
        ) : null}
      </div>
    </div>
  );
}
