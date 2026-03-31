"""
对话 API (SSE 流式)
"""
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, AsyncGenerator
import json
import asyncio

router = APIRouter()


class ChatMessage(BaseModel):
    role: str  # user / assistant
    content: str
    referenced_files: Optional[List[str]] = None


class ChatRequest(BaseModel):
    message: str
    analysis_id: str


@router.post("/{analysis_id}/chat")
async def chat(body: ChatRequest):
    """
    AI 对话 (SSE 流式)
    
    基于仓库上下文的多轮对话，支持代码解释、架构讨论、Bug 分析等
    """
    async def generate() -> AsyncGenerator[str, None]:
        # TODO: RAG 检索 → 组装上下文 → LLM 流式生成
        messages = [
            f"data: {json.dumps({'type': 'content', 'content': 'This is a placeholder response. RAG integration pending.'})}\n\n"
        ]
        for msg in messages:
            yield msg
            await asyncio.sleep(0.1)
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/{analysis_id}/chat/history")
async def get_chat_history(analysis_id: str):
    """获取对话历史"""
    # TODO: 从数据库查询对话历史
    return {"messages": []}
