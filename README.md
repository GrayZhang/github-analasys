# RepoLens

> 输入一个 GitHub 仓库 URL，AI 自动读懂整个项目，生成交互式架构流程图，并提供持续对话能力深挖代码实现。

## 技术栈

### 后端
- **框架**: FastAPI
- **数据库**: PostgreSQL 16
- **缓存/队列**: Redis 7
- **向量数据库**: Qdrant
- **任务队列**: ARQ (Redis-based)
- **代码解析**: tree-sitter

### 前端
- **框架**: Next.js 14 (App Router)
- **UI**: shadcn/ui + Tailwind CSS
- **流程图**: React Flow
- **状态管理**: Zustand
- **实时通信**: SSE (EventSource) / WebSocket

## 快速开始

### 安装依赖

```bash
# 后端
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 前端
cd frontend
npm install
```

### 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入必要配置
```

### 启动服务

```bash
# 后端
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 前端
cd frontend && npm run dev
```

## 项目结构

```
github-analasys/
├── backend/                # FastAPI 后端
│   ├── app/
│   │   ├── main.py        # 应用入口
│   │   ├── api/           # API 路由
│   │   ├── core/          # 核心模块
│   │   ├── models/        # 数据模型
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # 业务逻辑
│   │   └── workers/       # 异步任务
│   └── requirements.txt
├── frontend/              # Next.js 前端
│   ├── src/
│   │   ├── app/           # App Router
│   │   ├── components/    # 组件
│   │   ├── hooks/         # Hooks
│   │   ├── lib/           # 工具函数
│   │   └── stores/        # Zustand stores
│   ├── public/
│   ├── package.json
│   └── tailwind.config.ts
├── docs/                  # 产品文档
├── docker-compose.yml
└── README.md
```

## 开发路线图

- [x] Phase 1: 核心验证（MVP）
- [ ] Phase 2: 对话能力（RAG）
- [ ] Phase 3: 体验完善（用户系统、Private 仓库）
- [ ] Phase 4: 增长与商业化

## License

MIT
