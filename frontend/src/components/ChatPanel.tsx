/**
 * AI 对话面板组件
 */
"use client";

import { useState } from "react";
import { useAnalysisStore } from "@/stores/analysis";
import { chatStream } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export function ChatPanel() {
  const { analysisId, status } = useAnalysisStore();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim() || !analysisId) return;
    const userMsg = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setIsLoading(true);

    let assistantContent = "";
    setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

    try {
      for await (const chunk of chatStream(analysisId, userMsg)) {
        assistantContent += chunk;
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            role: "assistant",
            content: assistantContent,
          };
          return updated;
        });
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "对话出错，请稍后重试" },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  if (status !== "done") {
    return null;
  }

  return (
    <div className="flex flex-col h-[600px] border border-black/10">
      {/* 消息列表 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-black/30 py-12">
            <p className="text-lg mb-2">分析完成</p>
            <p className="text-sm">开始提问吧，我可以解释代码、讨论架构、找 Bug</p>
          </div>
        )}
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] px-4 py-3 text-sm whitespace-pre-wrap ${
                msg.role === "user"
                  ? "bg-black text-white"
                  : "bg-black/5 text-black"
              }`}
            >
              {msg.content}
              {isLoading && i === messages.length - 1 && msg.role === "assistant" && (
                <span className="animate-pulse">▌</span>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* 输入框 */}
      <div className="border-t border-black/10 p-4 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="问一个关于这个仓库的问题..."
          className="flex-1 px-3 py-2 border border-black/20 text-sm focus:outline-none focus:border-black"
          disabled={isLoading}
        />
        <button
          onClick={handleSend}
          disabled={isLoading || !input.trim()}
          className="px-4 py-2 bg-black text-white text-sm font-bold hover:bg-black/90 disabled:opacity-50"
        >
          发送
        </button>
      </div>
    </div>
  );
}
