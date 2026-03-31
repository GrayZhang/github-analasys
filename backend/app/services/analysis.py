"""
代码分析服务 - 分层摘要
"""
from typing import Dict, Any, List


class AnalysisService:
    """
    分层摘要策略:
    Layer 1: 文件级摘要
    Layer 2: 模块级摘要
    Layer 3: 项目级摘要
    Layer 4: 流程图生成
    """

    # 文件分级 (Tier 0-3)
    TIER0_IGNORE = {
        ".git", "node_modules", "vendor", "dist", "build", "__pycache__",
        ".next", ".venv", "venv",
    }
    TIER0_EXTENSIONS = {".min.js", ".map", ".lock", ".log", ".pyc", ".pyo"}

    TIER1_PRIORITY = {
        "readme.md", "package.json", "requirements.txt", "go.mod", "cargo.toml",
        "dockerfile", "docker-compose.yml", ".github", "main.py", "index.ts",
        "index.js", "app.py", "app.ts", "manage.py", "main.go",
    }

    async def classify_files(self, file_tree: List[Dict]) -> Dict[int, List[Dict]]:
        """文件分级"""
        tiers = {1: [], 2: [], 3: [], 0: []}

        for item in file_tree:
            path = item.get("path", "")
            tier = self._classify_file(path)
            tiers[tier].append(item)

        return tiers

    def _classify_file(self, path: str) -> int:
        """单文件分级"""
        parts = path.split("/")
        basename = path.lower().split("/")[-1]

        # Tier 0: 忽略
        for ignore in self.TIER0_IGNORE:
            if ignore in parts:
                return 0
        for ext in self.TIER0_EXTENSIONS:
            if basename.endswith(ext):
                return 0

        # Tier 1: 高优先
        if basename in self.TIER1_PRIORITY:
            return 1
        if basename.startswith("dockerfile"):
            return 1
        if basename in {"schema.ts", "schema.py", "models.py", "config.py", ".env.example"}:
            return 1

        # Tier 2: 业务逻辑
        if basename.endswith((".py", ".ts", ".js", ".go", ".rs", ".java")):
            return 2

        # Tier 3: 测试/文档
        if basename.endswith((".test.ts", ".test.js", ".spec.ts", ".spec.py", ".md")):
            return 3

        return 3

    async def generate_file_summary(self, file_path: str, content: str) -> str:
        """生成文件级摘要 (Layer 1)"""
        # TODO: 调用 LLM 生成摘要
        return f"[stub] Summary for {file_path}"

    async def generate_module_summary(self, module_name: str, file_summaries: Dict[str, str]) -> str:
        """生成模块级摘要 (Layer 2)"""
        # TODO: 聚合文件摘要 → LLM
        return f"[stub] Module summary for {module_name}"

    async def generate_project_summary(self, modules: Dict[str, str], metadata: Dict) -> Dict[str, Any]:
        """生成项目级摘要 (Layer 3)"""
        # TODO: 聚合模块摘要 → LLM
        return {
            "project_type": "unknown",
            "description": "[stub]",
            "tech_stack": {},
            "architecture": {"pattern": "unknown", "modules": []},
            "data_flow": "[stub]",
        }

    async def generate_diagrams(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """生成流程图 (Layer 4)"""
        # TODO: 基于分析结果生成 Mermaid / JSON 图数据
        return {
            "system_architecture": "",
            "data_flow": "",
            "api_routes": "",
        }
