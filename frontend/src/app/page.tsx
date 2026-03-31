/**
 * RepoLens 首页 - URL 输入 + 分析入口 (接入真实 API)
 */
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { startAnalysis } from "@/lib/api";

export default function Home() {
  const router = useRouter();
  const [repoUrl, setRepoUrl] = useState("");
  const [branch, setBranch] = useState("main");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!repoUrl.trim()) return;
    setIsAnalyzing(true);
    setError(null);

    try {
      const { analysis_id } = await startAnalysis({
        repo_url: repoUrl.trim(),
        branch: branch.trim(),
      });
      router.push(`/analyze/${analysis_id}`);
    } catch (err: any) {
      setError(err.message || "分析请求失败");
      setIsAnalyzing(false);
    }
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
            onKeyDown={(e) => e.key === "Enter" && handleAnalyze()}
            placeholder="https://github.com/owner/repo"
            className="flex-1 px-4 py-3 border border-black/20 rounded-none text-base focus:outline-none focus:border-black"
            disabled={isAnalyzing}
          />
          <input
            type="text"
            value={branch}
            onChange={(e) => setBranch(e.target.value)}
            placeholder="main"
            className="w-28 px-4 py-3 border border-black/20 rounded-none text-base focus:outline-none focus:border-black"
            disabled={isAnalyzing}
          />
          <button
            onClick={handleAnalyze}
            disabled={isAnalyzing || !repoUrl.trim()}
            className="px-6 py-3 bg-black text-white font-bold hover:bg-black/90 disabled:opacity-50 transition-colors"
          >
            {isAnalyzing ? "分析中..." : "分析"}
          </button>
        </div>

        {error && (
          <p className="text-red-500 text-sm mt-4">{error}</p>
        )}

        <p className="text-xs text-black/30 mt-4">
          支持 Public 和 Private 仓库（Private 需 GitHub OAuth 授权）
        </p>

        {/* 示例仓库 */}
        <div className="mt-8">
          <p className="text-xs text-black/40 mb-2">示例仓库：</p>
          <div className="flex flex-wrap gap-2 justify-center">
            {[
              "facebook/react",
              "vercel/next.js",
              "fastapi/fastapi",
              "GrayZhang/github-analasys",
            ].map((repo) => (
              <button
                key={repo}
                onClick={() => setRepoUrl(`https://github.com/${repo}`)}
                className="text-xs px-3 py-1 border border-black/10 hover:border-black/30 text-black/60 hover:text-black transition-colors"
              >
                {repo}
              </button>
            ))}
          </div>
        </div>
      </div>
    </main>
  );
}
