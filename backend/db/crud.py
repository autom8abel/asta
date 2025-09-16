from sqlalchemy.orm import Session
from . import models

def create_task(db: Session, title: str, description: str = None, due_date=None):
    task = models.Task(title=title, description=description, due_date=due_date)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def get_tasks(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Task).offset(skip).limit(limit).all()
