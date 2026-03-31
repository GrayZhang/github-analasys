/**
 * RepoLens - GitHub Repository AI Analyzer
 * Next.js 前端入口
 */

import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "RepoLens - GitHub Repo AI Analyzer",
  description: "输入一个 GitHub 仓库 URL，AI 自动读懂整个项目，生成交互式架构流程图",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
