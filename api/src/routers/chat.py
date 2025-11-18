"""
Chat Router

Handles chat endpoints for AI interactions with conversation history.
Uses StatisticsService to provide well-formatted responses with statistics, sources, and dates.
Integrates StatisticsService (AI) and ChatHistoryService (history management).
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.dependencies import get_current_user
from ..database.database import get_db
from ..database.models import User
from ..schemas import ChatRequest, ChatResponse
from ..services.statistics_service import StatisticsService
from ..services.chat_history_service import ChatHistoryService

router = APIRouter(tags=["chat"])

# Initialize statistics service (singleton)
statistics_service = StatisticsService()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    chat_id: str = Query(..., description="The chat session identifier"),
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
):
    """
    Send a chat message and get AI response (non-streaming).
    Uses StatisticsService to provide well-formatted responses with statistics, sources, and dates.
    Automatically saves both user message and AI response to chat history.
    
    Args:
        request: Chat request with message and temperature
        chat_id: The chat session identifier
        current_user: Authenticated user
        db: Database session
        
    Returns:
        ChatResponse with AI response and model name
    """
    # Initialize services
    history_service = ChatHistoryService(db)

    # Verify chat access
    if not await history_service.verify_chat_access(chat_id, current_user.id):
        raise HTTPException(status_code=404, detail="Chat not found")

    # Get chat history for context
    history = await history_service.format_for_ai(chat_id)

    # Add user message to history
    await history_service.add_message(chat_id, "user", request.message)

    # Generate statistics response using StatisticsService with chat history context
    result = await statistics_service.generate_statistics(
        query=request.message,
        source="AI Generated",
        chat_history=history,
    )

    # Format response to include source and date information in a readable way
    formatted_response = result["response"]
    
    # Ensure the user's query is highlighted at the start if not already present
    query_marker = "📋 **Question:**"
    if not formatted_response.startswith(query_marker) and "Question:" not in formatted_response[:100]:
        formatted_response = f"{query_marker} {request.message}\n\n{formatted_response}"
    
    # Append source and date information if not already included in the response
    if "Source:" not in formatted_response and "source:" not in formatted_response.lower():
        formatted_response += f"\n\n---\n**Source:** {result['source']}\n**Date:** {result['date']}"

    # Save AI response to history (with source and date info)
    await history_service.add_message(chat_id, "assistant", formatted_response)

    return ChatResponse(response=formatted_response, model=result["model"])


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    chat_id: str = Query(..., description="The chat session identifier"),
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
):
    """
    Send a chat message and get streaming AI response.
    Uses StatisticsService to provide well-formatted responses with statistics, sources, and dates.
    Automatically saves both user message and AI response to chat history.
    
    Args:
        request: Chat request with message and temperature
        chat_id: The chat session identifier
        current_user: Authenticated user
        db: Database session
        
    Returns:
        StreamingResponse with AI response chunks
    """
    # Initialize services
    history_service = ChatHistoryService(db)

    # Verify chat access
    if not await history_service.verify_chat_access(chat_id, current_user.id):
        raise HTTPException(status_code=404, detail="Chat not found")

    # Get chat history for context
    history = await history_service.format_for_ai(chat_id)

    # Add user message to history
    await history_service.add_message(chat_id, "user", request.message)

    # Get streaming statistics response using StatisticsService
    stream = statistics_service.generate_statistics_stream(
        query=request.message,
        source="AI Generated",
        chat_history=history,
    )

    # Collect response for saving to history
    full_response = ""
    query_marker = "📋 **Question:**"
    query_added = False
    
    async def generate_with_history():
        nonlocal full_response, query_added
        async for chunk in stream:
            full_response += chunk
            # Check if query marker is in the response
            if query_marker in full_response or "Question:" in full_response[:200]:
                query_added = True
            yield chunk
        
        # Ensure the user's query is highlighted at the start if not already present
        if not query_added and full_response:
            query_header = f"{query_marker} {request.message}\n\n"
            full_response = query_header + full_response
            # We can't prepend to a stream, but we'll fix it when saving
        
        # Append source and date information if not already included
        if full_response and ("Source:" not in full_response and "source:" not in full_response.lower()):
            from datetime import datetime
            current_date = datetime.now().strftime("%Y-%m-%d")
            source_info = f"\n\n---\n**Source:** AI Generated\n**Date:** {current_date}"
            full_response += source_info
            yield source_info
        
        # Save complete AI response to history after streaming completes
        if full_response:
            await history_service.add_message(chat_id, "assistant", full_response)

    return StreamingResponse(
        generate_with_history(),
        media_type="text/plain",
    )

