from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ModuleBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    difficulty_level: Optional[str] = None
    duration_minutes: Optional[int] = None
    prerequisites: Optional[List[str]] = []
    learning_outcomes: Optional[List[str]] = []
    content_url: Optional[str] = None

class ModuleCreate(ModuleBase):
    pass

class ModuleUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    difficulty_level: Optional[str] = None
    duration_minutes: Optional[int] = None
    prerequisites: Optional[List[str]] = None
    learning_outcomes: Optional[List[str]] = None
    content_url: Optional[str] = None
    is_published: Optional[bool] = None

class ModuleResponse(ModuleBase):
    id: int
    is_published: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
