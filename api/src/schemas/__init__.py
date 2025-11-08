from datetime import datetime

from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


class ChatResponse(BaseModel):
    response: str
    model: str


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6)


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    session_id: str
    user_id: int
    username: str


class SessionResponse(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime


class ChatSessionResponse(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime


class MessageResponse(BaseModel):
    role: str
    content: str
    created_at: datetime


class StatisticsQueryRequest(BaseModel):
    query: str = Field(min_length=1, description="The statistical query or question from the user")
    source: str = Field(default="AI Generated", description="Source of the statistics")


class StatisticsResponse(BaseModel):
    id: int
    request_info: str
    response: str
    source: str
    created_at: datetime