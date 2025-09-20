from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Dict, Optional, List

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
        from_attributes = True # replaces orm_mode in Pydantic v2

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
        from_attributes = True # make Pydantic accept ORM objects

# NLP schemas
class NLPInput(BaseModel):
    text: str = Field(..., min_length=2, description="User input must not be empty")
    user_id: Optional[int] = None  # For /nlp/act

class NLPParseOutput(BaseModel):
    intent: str
    entities: Dict[str, str]

class NLPActOutput(BaseModel):
    intent: str
    entities: Dict[str, str]
    action: str
    task: Optional["Task"] = None
    tasks: Optional[List["Task"]] = None
    task_id: Optional[int] = None
    message: Optional[str] = None
    log: Optional["Log"] = None

    class Config:
        from_attributes = True
