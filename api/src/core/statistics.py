from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.models import StatisticsRequest


class StatisticsManager:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_statistics_request(
        self, user_id: int, request_info: str, response: str, source: str
    ) -> StatisticsRequest:
        stats_request = StatisticsRequest(
            user_id=user_id,
            request_info=request_info,
            response=response,
            source=source,
        )
        self.db.add(stats_request)
        await self.db.commit()
        await self.db.refresh(stats_request)
        return stats_request

    async def get_statistics_request(self, request_id: int) -> Optional[StatisticsRequest]:
        result = await self.db.execute(
            select(StatisticsRequest).where(StatisticsRequest.id == request_id)
        )
        return result.scalar_one_or_none()

    async def get_user_statistics_requests(self, user_id: int) -> list[StatisticsRequest]:
        result = await self.db.execute(
            select(StatisticsRequest)
            .where(StatisticsRequest.user_id == user_id)
            .order_by(StatisticsRequest.created_at.desc())
        )
        return list(result.scalars().all())

