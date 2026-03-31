"""
仓库管理 API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional

router = APIRouter()


class RepoInfo(BaseModel):
    url: str
    branch: str = "main"
    owner: str
    name: str
    description: str = ""
    stars: int = 0
    language: str = ""
    default_branch: str = "main"


class AnalyzeRequest(BaseModel):
    repo_url: str
    branch: str = "main"


class AnalyzeResponse(BaseModel):
    analysis_id: str
    status: str
    message: str


@router.get("/{owner}/{repo}/info", response_model=RepoInfo)
async def get_repo_info(owner: str, repo: str):
    """获取 GitHub 仓库元信息"""
    # TODO: 调用 GitHub API 获取仓库信息
    return RepoInfo(
        url=f"https://github.com/{owner}/{repo}",
        branch="main",
        owner=owner,
        name=repo,
        description="(placeholder)",
    )


@router.post("/analyze", response_model=AnalyzeResponse)
async def start_analysis(body: AnalyzeRequest):
    """提交分析任务"""
    # TODO: 校验 URL 格式 → 调用 GitHub API 验证仓库存在 → 入队异步分析任务
    return AnalyzeResponse(
        analysis_id="placeholder-id",
        status="pending",
        message="Analysis queued",
    )
