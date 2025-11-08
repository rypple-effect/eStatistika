from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.sessions import SessionManager
from ..database.database import get_db
from ..schemas import LoginRequest, LoginResponse, RegisterRequest

router = APIRouter(tags=["auth"])


@router.post("/auth/register", status_code=201)
async def register(
    request: RegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    manager = SessionManager(db)
    try:
        user = await manager.create_user(request.username, request.password)
        return {"user_id": user.id, "username": user.username}
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")


@router.post("/auth/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    manager = SessionManager(db)
    user = await manager.authenticate_user(request.username, request.password)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    session = await manager.create_session(user.id)
    return LoginResponse(session_id=session.id, user_id=user.id, username=user.username)
