from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, Any
from datetime import datetime

T = TypeVar('T')

class MetaResponse(BaseModel):
    request_id: Optional[str] = None
    timestamp: datetime = datetime.utcnow()

class ErrorResponse(BaseModel):
    code: str
    message: str

class APIResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    meta: MetaResponse
    error: Optional[ErrorResponse] = None
