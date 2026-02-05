from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProgressBase(BaseModel):
    user_id: int
    module_id: int
    status: str
    progress_percentage: float

class ProgressCreate(ProgressBase):
    pass

class ProgressUpdate(BaseModel):
    status: Optional[str] = None
    progress_percentage: Optional[float] = None
    time_spent_minutes: Optional[int] = None

class ProgressResponse(ProgressBase):
    id: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    time_spent_minutes: int
    created_at: datetime
    
    class Config:
        from_attributes = True
