# GitHub Repo AI Analyzer — 产品与研发文档

> **文档版本**: v1.0  
> **日期**: 2026-03-31  
> **产品代号**: RepoLens

---

## 一、产品概述

### 1.1 一句话定义

输入一个 GitHub 仓库 URL，AI 自动读懂整个项目，生成交互式架构流程图，并提供持续对话能力深挖代码实现、排查 Bug、讨论优化方案。

### 1.2 目标用户

| 用户类型 | 场景 | 痛点 |
|---------|------|------|
| 开发者（接手项目） | 新加入团队、接手遗留代码 | 没文档，不知道代码在干嘛 |
| 开源爱好者 | 评估是否使用某个开源库 | README 不够，想快速了解内部架构 |
| 技术面试官/候选人 | 评估/展示 GitHub 项目 | 需要快速理解项目全貌 |
| 技术 Leader | Code Review、架构审查 | 大项目难以快速把握全局 |
| 独立开发者 | 学习优秀开源项目的架构 | 逐文件阅读效率低 |

### 1.3 核心价值主张

- **秒懂项目**：5 分钟内理解一个陌生仓库的架构和核心逻辑
- **可视化架构**：自动生成交互式流程图，比 README 更直观
- **深度对话**：不只是概览，可以针对任意函数、模块追问细节
- **Bug 猎手**：AI 识别潜在 Bug、安全隐患、性能瓶颈

---

## 二、功能规格

### 2.1 功能模块总览

```
┌─────────────────────────────────────────────────────┐
│                    RepoLens 前端                      │
│  ┌──────────┐  ┌───────────────┐  ┌───────────────┐ │
│  │ URL 输入  │  │  架构流程图    │  │  AI 对话面板   │ │
│  │ + 控制台  │  │  (交互式)     │  │  (流式输出)    │ │
│  └──────────┘  └───────────────┘  └───────────────┘ │
│  ┌──────────────────────────────────────────────────┐│
│  │            分析报告 + 文件浏览器                    ││
│  └──────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────┘
```

### 2.2 模块一：仓库输入与控制台

**功能描述**：用户输入 GitHub URL，系统验证并触发分析流程，实时展示分析进度。

**详细需求**：

- 支持的 URL 格式：
  - `https://github.com/{owner}/{repo}`
  - `https://github.com/{owner}/{repo}/tree/{branch}`
  - `git@github.com:{owner}/{repo}.git`
- URL 合法性校验（正则 + GitHub API 验证仓库是否存在）
- 分支选择器（默认 main/master，可切换）
- 实时进度条显示分析阶段：
  - ① 抓取仓库元信息
  - ② 克隆/下载关键文件
  - ③ 代码索引与向量化
  - ④ AI 分析生成中
  - ⑤ 流程图渲染中
- 分析历史列表（侧边栏，可快速切换已分析的仓库）
- 支持 Public 和 Private 仓库（Private 需 GitHub OAuth 授权）

**边界情况处理**：

| 场景 | 处理方式 |
|------|---------|
| 空仓库 | 提示"该仓库暂无代码" |
| 超大仓库（>500MB / >10000 文件） | 提示预估分析时间，建议选择子目录分析 |
| 非代码仓库（纯文档/数据集） | 降级为文档摘要模式 |
| 仓库不存在或无权限 | 明确提示错误原因 |
| Fork 仓库 | 标注 fork 来源，可选择只分析差异 |

### 2.3 模块二：AI 分析引擎

**功能描述**：解析仓库结构，输出结构化分析报告。

**分析报告内容**：

1. **项目概览**
   - 项目名称、描述、License
   - 主要编程语言及占比
   - 依赖列表（package.json / requirements.txt / go.mod 等）
   - Star / Fork / 最近更新时间
   - 活跃度评估（commit 频率、contributor 数量）

2. **架构分析**
   - 项目类型识别（Web App / CLI / Library / Microservice / Monorepo 等）
   - 核心模块划分及各模块职责说明
   - 入口文件识别（main / index / app）
   - 设计模式识别（MVC / Event-driven / Plugin 等）
   - 技术栈详细拆解（框架、中间件、ORM、测试框架等）

3. **数据流分析**
   - 请求处理流程（API → Controller → Service → DB）
   - 数据模型关系
   - 外部依赖调用链（第三方 API、消息队列等）

4. **代码质量评估**
   - 潜在 Bug 清单（空指针、未处理异常、竞态条件等）
   - 安全隐患（硬编码密钥、SQL 注入、XSS 等）
   - 性能瓶颈识别（N+1 查询、未优化循环等）
   - 代码规范评分（命名、注释、文件组织）

