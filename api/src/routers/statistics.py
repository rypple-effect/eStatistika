from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.chats import ChatManager
from ..core.dependencies import get_current_user
from ..core.statistics import StatisticsManager
from ..database.database import get_db
from ..database.models import User
from ..schemas import StatisticsQueryRequest, StatisticsResponse
from ..services.statistics_service import StatisticsService

router = APIRouter(tags=["statistics"])

# Initialize statistics service (singleton)
statistics_service = StatisticsService()


@router.post("/statistics", response_model=StatisticsResponse, status_code=201)
async def create_statistics_request(
    request: StatisticsQueryRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Create a statistics request. The AI will generate statistics based on the user's query.
    The response includes the date, source, and statistical information.
    Also creates a chat with messages for chat history.
    """
    try:
        # Generate statistics using AI
        ai_response = await statistics_service.generate_statistics(
            query=request.query, source=request.source
        )
        
        # Save to database
        manager = StatisticsManager(db)
        stats_request = await manager.create_statistics_request(
            user_id=current_user.id,
            request_info=request.query,
            response=ai_response["response"],
            source=ai_response["source"],
        )
        
        # Create a chat and add messages for chat history
        try:
            chat_manager = ChatManager(db)
            chat = await chat_manager.create_chat(current_user.id)
            
            # Add user's question as a message
            await chat_manager.add_message(
                chat_id=chat.id,
                role="user",
                content=request.query
            )
            
            # Add AI's response as a message
            await chat_manager.add_message(
                chat_id=chat.id,
                role="assistant",
                content=ai_response["response"]
            )
        except Exception as chat_error:
            # If chat creation fails, log but don't fail the statistics request
            # This ensures statistics requests still work even if chat creation fails
            print(f"Warning: Failed to create chat for statistics request: {chat_error}")
        
        return StatisticsResponse(
            id=stats_request.id,
            request_info=stats_request.request_info,
            response=stats_request.response,
            source=stats_request.source,
            created_at=stats_request.created_at,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating statistics: {str(e)}")


@router.get("/statistics", response_model=list[StatisticsResponse])
async def list_statistics_requests(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get all statistics requests for the current user."""
    manager = StatisticsManager(db)
    requests = await manager.get_user_statistics_requests(current_user.id)
    return [
        StatisticsResponse(
            id=r.id,
            request_info=r.request_info,
            response=r.response,
            source=r.source,
            created_at=r.created_at,
        )
        for r in requests
    ]


@router.get("/statistics/{request_id}", response_model=StatisticsResponse)
async def get_statistics_request(
    request_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a specific statistics request by ID."""
    manager = StatisticsManager(db)
    stats_request = await manager.get_statistics_request(request_id)
    
    if not stats_request or stats_request.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Statistics request not found")
    
    return StatisticsResponse(
        id=stats_request.id,
        request_info=stats_request.request_info,
        response=stats_request.response,
        source=stats_request.source,
        created_at=stats_request.created_at,
    )

