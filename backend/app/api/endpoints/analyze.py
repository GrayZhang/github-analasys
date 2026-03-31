"""
分析结果 API - 接入真实 Pipeline
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uuid

from app.services.repo_fetcher import RepoFetcher
from app.services.analysis import AnalysisPipeline

router = APIRouter()

# 内存存储 (Phase 1 用内存，后续迁移到 PostgreSQL)
_analysis_cache: Dict[str, Dict[str, Any]] = {}


class AnalyzeRequest(BaseModel):
    repo_url: str
    branch: str = "main"


class AnalyzeResponse(BaseModel):
    analysis_id: str
    status: str
    message: str


class AnalysisStatus(BaseModel):
    id: str
    status: str
    progress: int
    current_step: str
    error: Optional[str] = None


def parse_github_url(url: str) -> tuple:
    """从 GitHub URL 解析 owner/repo"""
    url = url.strip().rstrip("/")
    if url.startswith("git@github.com:"):
        url = url.replace("git@github.com:", "https://github.com/")
    if "github.com/" not in url:
        raise HTTPException(status_code=400, detail=f"Invalid GitHub URL: {url}")

    path = url.split("github.com/")[1].split("?")[0]
    parts = path.split("/")
    if len(parts) < 2:
        raise HTTPException(status_code=400, detail=f"Invalid GitHub URL: {url}")

    owner = parts[0]
    repo = parts[1].replace(".git", "")
    return owner, repo


@router.post("/analyze", response_model=AnalyzeResponse)
async def start_analysis(body: AnalyzeRequest):
    """提交分析任务"""
    try:
        owner, repo = parse_github_url(body.repo_url)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse URL: {e}")

    analysis_id = str(uuid.uuid4())[:8]

    # 检查缓存
    cache_key = f"{owner}/{repo}:{body.branch}"
    for existing_id, data in _analysis_cache.items():
        if data.get("cache_key") == cache_key and data.get("status") == "done":
            return AnalyzeResponse(
                analysis_id=existing_id,
                status="cached",
                message=f"Using cached result for {owner}/{repo}",
            )

    # 初始化分析记录
    _analysis_cache[analysis_id] = {
        "id": analysis_id,
        "owner": owner,
        "repo": repo,
        "branch": body.branch,
        "url": body.repo_url,
        "cache_key": cache_key,
        "status": "pending",
        "progress": 0,
        "current_step": "Queued",
        "result": None,
        "error": None,
    }

    # TODO: 异步执行 (当前同步执行)
    await _run_analysis(analysis_id)

    return AnalyzeResponse(
        analysis_id=analysis_id,
        status="started",
        message=f"Analysis started for {owner}/{repo}",
    )


async def _run_analysis(analysis_id: str):
    """执行分析 (Phase 1: 同步执行)"""
    data = _analysis_cache.get(analysis_id)
    if not data:
        return

    owner = data["owner"]
    repo = data["repo"]
    branch = data["branch"]

    try:
        # Phase 1: 抓取
        data["status"] = "fetching"
        data["progress"] = 10
        data["current_step"] = "抓取仓库元信息"

        fetcher = RepoFetcher()
        repo_data = await fetcher.fetch_repo(owner, repo, branch)

        data["progress"] = 40
        data["current_step"] = f"已获取 {len(repo_data.files)} 个文件"

        # Phase 2: 分析
        data["status"] = "analyzing"
        data["progress"] = 50
        data["current_step"] = "AI 分析生成中"

        pipeline = AnalysisPipeline()
        result = await pipeline.run(repo_data)

        data["progress"] = 80
        data["current_step"] = "流程图渲染中"

        # 存储结果
        data["result"] = {
            "owner": owner,
            "repo": repo,
            "branch": branch,
            "url": data["url"],
            "description": repo_data.description,
            "stars": repo_data.stars,
            "language": repo_data.language,
            "languages": repo_data.languages,
            "commit_sha": repo_data.commit_sha,
            "file_count": len(repo_data.files),
            "tier1_count": sum(1 for f in repo_data.files if f.tier == 1),
            "tier2_count": sum(1 for f in repo_data.files if f.tier == 2),
            "file_summaries": {
                path: {
                    "path": fs.path,
                    "name": fs.name,
                    "tier": fs.tier,
                    "responsibility": fs.responsibility,
                    "dependencies": fs.dependencies[:5],
                }
                for path, fs in result.file_summaries.items()
            },
            "module_summaries": {
                name: {
                    "name": ms.name,
                    "responsibility": ms.responsibility,
                    "key_files": ms.key_files[:10],
                }
                for name, ms in result.module_summaries.items()
            },
            "project_summary": {
                "project_type": result.project_summary.project_type if result.project_summary else "unknown",
                "description": result.project_summary.description if result.project_summary else "",
                "tech_stack": result.project_summary.tech_stack if result.project_summary else {},
                "architecture": result.project_summary.architecture if result.project_summary else {},
                "entry_points": result.project_summary.entry_points if result.project_summary else [],
            },
            "diagrams": result.diagrams,
        }

        data["status"] = "done"
        data["progress"] = 100
        data["current_step"] = "完成"

    except Exception as e:
        data["status"] = "failed"
        data["error"] = str(e)
        data["current_step"] = f"失败: {str(e)[:100]}"
        print(f"[Analysis] Failed for {owner}/{repo}: {e}")


@router.get("/{analysis_id}/status", response_model=AnalysisStatus)
async def get_analysis_status(analysis_id: str):
    """查询分析进度"""
    data = _analysis_cache.get(analysis_id)
    if not data:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return AnalysisStatus(
        id=analysis_id,
        status=data["status"],
        progress=data["progress"],
        current_step=data["current_step"],
        error=data.get("error"),
    )


@router.get("/{analysis_id}/report")
async def get_analysis_report(analysis_id: str):
    """获取分析报告"""
    data = _analysis_cache.get(analysis_id)
    if not data:
        raise HTTPException(status_code=404, detail="Analysis not found")
    if data["status"] != "done":
        raise HTTPException(status_code=400, detail=f"Analysis status: {data['status']}")
    return data["result"]


@router.get("/{analysis_id}/diagrams")
async def get_diagrams(analysis_id: str):
    """获取流程图数据"""
    data = _analysis_cache.get(analysis_id)
    if not data or data["status"] != "done":
        raise HTTPException(status_code=404, detail="Analysis not found or not done")
    return {"diagrams": data["result"]["diagrams"]}


@router.get("/{analysis_id}/files")
async def get_file_tree(analysis_id: str):
    """获取文件树"""
    data = _analysis_cache.get(analysis_id)
    if not data or data["status"] != "done":
        raise HTTPException(status_code=404, detail="Analysis not found or not done")
    # TODO: 返回完整文件树
    return {"tree": data["result"].get("file_tree", [])}


@router.get("/{analysis_id}/files/{file_path:path}")
async def get_file_content(analysis_id: str, file_path: str):
    """获取单文件内容"""
    data = _analysis_cache.get(analysis_id)
    if not data or data["status"] != "done":
        raise HTTPException(status_code=404, detail="Analysis not found or not done")
    summaries = data["result"].get("file_summaries", {})
    if file_path in summaries:
        return summaries[file_path]
    return {"path": file_path, "error": "File not in analyzed set"}
