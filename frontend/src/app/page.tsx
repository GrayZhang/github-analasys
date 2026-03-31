/**
 * RepoLens 首页 - URL 输入 + 分析入口
 */
"use client";

import { useState } from "react";

export default function Home() {
  const [repoUrl, setRepoUrl] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleAnalyze = () => {
    if (!repoUrl.trim()) return;
    setIsAnalyzing(true);
    // TODO: 调用 POST /api/v1/repos/analyze
    console.log("Analyzing:", repoUrl);
  };

  return (
    <main className="min-h-screen bg-white flex flex-col items-center justify-center p-8">
      <div className="max-w-2xl w-full text-center">
        <h1 className="text-5xl font-black mb-4 tracking-tight">
          RepoLens
        </h1>
        <p className="text-black/50 text-lg mb-12">
          输入 GitHub 仓库 URL，AI 自动读懂项目架构，生成交互式流程图
        </p>

        <div className="flex gap-3">
          <input
            type="text"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            placeholder="https://github.com/owner/repo"
            className="flex-1 px-4 py-3 border border-black/20 rounded-none text-base focus:outline-none focus:border-black"
          />
          <button
            onClick={handleAnalyze}
            disabled={isAnalyzing}
            className="px-6 py-3 bg-black text-white font-bold hover:bg-black/90 disabled:opacity-50 transition-colors"
          >
            {isAnalyzing ? "分析中..." : "分析"}
          </button>
        </div>

        <p className="text-xs text-black/30 mt-4">
          支持 Public 和 Private 仓库（Private 需 GitHub OAuth 授权）
        </p>
      </div>
    </main>
  );
}
