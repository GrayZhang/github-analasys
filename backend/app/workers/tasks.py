"""
分析 Worker (ARQ) - 异步分析任务
"""
from typing import Dict, Any
import asyncio


async def analyze_repo(ctx: Dict[str, Any], analysis_id: str, owner: str, repo: str, branch: str = "main"):
    """
    主分析任务：串联 4 个阶段
    1. repo_fetch  - 抓取仓库
    2. code_index  - 索引 + 向量化
    3. ai_analysis - AI 分析 (分层摘要)
    4. diagram_gen - 流程图生成
    """
    print(f"[Worker] Starting analysis: {owner}/{repo} (branch={branch})")

    # TODO: 实现完整 pipeline
    # 1. 调用 GitHubService 获取仓库
    # 2. 文件分级 → 逐文件摘要
    # 3. 模块聚合 → 项目级摘要
    # 4. 流程图生成 → 语法校验
    # 5. 写入数据库

    await asyncio.sleep(1)  # placeholder
    print(f"[Worker] Analysis stub complete for {owner}/{repo}")
    return {"status": "done", "analysis_id": analysis_id}


class WorkerSettings:
    functions = [analyze_repo]
    redis_settings = None  # TODO: 配置 ARQ Redis
    on_startup = None
    on_shutdown = None