5. **关键文件索引**
   - 标注哪些文件是核心逻辑、哪些是配置、哪些是辅助

### 2.4 模块三：交互式流程图

**功能描述**：基于分析结果生成可交互的架构图和流程图。

**图表类型**：

| 图表 | 说明 | 触发条件 |
|------|------|---------|
| 系统架构图 | 顶层模块关系，展示主要组件及其交互 | 默认生成 |
| 调用关系图 | 函数/方法级别的调用链 | 用户点击某模块后展开 |
| 数据流图 | 数据从输入到输出的完整路径 | 默认生成 |
| 数据库 ER 图 | 数据模型关系（如果有 ORM/Schema） | 检测到数据库模型时生成 |
| API 路由图 | 所有 API 端点及其处理链路 | 检测到 Web 框架时生成 |
| 部署架构图 | Docker/K8s/CI-CD 流程 | 检测到 Dockerfile/CI 配置时生成 |

**交互能力**：

- 缩放、拖拽、平移
- 点击节点 → 展开子模块 / 跳转到对应代码
- 点击节点 → 在对话面板中自动发起该模块的深入分析
- 节点悬停 → 显示简要说明 tooltip
- 层级切换：鸟瞰视图 ↔ 模块视图 ↔ 函数视图
- 搜索定位：输入关键词高亮相关节点
- 导出：PNG / SVG / Mermaid 源码

### 2.5 模块四：AI 对话面板

**功能描述**：基于仓库上下文的多轮对话系统，支持深入讨论代码细节。

**对话能力范围**：

- **代码解释**："这个函数是做什么的？" "这段正则表达式匹配什么？"
- **架构讨论**："为什么选择这种设计模式？" "这个模块和那个模块是怎么通信的？"
- **Bug 分析**："这里有没有潜在的并发问题？" "这个错误处理覆盖全了吗？"
- **改进建议**："如何优化这个查询的性能？" "这个模块怎么重构比较好？"
- **功能扩展**："如果要加一个缓存层应该放在哪？" "怎么给这个项目加认证？"
- **代码生成**："帮我写一个这个模块的单元测试" "帮我实现一个类似的功能"

**交互细节**：

- 流式输出（SSE），打字机效果
- 代码块语法高亮
- 消息中引用的文件名可点击，跳转到文件浏览器
- 对话中引用的代码行号可点击，跳转到源码
- 支持上传截图（如错误截图），AI 结合仓库上下文分析
- 对话历史持久化，切换仓库后可回到之前的对话
- 预设快捷问题（分析完成后推荐 3-5 个有价值的深入问题）

### 2.6 模块五：文件浏览器

**功能描述**：内嵌的代码阅读器，支持在不离开页面的情况下查看源码。

- 目录树导航（带文件类型图标）
- 代码语法高亮
- AI 注释层：在关键代码行旁显示 AI 生成的行内注释
- 与对话联动：选中代码段 → 右键 "Ask AI about this"
- 文件重要度标记（核心文件 / 配置文件 / 测试文件 / 可忽略文件）

---

## 三、系统架构设计

### 3.1 整体架构

```
                         ┌──────────────┐
                         │   Nginx /    │
                         │   Caddy      │
                         │  (反向代理)   │
                         └──────┬───────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
         ┌──────▼──────┐ ┌─────▼─────┐ ┌──────▼──────┐
         │  Next.js     │ │  FastAPI   │ │  FastAPI    │
         │  前端 SSR    │ │  主服务     │ │  Worker     │
         │  (Vercel)    │ │  (API)     │ │  (分析任务)  │
         └─────────────┘ └─────┬─────┘ └──────┬──────┘
                               │               │
                    ┌──────────┼──────────┐    │
                    │          │          │    │
              ┌─────▼───┐ ┌───▼───┐ ┌───▼────▼──┐
              │ PostgreSQL│ │ Redis │ │  Qdrant   │
              │ (元数据)  │ │(缓存   │ │  (向量DB) │
              │          │ │ 队列)  │ │           │
              └──────────┘ └───────┘ └───────────┘
                                          │
                               ┌──────────┘
                               │
                        ┌──────▼──────┐
                        │  对象存储    │
                        │  (S3/MinIO) │
                        │  克隆的仓库  │
                        └─────────────┘
```

### 3.2 核心组件说明

#### 3.2.1 前端（Next.js + React）

