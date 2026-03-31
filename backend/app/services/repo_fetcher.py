"""
GitHub 仓库抓取与预处理
"""
import os
import shutil
import asyncio
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

import httpx

from app.core.config import settings


@dataclass
class FileInfo:
    path: str
    name: str
    size: int = 0
    tier: int = 3  # 0=ignore, 1=priority, 2=business, 3=low
    content: Optional[str] = None
    summary: Optional[str] = None


@dataclass
class RepoData:
    owner: str
    name: str
    url: str
    branch: str = "main"
    description: str = ""
    stars: int = 0
    language: str = ""
    languages: Dict[str, int] = field(default_factory=dict)
    default_branch: str = "main"
    commit_sha: str = ""
    clone_dir: Optional[str] = None
    files: List[FileInfo] = field(default_factory=list)
    file_tree: List[Dict] = field(default_factory=list)


# ── 文件分级规则 ──────────────────────────────────────────────────────────

TIER0_IGNORE_DIRS = {
    ".git", "node_modules", "vendor", "dist", "build", "__pycache__",
    ".next", ".venv", "venv", ".tox", ".mypy_cache", "target",
    "coverage", ".nyc_output", ".output", ".svelte-kit",
}

TIER0_EXTENSIONS = {
    ".min.js", ".min.css", ".map", ".lock", ".log", ".pyc", ".pyo",
    ".so", ".dylib", ".dll", ".exe", ".bin", ".o", ".a",
    ".jpg", ".jpeg", ".png", ".gif", ".svg", ".ico", ".webp",
    ".mp3", ".mp4", ".wav", ".avi", ".mov",
    ".woff", ".woff2", ".ttf", ".eot",
    ".zip", ".tar", ".gz", ".rar", ".7z",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx",
    ".wasm", ".node",
}

TIER1_PRIORITY = {
    "readme", "readme.md", "readme.rst", "readme.txt",
    "package.json", "requirements.txt", "pyproject.toml", "setup.py",
    "go.mod", "go.sum", "cargo.toml", "cargo.lock",
    "dockerfile", "docker-compose.yml", "docker-compose.yaml",
    "compose.yml", "compose.yaml",
    "main.py", "index.ts", "index.js", "app.py", "app.ts", "app.js",
    "manage.py", "wsgi.py", "asgi.py",
    "main.go", "main.rs", "lib.rs",
    "config.py", "config.ts", "config.js", ".env.example",
    "schema.ts", "schema.py", "models.py", "models.ts",
    "settings.py", "settings.ts",
    ".github", ".gitlab-ci.yml",
    "nginx.conf", "caddyfile",
}

TIER1_PREFIXES = {"dockerfile", ".github"}


def classify_file(path: str) -> int:
    """文件分级：0=忽略, 1=高优先, 2=业务逻辑, 3=低优先"""
    parts = path.replace("\\", "/").split("/")
    basename = parts[-1].lower()

    # Tier 0: 忽略目录
    for part in parts[:-1]:
        if part in TIER0_IGNORE_DIRS:
            return 0

    # Tier 0: 忽略扩展名
    for ext in TIER0_EXTENSIONS:
        if basename.endswith(ext):
            return 0

    # Tier 0: 特大文件判断 (占位，实际由 size 判断)
    # Tier 1: 高优先级
    if basename in TIER1_PRIORITY:
        return 1
    for prefix in TIER1_PREFIXES:
        if basename.startswith(prefix):
            return 1

    # Tier 2: 业务代码
    if basename.endswith((".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java", ".rb", ".php", ".cs", ".cpp", ".c", ".h")):
        return 2

    # Tier 3: 测试/文档/配置
    if basename.endswith((".test.ts", ".test.tsx", ".test.js", ".spec.ts", ".spec.py", ".md", ".rst", ".yml", ".yaml", ".toml", ".json", ".sql")):
        return 3

    return 3


