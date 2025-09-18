from sqlalchemy.orm import Session
from . import models

# ---------- Users ----------
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, username: str):
    user = models.User(username=username)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# ---------- Tasks ----------
def create_task(db: Session, title: str, description: str = None, due_date=None, user_id: int = None):
    # Create the task with optional user_id
    task = models.Task(title=title, description=description, due_date=due_date, user_id=user_id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def get_tasks(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Task).offset(skip).limit(limit).all()

def get_tasks_for_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Task).filter(models.Task.user_id == user_id).offset(skip).limit(limit).all()

# ---------- Logs ----------
def create_log(db: Session, user_id: int, event_type: str, content: str):
    log = models.Log(user_id=user_id, event_type=event_type, content=content)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

def get_logs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Log).offset(skip).limit(limit).all()

def get_logs_for_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Log).filter(models.Log.user_id == user_id).offset(skip).limit(limit).all()