| 组件 | 技术选型 | 说明 |
|------|---------|------|
| 框架 | Next.js 14+ (App Router) | SSR + CSR 混合渲染 |
| 流程图渲染 | React Flow | 交互式节点图，支持缩放/拖拽/事件 |
| 代码高亮 | Shiki / Prism | 多语言语法高亮 |
| 状态管理 | Zustand | 轻量，适合中型应用 |
| 实时通信 | SSE (EventSource) | AI 对话流式输出 |
| WebSocket | Socket.io | 分析进度实时推送 |
| UI 组件库 | shadcn/ui + Tailwind | 现代化设计系统 |
| Markdown 渲染 | react-markdown | AI 回答中的 Markdown |

#### 3.2.2 后端主服务（FastAPI）

职责：接收请求、鉴权、调度任务、提供 API。

**核心 API 设计**：

```
POST   /api/v1/repos/analyze          # 提交分析任务
GET    /api/v1/repos/{id}/status       # 查询分析进度
GET    /api/v1/repos/{id}/report       # 获取分析报告
GET    /api/v1/repos/{id}/diagrams     # 获取流程图数据
GET    /api/v1/repos/{id}/files        # 获取文件树
GET    /api/v1/repos/{id}/files/{path} # 获取单文件内容
POST   /api/v1/repos/{id}/chat         # 对话（SSE 流式）
GET    /api/v1/repos/{id}/chat/history # 对话历史
POST   /api/v1/auth/github             # GitHub OAuth
GET    /api/v1/user/repos              # 用户分析历史
DELETE /api/v1/repos/{id}              # 删除分析记录
```

#### 3.2.3 分析 Worker（Celery / ARQ）

职责：异步执行耗时的分析任务，与主服务解耦。

**任务流水线**：

```
任务1: repo_fetch
  ├─ 调用 GitHub API 获取元信息
  ├─ 智能判断克隆策略 (shallow clone / sparse checkout / full clone)
  └─ 输出: 仓库文件到本地磁盘或对象存储

任务2: code_index
  ├─ 文件筛选 (忽略 node_modules, .git, vendor, dist, 二进制文件)
  ├─ AST 解析 (tree-sitter) → 提取函数、类、模块边界
  ├─ 代码切片 (按语义边界, 非固定 token)
  ├─ 生成 Embedding (text-embedding-3-small 或 开源模型)
  └─ 输出: 向量存入 Qdrant, 元数据存入 PostgreSQL

任务3: ai_analysis
  ├─ 阶段1: 文件级摘要 (每个关键文件生成 summary)
  ├─ 阶段2: 模块级摘要 (聚合文件摘要 → 模块职责)
  ├─ 阶段3: 项目级摘要 (聚合模块摘要 → 全局架构)
  ├─ 阶段4: 质量扫描 (Bug / 安全 / 性能)
  └─ 输出: 结构化分析报告 (JSON)

任务4: diagram_gen
  ├─ 基于分析报告生成 Mermaid/JSON 图数据
  ├─ 语法校验 → 失败则带错误信息重试 (最多 3 次)
  └─ 输出: 多层级图数据 (顶层架构 + 模块细节 + 调用链)
```

#### 3.2.4 存储层

| 存储 | 用途 | 说明 |
|------|------|------|
| PostgreSQL | 用户信息、仓库元数据、分析报告、对话历史 | 主数据库 |
| Redis | 任务队列、分析结果缓存、会话缓存、限流计数 | 热数据层 |
| Qdrant | 代码 Embedding 向量 | 对话时检索相关代码 |
| S3 / MinIO | 克隆的仓库文件、生成的图片 | 大文件存储 |

### 3.3 数据模型设计

