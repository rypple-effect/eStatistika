from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.chats import ChatManager
from ..core.dependencies import get_current_user
from ..database.database import get_db
from ..database.models import User
from ..schemas import ChatSessionResponse, MessageResponse

router = APIRouter(tags=["chats"])


@router.get("/chats", response_model=list[ChatSessionResponse])
async def list_chats(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    manager = ChatManager(db)
    chats = await manager.get_user_chats(current_user.id)
    return [
        ChatSessionResponse(id=c.id, created_at=c.created_at, updated_at=c.updated_at)
        for c in chats
    ]


@router.post("/chats", response_model=ChatSessionResponse, status_code=201)
async def create_chat(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    manager = ChatManager(db)
    chat = await manager.create_chat(current_user.id)
    return ChatSessionResponse(
        id=chat.id, created_at=chat.created_at, updated_at=chat.updated_at
    )


@router.delete("/chats/{chat_id}", status_code=204)
async def delete_chat(
    chat_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    manager = ChatManager(db)
    chat = await manager.get_chat(chat_id)

    if not chat or chat.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Chat not found")

    await manager.delete_chat(chat_id)


@router.get("/chats/{chat_id}/messages", response_model=list[MessageResponse])
async def get_chat_messages(
    chat_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    manager = ChatManager(db)
    chat = await manager.get_chat(chat_id)

    if not chat or chat.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Chat not found")

    messages = await manager.get_chat_messages(chat_id)
    return [
        MessageResponse(role=m.role, content=m.content, created_at=m.created_at)
        for m in messages
    ]
