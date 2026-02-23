from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    status: str
    statusCode: int
    data: Optional[T] = None
    message: str
    errors: Optional[List[str]] = None


class APIErrorDetail(BaseModel):
    code: str
    message: str
    details: str
    timestamp: str


class APIErrorResponse(BaseModel):
    status: str
    statusCode: int
    error: APIErrorDetail
    requestId: str
