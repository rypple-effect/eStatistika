from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database.database import get_db
from ..database.models import Session, User

security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    token = credentials.credentials
    result = await db.execute(
        select(Session).where(Session.id == token).options(selectinload(Session.user))
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=401, detail="Invalid token")

    if session.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Token expired")

    return session.user
