"""
代码分析 Pipeline - 分层摘要 (4 阶段)
"""
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from app.services.repo_fetcher import FileInfo, RepoData


@dataclass
class FileSummary:
    path: str
    name: str
    tier: int
    responsibility: str = ""
    interfaces: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    key_logic: str = ""


@dataclass
class ModuleSummary:
    name: str
    responsibility: str = ""
    key_files: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)


@dataclass
class ProjectSummary:
    project_type: str = "unknown"
    description: str = ""
    tech_stack: Dict[str, Any] = field(default_factory=dict)
    architecture: Dict[str, Any] = field(default_factory=dict)
    data_flow: str = ""
    entry_points: List[str] = field(default_factory=list)
    potential_issues: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class AnalysisResult:
    repo_data: RepoData
    file_summaries: Dict[str, FileSummary] = field(default_factory=dict)
    module_summaries: Dict[str, ModuleSummary] = field(default_factory=dict)
    project_summary: Optional[ProjectSummary] = None
    diagrams: Dict[str, str] = field(default_factory=dict)


class AnalysisPipeline:
    """
    4 阶段分析 Pipeline:
    1. repo_fetch    - 抓取仓库 (已在 RepoFetcher 完成)
    2. file_summaries - 文件级摘要 (Layer 1)
    3. module_summaries - 模块级摘要 (Layer 2)
    4. project_summary - 项目级摘要 (Layer 3) + 流程图 (Layer 4)
    """

    def __init__(self, llm_client=None):
        self.llm = llm_client  # TODO: 注入 LLM 客户端

    async def run(self, repo_data: RepoData) -> AnalysisResult:
        """执行完整分析 pipeline"""
        result = AnalysisResult(repo_data=repo_data)

        # Phase 1: 文件级摘要
        result.file_summaries = await self._layer1_file_summaries(repo_data)

        # Phase 2: 模块级摘要
        result.module_summaries = await self._layer2_module_summaries(result.file_summaries)

        # Phase 3: 项目级摘要
        result.project_summary = await self._layer3_project_summary(
            result.module_summaries, repo_data
        )

        # Phase 4: 流程图生成
        result.diagrams = await self._layer4_diagrams(result)

        return result

    async def _layer1_file_summaries(self, repo_data: RepoData) -> Dict[str, FileSummary]:
        """Layer 1: 文件级摘要"""
        summaries = {}
        tier12 = [f for f in repo_data.files if f.tier in (1, 2) and f.content]

        if not tier12:
            return summaries

        # 批量生成摘要 (每批 5 个)
        batch_size = 5
        for i in range(0, len(tier12), batch_size):
            batch = tier12[i:i + batch_size]
            tasks = [self._generate_file_summary(fi) for fi in batch]
            batch_summaries = await asyncio.gather(*tasks)
            for fi, summary in zip(batch, batch_summaries):
                summaries[fi.path] = summary
            if i + batch_size < len(tier12):
                await asyncio.sleep(0.2)

        return summaries

    async def _generate_file_summary(self, fi: FileInfo) -> FileSummary:
        """生成单文件摘要"""
        summary = FileSummary(path=fi.path, name=fi.name, tier=fi.tier)

        # TODO: 调用 LLM 生成真正的摘要
        # 当前用简单规则生成占位摘要
        if fi.content:
            lines = fi.content.split("\n")
            summary.responsibility = f"File with {len(lines)} lines ({fi.name})"
            # 简单提取 import/require
            imports = []
            for line in lines[:50]:
                stripped = line.strip()
                if stripped.startswith("import ") or stripped.startswith("from "):
                    imports.append(stripped[:80])
                elif stripped.startswith("require(") or stripped.startswith("const ") and "=" in stripped and "require" in stripped:
                    imports.append(stripped[:80])
            summary.dependencies = imports[:5]

        return summary

    async def _layer2_module_summaries(self, file_summaries: Dict[str, FileSummary]) -> Dict[str, ModuleSummary]:
        """Layer 2: 模块级摘要"""
        # 按目录分组
        modules: Dict[str, List[FileSummary]] = {}
        for path, fs in file_summaries.items():
            parts = path.split("/")
            if len(parts) > 1:
                module_name = parts[0]
            else:
                module_name = "(root)"
            modules.setdefault(module_name, []).append(fs)

        summaries = {}
        for module_name, files in modules.items():
            ms = ModuleSummary(
                name=module_name,
                key_files=[f.path for f in files[:10]],
            )
            # TODO: 调用 LLM 生成模块摘要
            ms.responsibility = f"Module '{module_name}' with {len(files)} files"
            summaries[module_name] = ms

        return summaries

    async def _layer3_project_summary(
        self, module_summaries: Dict[str, ModuleSummary], repo_data: RepoData
    ) -> ProjectSummary:
        """Layer 3: 项目级摘要"""
        ps = ProjectSummary(
            description=repo_data.description or f"{repo_data.owner}/{repo_data.name}",
            tech_stack={
                "primary_language": repo_data.language,
                "languages": repo_data.languages,
            },
            entry_points=[],
        )

        # 简单类型推断
        for f in repo_data.files:
            if f.name.lower() in {"main.py", "app.py", "manage.py"}:
                ps.entry_points.append(f.path)
            elif f.name.lower() in {"index.ts", "index.js", "main.ts"}:
                ps.entry_points.append(f.path)
            elif f.name.lower() in {"main.go"}:
                ps.entry_points.append(f.path)

        if not ps.entry_points:
            ps.entry_points = ["(not detected)"]

        # TODO: 调用 LLM 做更精细的架构分析
        ps.architecture = {
            "pattern": "unknown",
            "modules": [{"name": k, "responsibility": v.responsibility} for k, v in module_summaries.items()],
        }

        return ps

    async def _layer4_diagrams(self, result: AnalysisResult) -> Dict[str, str]:
        """Layer 4: 流程图生成 (Mermaid)"""
        diagrams = {}

        # 系统架构图
        diagrams["system_architecture"] = self._generate_system_arch_mermaid(result)

        # 数据流图
        diagrams["data_flow"] = self._generate_data_flow_mermaid(result)

        return diagrams

    def _generate_system_arch_mermaid(self, result: AnalysisResult) -> str:
        """生成系统架构 Mermaid 图"""
        lines = ["graph TD"]

        # 基于模块生成节点
        modules = list(result.module_summaries.keys())[:12]
        for i, mod in enumerate(modules):
            safe_id = f"mod{i}"
            ms = result.module_summaries[mod]
            label = f"{mod}\\n{ms.responsibility[:30]}"
            lines.append(f'    {safe_id}["{label}"]')

        # 基于依赖生成边 (简化)
        for i, mod in enumerate(modules):
            ms = result.module_summaries[mod]
            for dep in ms.dependencies[:3]:
                for j, other_mod in enumerate(modules):
                    if other_mod != mod and other_mod in dep.lower():
                        lines.append(f"    mod{i} --> mod{j}")

        if len(lines) == 1:
            lines.append('    frontend["Frontend"] --> backend["Backend"]')
            lines.append('    backend --> db["Database"]')

        return "\n".join(lines)

    def _generate_data_flow_mermaid(self, result: AnalysisResult) -> str:
        """生成数据流 Mermaid 图"""
        # TODO: 基于实际分析结果生成
        return """flowchart LR
    input["User Input"] --> api["API Layer"]
    api --> service["Service Layer"]
    service --> db["Database"]
    service --> cache["Cache"]
    service --> llm["LLM"]
    llm --> result["Result"]
    result --> output["User Output"]"""
