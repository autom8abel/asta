from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.db import crud, session
from backend.api import schemas

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello from ASTA MVP"}

# ---------------- User endpoints ----------------
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(session.get_db)):
    # Prevent duplicate usernames
    existing = crud.get_user_by_username(db, user.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    return crud.create_user(db, username=user.username)

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(session.get_db)):
    db_user = crud.get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(session.get_db)):
    return crud.get_users(db, skip=skip, limit=limit)

# ---------------- Task endpoints ----------------
@app.post("/tasks/", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(session.get_db)):
    # If an owner is specified, ensure the user exists
    if task.user_id is not None and not crud.get_user(db, task.user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return crud.create_task(db=db, title=task.title, description=task.description, due_date=task.due_date, user_id=task.user_id)

@app.get("/tasks/", response_model=list[schemas.Task])
def read_tasks(skip: int = 0, limit: int = 10, db: Session = Depends(session.get_db)):
    return crud.get_tasks(db=db, skip=skip, limit=limit)

@app.get("/users/{user_id}/tasks", response_model=list[schemas.Task])
def read_user_tasks(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(session.get_db)):
    if not crud.get_user(db, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return crud.get_tasks_for_user(db=db, user_id=user_id, skip=skip, limit=limit)
