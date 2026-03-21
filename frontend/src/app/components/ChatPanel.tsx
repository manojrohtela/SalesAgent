import { useState, useRef, useEffect } from "react";
import { Send } from "lucide-react";
import { ChatMessage } from "./ChatMessage";
import { TypingIndicator } from "./TypingIndicator";
import { ChatPanelHeader } from "./ChatPanelHeader";

interface Message {
  id: number;
  type: "user" | "ai";
  content: string;
}

interface ChatPanelProps {
  initialMessages?: Message[];
}

export function ChatPanel({ initialMessages = [] }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>(
    initialMessages.length > 0
      ? initialMessages
      : [
          {
            id: 1,
            type: "ai",
            content: "Hello! I've analyzed your data. What insights would you like to explore?",
          },
        ]
  );
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSendMessage = () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: messages.length + 1,
      type: "user",
      content: inputValue,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsTyping(true);

    // Simulate AI response
    setTimeout(() => {
      const aiMessage: Message = {
        id: messages.length + 2,
        type: "ai",
        content:
          "That's a great question! Based on the data analysis, I can see several interesting patterns that might help answer your query. The revenue trends show significant growth in Q3, particularly in the e-commerce segment.",
      };
      setMessages((prev) => [...prev, aiMessage]);
      setIsTyping(false);
    }, 2000);
  };

  return (
    <div className="w-full md:w-[400px] border-l border-gray-800 bg-[#1e293b]/30 flex flex-col">
      <ChatPanelHeader />

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((message) => (
          <ChatMessage
            key={message.id}
            type={message.type}
            content={message.content}
          />
        ))}

        {isTyping && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </div>

      {/* Chat Input */}
      <div className="p-4 border-t border-gray-800 bg-[#1e293b]/50">
        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
            placeholder="Ask anything about your data..."
            className="flex-1 bg-[#0f172a] border border-gray-700 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent placeholder-gray-500"
          />
          <button
            onClick={handleSendMessage}
            disabled={!inputValue.trim()}
            className="px-4 py-3 bg-indigo-600 hover:bg-indigo-700 rounded-lg transition-all duration-300 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}