class RepoFetcher:
    """GitHub 仓库抓取器"""

    def __init__(self, token: Optional[str] = None):
        self.token = token or settings.GITHUB_TOKEN
        self.headers = {"Accept": "application/vnd.github+json"}
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

    async def fetch_repo(self, owner: str, repo: str, branch: str = "main") -> RepoData:
        """
        完整抓取流程：
        1. 获取仓库元信息
        2. 获取目录树
        3. 获取语言分布
        4. 克隆或 API 拉取文件
        5. 文件分级
        """
        repo_data = RepoData(owner=owner, name=repo, url=f"https://github.com/{owner}/{repo}", branch=branch)

        # 1. 元信息
        meta = await self._get_repo_meta(owner, repo)
        repo_data.description = meta.get("description", "")
        repo_data.stars = meta.get("stargazers_count", 0)
        repo_data.language = meta.get("language", "")
        repo_data.default_branch = meta.get("default_branch", "main")
        if branch == "main" and repo_data.default_branch != "main":
            repo_data.branch = repo_data.default_branch

        # 2. 语言分布
        repo_data.languages = await self._get_languages(owner, repo)

        # 3. 目录树
        tree_data = await self._get_file_tree(owner, repo, repo_data.branch)
        raw_tree = tree_data.get("tree", [])
        repo_data.commit_sha = tree_data.get("sha", "")

        # 4. 文件分级
        for item in raw_tree:
            if item.get("type") == "blob":
                path = item["path"]
                fi = FileInfo(
                    path=path,
                    name=path.split("/")[-1],
                    size=item.get("size", 0),
                    tier=classify_file(path),
                )
                repo_data.files.append(fi)

        # 5. 只拉取 Tier 1/2 文件内容 (API 模式)
        tier12 = [f for f in repo_data.files if f.tier in (1, 2)]
        contents = await self._fetch_file_contents_batch(owner, repo, repo_data.branch, tier12)
        for fi in tier12:
            if fi.path in contents:
                fi.content = contents[fi.path]

        # 6. 构建文件树 (仅非 Tier0)
        repo_data.file_tree = self._build_tree(repo_data.files)

        return repo_data

    async def _get_repo_meta(self, owner: str, repo: str) -> Dict:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(f"https://api.github.com/repos/{owner}/{repo}", headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    async def _get_languages(self, owner: str, repo: str) -> Dict[str, int]:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(f"https://api.github.com/repos/{owner}/{repo}/languages", headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    async def _get_file_tree(self, owner: str, repo: str, branch: str) -> Dict:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}",
                headers=self.headers,
                params={"recursive": 1},
            )
            resp.raise_for_status()
            return resp.json()

    async def _fetch_file_contents(self, owner: str, repo: str, branch: str, file_path: str) -> Optional[str]:
        """拉取单个文件内容"""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(
                    f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}",
                    headers={**self.headers, "Accept": "application/vnd.github.raw"},
                    params={"ref": branch},
                )
                if resp.status_code == 200:
                    return resp.text
        except Exception as e:
            print(f"[Fetcher] Failed to fetch {file_path}: {e}")
        return None

    async def _fetch_file_contents_batch(
        self, owner: str, repo: str, branch: str, files: List[FileInfo]
    ) -> Dict[str, str]:
        """批量拉取文件内容 (限流: 每批 5 个)"""
        results = {}
        batch_size = 5
        for i in range(0, len(files), batch_size):
            batch = files[i:i + batch_size]
            tasks = [
                self._fetch_file_contents(owner, repo, branch, f.path)
                for f in batch
            ]
            contents = await asyncio.gather(*tasks)
            for fi, content in zip(batch, contents):
                if content is not None:
                    results[fi.path] = content
            # GitHub API rate limit: 简单限流
            if i + batch_size < len(files):
                await asyncio.sleep(0.5)
        return results

    def _build_tree(self, files: List[FileInfo]) -> List[Dict]:
        """构建层级文件树"""
        tree = {}
        for fi in files:
            if fi.tier == 0:
                continue
            parts = fi.path.split("/")
            current = tree
            for j, part in enumerate(parts):
                if j == len(parts) - 1:
                    current[part] = {"name": part, "path": fi.path, "type": "file", "tier": fi.tier}
                else:
                    if part not in current or not isinstance(current[part], dict) or "children" not in current.get(part, {}):
                        current[part] = {"name": part, "type": "dir", "children": {}}
                    current = current[part]["children"]
        return self._tree_dict_to_list(tree)

    def _tree_dict_to_list(self, d: Dict) -> List:
        result = []
        for k, v in d.items():
            if isinstance(v, dict) and "children" in v:
                result.append({
                    "name": k,
                    "type": "dir",
                    "children": self._tree_dict_to_list(v["children"]),
                })
            else:
                result.append(v)
        return sorted(result, key=lambda x: (x["type"] != "dir", x.get("name", "")))