```sql
-- 用户表
CREATE TABLE users (
    id            UUID PRIMARY KEY,
    github_id     BIGINT UNIQUE,
    username      VARCHAR(255),
    email         VARCHAR(255),
    avatar_url    TEXT,
    access_token  TEXT,          -- GitHub OAuth token (加密存储)
    plan          VARCHAR(20) DEFAULT 'free',  -- free / pro / team
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- 仓库分析记录
CREATE TABLE repo_analyses (
    id            UUID PRIMARY KEY,
    user_id       UUID REFERENCES users(id),
    repo_url      TEXT NOT NULL,
    repo_owner    VARCHAR(255),
    repo_name     VARCHAR(255),
    branch        VARCHAR(255) DEFAULT 'main',
    commit_sha    VARCHAR(40),       -- 分析时的 commit
    status        VARCHAR(20),       -- pending / fetching / indexing / analyzing / done / failed
    report        JSONB,             -- 结构化分析结果
    diagrams      JSONB,             -- 流程图数据
    file_tree     JSONB,             -- 目录树
    language_stats JSONB,            -- 语言分布
    error_message TEXT,
    started_at    TIMESTAMPTZ,
    completed_at  TIMESTAMPTZ,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- 对话记录
CREATE TABLE chat_sessions (
    id            UUID PRIMARY KEY,
    repo_analysis_id UUID REFERENCES repo_analyses(id),
    user_id       UUID REFERENCES users(id),
    title         VARCHAR(255),
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    updated_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE chat_messages (
    id            UUID PRIMARY KEY,
    session_id    UUID REFERENCES chat_sessions(id),
    role          VARCHAR(20),       -- user / assistant
    content       TEXT,
    referenced_files JSONB,          -- 对话中引用的文件路径
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- 代码片段索引 (元数据, 向量在 Qdrant)
CREATE TABLE code_chunks (
    id              UUID PRIMARY KEY,
    repo_analysis_id UUID REFERENCES repo_analyses(id),
    file_path       TEXT,
    chunk_type      VARCHAR(20),     -- function / class / module / config
    name            VARCHAR(255),    -- 函数名/类名
    start_line      INT,
    end_line        INT,
    content         TEXT,
    summary         TEXT,            -- AI 生成的摘要
    vector_id       VARCHAR(255),    -- Qdrant 中的 ID
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_repo_analyses_user ON repo_analyses(user_id);
CREATE INDEX idx_repo_analyses_url ON repo_analyses(repo_url, commit_sha);
CREATE INDEX idx_chat_sessions_repo ON chat_sessions(repo_analysis_id);
CREATE INDEX idx_chat_messages_session ON chat_messages(session_id);
CREATE INDEX idx_code_chunks_repo ON code_chunks(repo_analysis_id);
CREATE INDEX idx_code_chunks_file ON code_chunks(repo_analysis_id, file_path);
```

---

## 四、核心流程详解

### 4.1 仓库抓取与预处理流程

```
输入: GitHub URL
      │
      ▼
┌─ URL 解析与校验 ─┐
│ 提取 owner/repo   │
│ 校验 URL 格式     │
│ 检查缓存 (同 repo │
│ + 同 commit 可复用)│
└────────┬─────────┘
         │
         ▼ (缓存未命中)
┌─ GitHub API 调取 ──────────────────┐
│ GET /repos/{owner}/{repo}           │
│ → 元信息: description, stars,       │
│   language, default_branch, size    │
│ GET /repos/{owner}/{repo}/git/trees │
│   /{branch}?recursive=1            │
│ → 完整目录树                         │
│ GET /repos/{owner}/{repo}/languages │
│ → 语言分布                           │
└────────┬───────────────────────────┘
         │
         ▼
┌─ 智能克隆策略决策 ─────────────────┐
│ if repo_size < 50MB:               │
│   → shallow clone (depth=1)        │
│ elif repo_size < 200MB:            │
│   → sparse checkout (只拉关键目录)  │
│ else:                              │
│   → API 逐文件拉取 (只拉关键文件)   │
└────────┬───────────────────────────┘
         │
         ▼
┌─ 文件筛选与分级 ───────────────────┐
│ 排除 (Tier 0 - 忽略):              │
│   .git, node_modules, vendor,      │
│   dist, build, __pycache__,        │
│   *.min.js, *.map, *.lock,        │
│   二进制文件, 图片, 字体            │
│                                    │
│ 优先 (Tier 1 - 必分析):            │
│   README, 入口文件, 配置文件,       │
│   路由定义, 数据模型, Dockerfile,   │
│   CI/CD 配置                       │
│                                    │
│ 次优先 (Tier 2 - 按需分析):        │
│   业务逻辑文件, 工具类, 中间件      │
│                                    │
│ 低优先 (Tier 3 - 摘要即可):        │
│   测试文件, 文档文件, 示例代码      │
└────────┬───────────────────────────┘
         │
         ▼
输出: 结构化仓库数据包
      - 目录树 (带分级标记)
      - 关键文件内容
      - 依赖清单
      - 仓库元信息
```

### 4.2 分层摘要策略（核心算法）

这是解决"大仓库超出上下文窗口"的关键设计。

