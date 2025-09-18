from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# Task schemas
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None

class TaskCreate(TaskBase):
    user_id: Optional[int] = None  # allow optional owner at create-time

class Task(TaskBase):
    id: int
    status: str
    user_id: Optional[int] = None

    class Config:
        orm_mode = True  # allow returning ORM objects directly

# User schemas
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    tasks: List[Task] = []

    class Config:
        orm_mode = True

# Log schemas
class LogBase(BaseModel):
    event_type: str
    content: str

class LogCreate(LogBase):
    user_id: int

class Log(LogBase):
    id: int
    user_id: int
    timestamp: datetime

    class Config:
        orm_mode = True

