from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from backend.db import models, crud, session
from backend.api import schemas

app = FastAPI()

# Root endpoint
@app.get("/")
def root():
    return {"message": "Hello from ASTA MVP"}

# Create task
@app.post("/tasks/", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(session.get_db)):
    return crud.create_task(db=db, title=task.title, description=task.description, due_date=task.due_date)

# Get tasks
@app.get("/tasks/", response_model=list[schemas.Task])
def read_tasks(skip: int = 0, limit: int = 10, db: Session = Depends(session.get_db)):
    return crud.get_tasks(db=db, skip=skip, limit=limit)

