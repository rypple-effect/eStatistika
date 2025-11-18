from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.models import Chat, Message


class ChatManager:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_chat(self, user_id: int) -> Chat:
        chat = Chat(id=str(uuid4()), user_id=user_id)
        self.db.add(chat)
        await self.db.commit()
        await self.db.refresh(chat)
        return chat

    async def get_chat(self, chat_id: str) -> Optional[Chat]:
        result = await self.db.execute(select(Chat).where(Chat.id == chat_id))
        return result.scalar_one_or_none()

    async def get_user_chats(self, user_id: int) -> list[Chat]:
        result = await self.db.execute(
            select(Chat).where(Chat.user_id == user_id).order_by(Chat.updated_at.desc())
        )
        return list(result.scalars().all())

    async def delete_chat(self, chat_id: str) -> bool:
        chat = await self.get_chat(chat_id)
        if chat:
            # Delete messages first (due to foreign key constraint)
            await self.db.execute(delete(Message).where(Message.chat_id == chat_id))
            # Then delete the chat
            await self.db.execute(delete(Chat).where(Chat.id == chat_id))
            await self.db.commit()
            return True
        return False

    async def add_message(self, chat_id: str, role: str, content: str) -> Message:
        message = Message(chat_id=chat_id, role=role, content=content)
        self.db.add(message)

        chat = await self.get_chat(chat_id)
        if chat:
            chat.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def get_chat_messages(self, chat_id: str) -> list[Message]:
        result = await self.db.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at)
        )
        return list(result.scalars().all())