```
Layer 1: 文件级摘要
  ┌───────────────────────────────┐
  │ 对每个 Tier 1/2 文件:          │
  │ → LLM 生成 100-300 字摘要      │
  │ → 提取: 文件职责、暴露的接口、  │
  │   依赖的其他模块、关键逻辑      │
  │                               │
  │ 并行处理, 每批 5-10 个文件      │
  │ Token 预算: ~2000 tokens/file │
  └───────────────┬───────────────┘
                  │
                  ▼
Layer 2: 模块级摘要
  ┌───────────────────────────────┐
  │ 按目录/逻辑分组聚合文件摘要:    │
  │ → 每个模块: 聚合其下所有文件摘要│
  │ → LLM 生成模块职责、对外接口、  │
  │   与其他模块的关系             │
  │                               │
  │ Token 预算: ~3000 tokens/模块  │
  └───────────────┬───────────────┘
                  │
                  ▼
Layer 3: 项目级摘要
  ┌───────────────────────────────┐
  │ 输入: 所有模块摘要 + 元信息     │
  │ → LLM 生成:                   │
  │   - 项目整体架构描述           │
  │   - 核心数据流                 │
  │   - 设计模式识别               │
  │   - 技术决策分析               │
  │                               │
  │ Token 预算: ~5000 tokens      │
  └───────────────┬───────────────┘
                  │
                  ▼
流程图生成基于 Layer 2 + Layer 3
对话 RAG 基于 Layer 1 + 原始代码
```

### 4.3 对话 RAG 检索策略

```
用户提问
    │
    ▼
┌─ 查询理解 ─────────────────────┐
│ LLM 将自然语言问题转化为:        │
│ 1. 搜索关键词 (用于 BM25)       │
│ 2. 语义查询 (用于向量检索)       │
│ 3. 精确标识符 (函数名/类名/路径) │
└────────┬───────────────────────┘
         │
         ▼
┌─ 三路并行检索 ─────────────────┐
│                                │
│  路径A: 精确匹配               │
│  → 文件路径 / 函数名精确搜索    │
│  → PostgreSQL LIKE 查询        │
│  → 权重: 0.5                   │
│                                │
│  路径B: 向量语义检索            │
│  → Qdrant 近邻搜索             │
│  → top_k=10                    │
│  → 权重: 0.3                   │
│                                │
│  路径C: 关键词检索 (BM25)       │
│  → 全文搜索                    │
│  → 权重: 0.2                   │
│                                │
└────────┬───────────────────────┘
         │
         ▼
┌─ 混合排序 (RRF) ──────────────┐
│ Reciprocal Rank Fusion          │
│ 合并三路结果, 去重, 重排序       │
│ → 取 top 5 代码片段             │
└────────┬───────────────────────┘
         │
         ▼
┌─ 上下文组装 ──────────────────┐
│ System Prompt:                 │
│   - 项目摘要 (Layer 3)         │
│   - 相关模块摘要 (Layer 2)     │
│                                │
│ Context:                       │
│   - 检索到的 5 个代码片段       │
│   - 每个片段附带文件路径/行号   │
│                                │
│ Chat History:                  │
│   - 最近 10 轮对话              │
└────────┬───────────────────────┘
         │
         ▼
  LLM 生成回答 (流式输出)
```

---

## 五、查缺补漏：初版分析遗漏的关键点

以下是在第一轮讨论中未覆盖但对产品成败至关重要的补充项。

### 5.1 安全性设计

| 风险 | 说明 | 应对措施 |
|------|------|---------|
| 恶意仓库 | 用户提交包含恶意代码的仓库 URL | 沙箱环境执行克隆；永远不执行仓库中的任何代码；文件大小/数量上限 |
| Prompt 注入 | 仓库代码中嵌入 prompt injection 指令 | 代码内容作为 user message 而非 system prompt；添加指令隔离标记 |
| GitHub Token 泄露 | OAuth token 被窃取 | AES-256 加密存储；最小权限 scope（repo:read）；token 定期轮换 |
| 信息泄露 | 分析结果包含敏感信息（API key 等） | 分析前扫描并遮蔽可能的密钥/密码 |
| DDoS / 滥用 | 大量提交分析请求 | 用户级 Rate Limit；IP 级限流；队列优先级 |

### 5.2 Private 仓库支持

```
用户点击 "分析 Private 仓库"
      │
      ▼
GitHub OAuth 授权流程
  → scope: repo (读取 private 仓库)
  → 回调获取 access_token
  → 加密存入数据库
      │
      ▼
使用用户 token 克隆仓库
  → git clone https://{token}@github.com/{owner}/{repo}.git
  → 分析完成后立即删除本地克隆文件
  → 向量数据标记为 private，仅该用户可访问
```

### 5.3 多语言代码解析支持

不同编程语言需要不同的 AST 解析策略：

| 语言 | AST 解析器 | 入口文件识别 | 依赖提取 |
|------|-----------|-------------|---------|
| Python | tree-sitter-python | main.py, app.py, manage.py | requirements.txt, pyproject.toml, setup.py |
| JavaScript/TS | tree-sitter-javascript/typescript | index.js, main.ts, app.ts | package.json |
| Go | tree-sitter-go | main.go, cmd/ | go.mod |
| Java | tree-sitter-java | *Application.java, Main.java | pom.xml, build.gradle |
| Rust | tree-sitter-rust | main.rs, lib.rs | Cargo.toml |
| C/C++ | tree-sitter-c/cpp | main.c, main.cpp | CMakeLists.txt, Makefile |
| Ruby | tree-sitter-ruby | app.rb, config.ru | Gemfile |
| PHP | tree-sitter-php | index.php, artisan | composer.json |

