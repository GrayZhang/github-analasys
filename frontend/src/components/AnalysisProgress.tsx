/**
 * 分析进度组件
 */
"use client";

import { useAnalysisStore } from "@/stores/analysis";

const STEPS = [
  "抓取仓库元信息",
  "克隆/下载关键文件",
  "代码索引与向量化",
  "AI 分析生成中",
  "流程图渲染中",
];

export function AnalysisProgress() {
  const { status, progress, currentStep, error } = useAnalysisStore();

  if (status === "idle" || status === "done" || status === "failed") {
    return null;
  }

  return (
    <div className="w-full max-w-xl mx-auto mt-8">
      <div className="flex justify-between mb-2">
        <span className="text-sm font-medium text-black/70">{currentStep || "排队中..."}</span>
        <span className="text-sm text-black/50">{progress}%</span>
      </div>

      <div className="w-full bg-black/10 h-2">
        <div
          className="bg-black h-2 transition-all duration-500"
          style={{ width: `${progress}%` }}
        />
      </div>

      <div className="mt-4 space-y-2">
        {STEPS.map((step, i) => {
          const stepProgress = ((i + 1) / STEPS.length) * 100;
          const isActive = progress >= stepProgress - 20 && progress < stepProgress;
          const isDone = progress >= stepProgress;

          return (
            <div
              key={step}
              className={`flex items-center gap-2 text-sm ${
                isDone
                  ? "text-green-600"
                  : isActive
                  ? "text-black font-medium"
                  : "text-black/30"
              }`}
            >
              <span>
                {isDone ? "✓" : isActive ? "●" : "○"}
              </span>
              <span>{step}</span>
            </div>
          );
        })}
      </div>

      {error && (
        <p className="text-red-500 text-sm mt-4">错误: {error}</p>
      )}
    </div>
  );
}
