/**
 * RepoLens 分析报告页面 - 展示分析结果
 */
"use client";

import { useEffect, useState } from "react";
import { useAnalysisStore } from "@/stores/analysis";
import { getAnalysisReport, getDiagrams } from "@/lib/api";
import { AnalysisProgress } from "@/components/AnalysisProgress";
import { ArchitectureDiagram } from "@/components/ArchitectureDiagram";
import { ChatPanel } from "@/components/ChatPanel";

export default function AnalyzePage({
  params,
}: {
  params: { id: string };
}) {
  const analysisId = params.id;
  const { status } = useAnalysisStore();
  const [report, setReport] = useState<any>(null);
  const [diagrams, setDiagrams] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!analysisId) return;

    const load = async () => {
      try {
        setLoading(true);
        const reportData = await getAnalysisReport(analysisId);
        setReport(reportData);

        try {
          const diagramsData = await getDiagrams(analysisId);
          setDiagrams(diagramsData);
        } catch {
          // diagrams might not be ready
        }
      } catch (err: any) {
        setError(err.message || "Failed to load analysis");
      } finally {
        setLoading(false);
      }
    };

    // 轮询直到完成
    const interval = setInterval(async () => {
      try {
        const data = await getAnalysisReport(analysisId);
        if (data.status === "done") {
          setReport(data);
          clearInterval(interval);
          setLoading(false);
        } else if (data.status === "failed") {
          setError("Analysis failed");
          clearInterval(interval);
          setLoading(false);
        }
      } catch {
        // still pending
      }
    }, 3000);

    load();
    return () => clearInterval(interval);
  }, [analysisId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <p className="text-lg font-medium mb-4">分析中...</p>
          <AnalysisProgress />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-500 text-lg">{error}</p>
        </div>
      </div>
    );
  }

  if (!report) return null;

  return (
    <div className="min-h-screen bg-white">
      {/* 头部 */}
      <header className="border-b border-black/10 px-8 py-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-black">{report.owner}/{report.repo}</h1>
            <p className="text-sm text-black/50 mt-1">{report.description}</p>
            <div className="flex items-center gap-4 mt-2 text-xs text-black/40">
              <span>⭐ {report.stars}</span>
              <span>{report.language}</span>
              <span>{report.file_count} files</span>
              <span>{report.branch}</span>
            </div>
          </div>
          <a
            href="/"
            className="px-4 py-2 border border-black/20 text-sm font-medium hover:bg-black/5"
          >
            分析其他仓库
          </a>
        </div>
      </header>

      <div className="grid grid-cols-3 gap-8 px-8 py-8">
        {/* 左侧：架构图 */}
        <div className="col-span-2">
          <h2 className="text-xl font-black mb-4">架构流程图</h2>
          <ArchitectureDiagram />

          {/* Mermaid 源码 */}
          {diagrams?.diagrams?.system_architecture && (
            <details className="mt-4">
              <summary className="text-sm text-black/50 cursor-pointer hover:text-black">
                查看 Mermaid 源码
              </summary>
              <pre className="mt-2 p-4 bg-black/5 text-xs font-mono overflow-auto">
                {diagrams.diagrams.system_architecture}
              </pre>
            </details>
          )}
        </div>

        {/* 右侧：项目概览 */}
        <div className="col-span-1">
          <h2 className="text-xl font-black mb-4">项目概览</h2>

          <div className="space-y-6">
            {/* 技术栈 */}
            <div>
              <h3 className="text-sm font-bold text-black/60 mb-2">技术栈</h3>
              <div className="space-y-1">
                <p className="text-sm">
                  <span className="text-black/50">主语言:</span>{" "}
                  <span className="font-medium">{report.language}</span>
                </p>
                {report.languages && Object.entries(report.languages).map(([lang, bytes]) => (
                  <p key={lang} className="text-xs text-black/50">
                    {lang}: {String(bytes)}
                  </p>
                ))}
              </div>
            </div>

            {/* 入口文件 */}
            <div>
              <h3 className="text-sm font-bold text-black/60 mb-2">入口文件</h3>
              {report.project_summary?.entry_points?.map((ep: string) => (
                <p key={ep} className="text-xs font-mono text-black/70">{ep}</p>
              ))}
            </div>

            {/* 模块 */}
            <div>
              <h3 className="text-sm font-bold text-black/60 mb-2">模块</h3>
              <div className="space-y-2">
                {report.module_summaries && Object.values(report.module_summaries).map((ms: any) => (
                  <div key={ms.name} className="border border-black/10 p-3">
                    <p className="text-sm font-medium">{ms.name}</p>
                    <p className="text-xs text-black/50">{ms.responsibility}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* 文件统计 */}
            <div>
              <h3 className="text-sm font-bold text-black/60 mb-2">文件统计</h3>
              <p className="text-sm">总计: {report.file_count} 个文件</p>
              <p className="text-xs text-black/50">Tier 1 (核心): {report.tier1_count}</p>
              <p className="text-xs text-black/50">Tier 2 (业务): {report.tier2_count}</p>
            </div>
          </div>
        </div>
      </div>

      {/* 对话面板 */}
      <div className="px-8 py-8">
        <h2 className="text-xl font-black mb-4">AI 对话</h2>
        <ChatPanel />
      </div>
    </div>
  );
}