MVP 阶段优先支持 Python、JavaScript/TypeScript、Go 三种语言。

### 5.4 Monorepo 处理

大型 monorepo（如 turborepo、nx、lerna）需要特殊处理：

- 检测 monorepo 标志文件（lerna.json, turbo.json, pnpm-workspace.yaml, nx.json）
- 先列出所有子包/子项目，让用户选择分析范围
- 每个子项目独立分析，再生成跨项目依赖关系图
- 共享模块（shared/common）标记为关联分析

### 5.5 增量更新机制

同一仓库有新 commit 时，不应重新全量分析：

```
检测到新 commit
      │
      ▼
git diff {old_sha}..{new_sha} --name-only
      │
      ▼
识别变更文件
      │
      ├─ 新增文件 → 生成摘要 + 向量化
      ├─ 修改文件 → 重新生成摘要 + 更新向量
      ├─ 删除文件 → 移除摘要 + 删除向量
      │
      ▼
判断是否需要重新生成模块/项目级摘要
  → 如果变更文件 < 10% → 只更新受影响模块摘要
  → 如果变更文件 > 10% → 全量重新分析
      │
      ▼
重新生成受影响的流程图节点
```

### 5.6 成本控制与缓存策略

| 策略 | 实施方式 |
|------|---------|
| 结果缓存 | 同一 repo + 同一 commit SHA → 直接返回缓存结果 |
| 分层 LLM | 文件摘要用廉价模型（Haiku/mini），项目分析用强模型（Sonnet/GPT-4o） |
| Token 预算 | 每个分析任务设 token 上限，超出时优雅降级 |
| 用户配额 | Free: 5 次/月, Pro: 100 次/月, Team: 无限 |
| 异步批处理 | 文件摘要批量并行处理，减少 API 调用次数 |
| Embedding 缓存 | 相同代码片段的 embedding 缓存 24h |

### 5.7 错误处理与降级策略

| 故障场景 | 降级方案 |
|---------|---------|
| GitHub API 限流 (5000 req/h) | 队列等待 + 用户提示预计时间 |
| LLM API 超时 | 重试 3 次，间隔 2/4/8 秒；失败则返回部分结果 |
| 向量数据库不可用 | 对话退化为"仅用项目摘要"模式（无精确代码检索） |
| 流程图生成语法错误 | 带错误信息重试 3 次；最终失败则返回纯文本架构描述 |
| 克隆超时 | 切换为 API 逐文件获取模式 |
| Worker 崩溃 | 任务自动重入队列，标记重试次数，3 次后标记 failed |

### 5.8 可观测性与监控

- 每个分析任务的全链路 Trace（OpenTelemetry）
- 关键指标 Dashboard：
  - 分析成功率 / 平均耗时 / P95 耗时
  - LLM token 消耗 / 成本
  - 对话满意度（用户评分）
  - 流程图生成成功率
- 告警规则：
  - 分析失败率 > 5% → 告警
  - LLM 延迟 P95 > 30s → 告警
  - 日 Token 消耗超预算 → 告警

---

## 六、技术选型汇总

| 类别 | 选型 | 备选 | 选择理由 |
|------|------|------|---------|
| 前端框架 | Next.js 14 | Nuxt, Remix | SSR + App Router + Vercel 一键部署 |
| 流程图 | React Flow | Mermaid, D3 | 原生交互、节点事件、自定义渲染 |
| 后端框架 | FastAPI | Flask, Django | 异步原生、类型安全、你已熟悉 |
| 任务队列 | ARQ (Redis-based) | Celery | 轻量、纯 Python async、Redis 复用 |
| 主数据库 | PostgreSQL 16 | MySQL | JSONB 支持、全文搜索、生态成熟 |
| 缓存 | Redis 7 | - | 队列 + 缓存 + 限流多用途 |
| 向量数据库 | Qdrant | Chroma, Pinecone | 自托管、性能好、filter 能力强 |
| 代码解析 | tree-sitter | AST 库 | 多语言统一接口、增量解析 |
| Embedding | text-embedding-3-small | BGE, Cohere | 成本低、效果够用 |
| LLM (摘要) | Claude Haiku / GPT-4o-mini | - | 低成本、速度快 |
| LLM (分析/对话) | Claude Sonnet / GPT-4o | - | 代码理解能力强 |
| 对象存储 | MinIO (自建) / S3 | - | 存储克隆仓库 |
| 部署 | Docker Compose → K8s | - | 初期 Compose，规模化后迁移 K8s |
| CI/CD | GitHub Actions | - | 与 GitHub 生态一致 |
| 监控 | Grafana + Prometheus | - | 开源标准方案 |
| 链路追踪 | OpenTelemetry | - | 全链路 trace |

