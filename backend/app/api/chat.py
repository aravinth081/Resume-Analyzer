"""
AI Chat Assistant API routes.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict
from pydantic import BaseModel

from app.database import get_db
from app.services.chat_service import chat, get_chat_history
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/chat", tags=["AI Chat Assistant"])


class ChatMessageRequest(BaseModel):
    message: str


@router.post("/message")
async def send_message(
    data: ChatMessageRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a message to the AI Career Copilot and get a response."""
    return await chat(data.message, user, db)


@router.get("/history")
async def history(
    limit: int = 50,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get recent chat history."""
    return await get_chat_history(user, db, limit)
