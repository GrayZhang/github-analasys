"""
主路由聚合
"""
from fastapi import APIRouter
from app.api.endpoints import repos, analyze, chat

api_router = APIRouter()
api_router.include_router(repos.router, prefix="/repos", tags=["repos"])
api_router.include_router(analyze.router, prefix="/repos", tags=["analyze"])
api_router.include_router(chat.router, prefix="/repos", tags=["chat"])