---

## 七、MVP 开发路线图

### Phase 1: 核心验证（4 周）

**目标**：验证"输入 URL → 生成分析 + 流程图"的核心体验。

- Week 1-2:
  - 后端: GitHub API 集成 + 仓库克隆 + 文件筛选
  - 后端: 基础分析 Pipeline（单层摘要，不做分层）
  - 后端: Mermaid 流程图生成 + 语法校验重试
- Week 3:
  - 前端: URL 输入 + 分析进度展示
  - 前端: React Flow 渲染流程图（静态展示）
  - 前端: 分析报告展示页
- Week 4:
  - 联调、Bug 修复
  - 部署到测试环境
  - 内测 5-10 个真实仓库验证效果

**Phase 1 简化决策**：
- 不做用户系统，匿名使用
- 不做 Private 仓库支持
- 不做向量化，对话用"摘要塞 prompt"方式
- 只支持 Python / JavaScript

### Phase 2: 对话能力（3 周）

**目标**：加入 AI 对话功能，可以追问代码细节。

- Week 5:
  - 后端: 代码切片 + tree-sitter 解析
  - 后端: Qdrant 集成 + Embedding 生成
- Week 6:
  - 后端: RAG 对话 API (SSE 流式)
  - 后端: 混合检索（向量 + BM25 + 精确匹配）
- Week 7:
  - 前端: 对话面板 UI
  - 前端: 流程图节点 ↔ 对话联动
  - 对话质量调优

### Phase 3: 体验完善（3 周）

**目标**：可对外发布的完整产品。

- Week 8:
  - 用户系统（GitHub OAuth 登录）
  - 分析历史管理
  - Private 仓库支持
- Week 9:
  - 文件浏览器
  - 流程图交互增强（钻取、搜索、导出）
  - 增量更新
- Week 10:
  - 性能优化 + 缓存策略
  - 错误处理完善
  - 部署到生产环境
  - Landing Page

### Phase 4: 增长与商业化（持续）

- 付费计划 (Pro / Team)
- 支持更多语言 (Go, Java, Rust)
- Monorepo 支持
- VS Code 插件
- API 开放（供其他工具集成）
- 团队协作（共享分析、协同标注）

---

## 八、商业化策略

### 8.1 定价模型

| Plan | 价格 | 额度 | 功能 |
|------|------|------|------|
| Free | $0 | 5 次分析/月, 20 条对话/天 | Public 仓库, 基础流程图 |
| Pro | $19/月 | 100 次分析/月, 无限对话 | Private 仓库, 高级流程图, 增量更新, 文件浏览器 |
| Team | $49/人/月 | 无限分析, 无限对话 | 协作, 共享分析, API 访问, 优先队列 |
| Enterprise | 定制 | 定制 | 自部署, SSO, 审计日志, SLA |

### 8.2 成本估算（单次分析）

| 项目 | 估算 | 说明 |
|------|------|------|
| GitHub API 调用 | ~20 次 | 元信息 + 文件树 + 文件内容 |
| LLM 文件摘要 | ~50K input tokens | 假设 30 个关键文件 |
| LLM 项目分析 | ~20K input tokens | 模块摘要聚合 |
| LLM 流程图生成 | ~10K input tokens | 含重试 |
| Embedding 生成 | ~100K tokens | 全部代码片段 |
| 合计 Token 成本 | ~$0.05 - $0.15 | 取决于模型选择 |
| 对话成本 | ~$0.01/轮 | 检索 + LLM |

Free 用户 5 次/月 → 成本 $0.25-0.75/用户/月，可承受。

---

## 九、风险与应对

| 风险 | 等级 | 应对 |
|------|------|------|
| LLM 分析质量不稳定 | 高 | 多轮校验 + 人工评测集 + 分语言优化 prompt |
| 大仓库分析耗时长 | 高 | 渐进式展示（先出摘要，再出流程图）+ 异步通知 |
| GitHub API 限流 | 中 | 多 Token 轮换 + 缓存 + 本地 git 操作替代 API |
| 流程图可读性差 | 中 | 限制单图节点数 < 20 + 分层钻取 + 布局算法优化 |
| 竞品追赶（已有类似产品） | 中 | 差异化: 对话深度 + 流程图交互 + 垂直场景优化 |
| 用户留存难 | 中 | 分析历史 + 增量更新 + 对话持久化 → 持续回访价值 |

