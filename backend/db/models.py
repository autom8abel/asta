from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)

    # Relationship: a user has many tasks
    tasks = relationship("Task", back_populates="owner")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    due_date = Column(DateTime, nullable=True)
    status = Column(String, default="pending")

    # user_id is a foreign key referencing users.id; nullable=True to avoid breaking existing rows
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationship back to the owning user
    owner = relationship("User", back_populates="tasks")

