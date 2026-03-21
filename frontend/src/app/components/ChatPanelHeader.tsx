import { Bot } from "lucide-react";

export function ChatPanelHeader() {
  return (
    <div className="p-6 border-b border-gray-800">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center">
          <Bot className="w-6 h-6 text-white" />
        </div>
        <div>
          <h3 className="font-semibold text-lg">AI Analyst</h3>
          <p className="text-sm text-gray-400">Always online</p>
        </div>
      </div>
    </div>
  );
}
