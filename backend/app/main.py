"""
RepoLens - GitHub Repository AI Analyzer
FastAPI 应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-powered GitHub repository analyzer with architecture visualization",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载路由
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}
