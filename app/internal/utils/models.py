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
