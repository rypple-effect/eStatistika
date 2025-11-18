"""
Chat History Service

Handles all chat history operations including:
- Retrieving chat message history
- Adding messages to chat history
- Formatting messages for AI context
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.chats import ChatManager
from ..database.models import Message


class ChatHistoryService:
    """Service for managing chat message history"""

    def __init__(self, db: AsyncSession):
        self.chat_manager = ChatManager(db)
        self.db = db

    async def get_history(self, chat_id: str) -> list[Message]:
        """
        Retrieve all messages for a chat session.
        
        Args:
            chat_id: The chat session identifier
            
        Returns:
            List of messages ordered by creation time
        """
        return await self.chat_manager.get_chat_messages(chat_id)

    async def add_message(self, chat_id: str, role: str, content: str) -> Message:
        """
        Add a message to the chat history.
        
        Args:
            chat_id: The chat session identifier
            role: Message role ('user' or 'assistant')
            content: Message content
            
        Returns:
            The created Message object
        """
        return await self.chat_manager.add_message(chat_id, role, content)

    async def format_for_ai(self, chat_id: str) -> list[dict[str, str]]:
        """
        Format chat history for AI API consumption.
        Converts database messages to the format expected by Ollama.
        
        Args:
            chat_id: The chat session identifier
            
        Returns:
            List of message dictionaries with 'role' and 'content' keys
        """
        messages = await self.get_history(chat_id)
        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

    async def verify_chat_access(self, chat_id: str, user_id: int) -> bool:
        """
        Verify that a user has access to a chat session.
        
        Args:
            chat_id: The chat session identifier
            user_id: The user identifier
            
        Returns:
            True if user has access, False otherwise
        """
        chat = await self.chat_manager.get_chat(chat_id)
        return chat is not None and chat.user_id == user_id

