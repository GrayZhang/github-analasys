"""
GitHub API 集成服务
"""
import httpx
from typing import Optional, Dict, Any, List


class GitHubService:
    BASE_URL = "https://api.github.com"

    def __init__(self, token: Optional[str] = None):
        self.headers = {"Accept": "application/vnd.github+json"}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    async def get_repo_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """获取仓库元信息"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.BASE_URL}/repos/{owner}/{repo}",
                headers=self.headers,
            )
            resp.raise_for_status()
            return resp.json()

    async def get_file_tree(self, owner: str, repo: str, branch: str = "main") -> Dict[str, Any]:
        """获取完整目录树 (递归)"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.BASE_URL}/repos/{owner}/{repo}/git/trees/{branch}",
                headers=self.headers,
                params={"recursive": 1},
            )
            resp.raise_for_status()
            return resp.json()

    async def get_file_content(self, owner: str, repo: str, path: str) -> str:
        """获取文件内容"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.BASE_URL}/repos/{owner}/{repo}/contents/{path}",
                headers={**self.headers, "Accept": "application/vnd.github.raw"},
            )
            resp.raise_for_status()
            return resp.text

    async def get_languages(self, owner: str, repo: str) -> Dict[str, int]:
        """获取语言分布"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.BASE_URL}/repos/{owner}/{repo}/languages",
                headers=self.headers,
            )
            resp.raise_for_status()
            return resp.json()