---

## 十、竞品参考

| 产品 | 做了什么 | 没做什么 | 我们的差异化 |
|------|---------|---------|------------|
| GitHub Copilot Chat | 单文件级对话 | 全局架构分析、流程图 | 仓库全局理解 + 可视化 |
| Sourcegraph Cody | 代码搜索 + 对话 | 架构可视化 | 交互式流程图 |
| CodeSee | 代码可视化地图 | AI 对话、Bug 分析 | AI 深度分析 + 对话 |
| Bloop (已关) | 代码搜索 + AI | 架构图 | 完整 pipeline |
| ChatGPT + 手动粘贴 | 回答代码问题 | 全仓库理解、可视化 | 自动化 + 全局上下文 |

核心差异化：**分析 + 可视化 + 对话三位一体**，市面上没有一个产品同时做好这三点。

---

## 附录 A: 关键 Prompt 模板

### A.1 项目分析 Prompt

```
你是一个资深软件架构师。请分析以下代码仓库，并输出结构化的 JSON 报告。

## 仓库信息
- 名称: {repo_name}
- 语言分布: {languages}
- 目录结构:
{file_tree}

## 关键文件摘要
{file_summaries}

## 依赖列表
{dependencies}

请输出以下 JSON 格式的分析报告:
{
  "project_type": "Web App | CLI | Library | ...",
  "description": "一句话描述这个项目做什么",
  "tech_stack": {
    "language": "...",
    "framework": "...",
    "database": "...",
    "others": ["..."]
  },
  "architecture": {
    "pattern": "MVC | Event-driven | ...",
    "modules": [
      {
        "name": "模块名",
        "responsibility": "职责描述",
        "key_files": ["file1.py", "file2.py"],
        "dependencies": ["其他模块名"]
      }
    ]
  },
  "data_flow": "描述数据从输入到输出的主要流程",
  "entry_points": ["main.py", "app.py"],
  "potential_issues": [
    {
      "type": "bug | security | performance",
      "severity": "high | medium | low",
      "file": "file.py",
      "line": 42,
      "description": "问题描述"
    }
  ]
}
```

### A.2 流程图生成 Prompt

```
基于以下项目分析报告，生成一个 Mermaid 格式的系统架构图。

## 分析报告
{analysis_report}

要求:
1. 使用 graph TD (自上而下) 布局
2. 每个模块作为一个节点，标注模块名和核心职责
3. 用箭头表示模块间的依赖/调用关系，箭头上标注交互方式
4. 外部依赖 (数据库、API、消息队列) 用不同样式的节点
5. 节点数量控制在 8-15 个之间，保持图的可读性
6. 只输出 Mermaid 代码，不要其他文字

输出:
```

### A.3 对话 System Prompt

```
你是 RepoLens AI 助手，专门帮助开发者理解和讨论 GitHub 代码仓库。

## 你正在分析的项目
{project_summary}

## 项目架构
{architecture_summary}

## 当前上下文中的代码片段
{retrieved_code_chunks}

## 你的行为准则
1. 始终基于实际代码内容回答，不要编造不存在的代码
2. 引用代码时标注文件路径和行号
3. 如果问题超出你看到的代码范围，明确告知并建议查看哪些文件
4. 发现潜在 Bug 时主动指出，并给出修复建议
5. 回答时兼顾"是什么"和"为什么这样设计"
6. 代码示例使用项目实际的编程语言和风格
```

---

## 附录 B: 与 OpenClaw 框架的结合点

RepoLens 的分析 Pipeline 天然适合 OpenClaw 的 Planner/Executor/Verifier 架构：

| OpenClaw 角色 | RepoLens 中的应用 |
|--------------|------------------|
| Planner | 接收 GitHub URL，分析仓库规模和语言，制定分析策略（全量/增量、分层深度、优先分析哪些模块） |
| Executor | 执行具体任务: 克隆仓库、文件摘要、模块分析、流程图生成、RAG 检索 |
| Verifier | 校验分析结果质量: 流程图语法是否正确、摘要是否覆盖关键模块、分析是否自洽 |

**具体集成方案**：RepoLens 的 Worker 本身就可以是一个 OpenClaw Agent 实例。Planner 动态调整分析粒度（小项目一次全量分析，大项目分阶段执行），Executor 可并行执行文件摘要等可并行任务，Verifier 在每个阶段输出后校验质量，不合格则让 Executor 重做。

这既是 RepoLens 的技术实现，也是 OpenClaw 框架的一个真实落地 showcase。
