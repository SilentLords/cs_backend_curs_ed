from fastapi import HTTPException
from pydantic import BaseModel, Field
from typing import TypeVar, Optional, List, Union, Dict, Any

# from fastapi import Response
from fastapi import Response

T = TypeVar('T')


class Content(BaseModel):
    message: str = Field(..., description='Response message')
    result: Optional[T] = None


class CommonResponse(Response):
    media_type = 'application/json'
    content: Content


class CommonHTTPException(HTTPException):
    detail: Content


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class Statistic(BaseModel):
    nickname: str | None = None
    rating_rang: int = 0
    matches_per_month: int = 0
    matches_win_per_month: int = 0
    matches_per_all_month: int = 0
    win_rate: float = 0
    faceit_points: float = 0
    longest_win_streak: int = 0
    hs_percent: float = 0
    k_r_avg_segments: float = 0
    k_d_avg_segments: float = 0


class UserBase(BaseModel):
    nickname: str | None = None


class User(UserBase):
    id: int | None = None
    stats: Statistic | None = None

    class Config:
        orm_mode = True
