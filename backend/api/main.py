from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.db import crud, session
from backend.api import schemas
from backend.nlp import nlp_processor
from backend.utils.date_utils import parse_due_date

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
    if task.user_id is not None and not crud.get_user(db, task.user_id):
        raise HTTPException(status_code=404, detail="User not found")
    db_task = crud.create_task(
        db=db,
        title=task.title,
        description=task.description,
        due_date=task.due_date,
        user_id=task.user_id
    )
    # Automatically log the task creation
    if task.user_id:
        crud.create_log(
            db=db,
            user_id=task.user_id,
            event_type="task_created",
            content=f"Task '{task.title}' created"
        )
    return db_task

@app.get("/tasks/", response_model=list[schemas.Task])
def read_tasks(skip: int = 0, limit: int = 10, db: Session = Depends(session.get_db)):
    return crud.get_tasks(db=db, skip=skip, limit=limit)

@app.get("/users/{user_id}/tasks", response_model=list[schemas.Task])
def read_user_tasks(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(session.get_db)):
    if not crud.get_user(db, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return crud.get_tasks_for_user(db=db, user_id=user_id, skip=skip, limit=limit)


# ---------------- Log endpoints ----------------
@app.post("/logs/", response_model=schemas.Log)
def create_log(log: schemas.LogCreate, db: Session = Depends(session.get_db)):
    # Ensure user exists before logging
    if not crud.get_user(db, log.user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return crud.create_log(db=db, user_id=log.user_id, event_type=log.event_type, content=log.content)

@app.get("/logs/", response_model=list[schemas.Log])
def read_logs(skip: int = 0, limit: int = 100, db: Session = Depends(session.get_db)):
    return crud.get_logs(db, skip=skip, limit=limit)

@app.get("/users/{user_id}/logs", response_model=list[schemas.Log])
def read_user_logs(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(session.get_db)):
    if not crud.get_user(db, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return crud.get_logs_for_user(db=db, user_id=user_id, skip=skip, limit=limit)

# ---------- NLP Endpoints ----------

@app.post("/nlp/parse", response_model=schemas.NLPParseOutput)
def parse_text(input_data: schemas.NLPInput):
    """
    Debug endpoint: Returns intent + entities from user input
    without performing any action.
    """
    result = nlp_processor.parse_input(input_data.text)
    return schemas.NLPParseOutput(intent=result["intent"], entities=result["entities"])


@app.post("/nlp/act", response_model=schemas.NLPActOutput)
def act_on_text(input_data: schemas.NLPInput, db: Session = Depends(session.get_db)):
    """
    Main NLP endpoint: interprets user input, performs CRUD if needed,
    and always logs the interaction.
    """
    # Ensure user exists
    if input_data.user_id and not crud.get_user(db, input_data.user_id):
        raise HTTPException(status_code=404, detail="User not found")

    # Run NLP processor
    result = nlp_processor.parse_input(input_data.text)
    intent, entities = result["intent"], result["entities"]

    action = None
    created_task = None
    retrieved_tasks = None
    deleted_task_id = None
    message = None
    log = None

    # Handle intents
    if intent == "create_task":
        # Extract title (remove detected entities + filler words)
        title = input_data.text
        for v in entities.values():
            title = title.replace(v, "")
        title = title.replace("remind me", "").strip()

        # Parse due_date using dateparser
        due_date = parse_due_date(entities)

        created_task = crud.create_task(
            db=db,
            title=title or "Untitled Task",
            description=None,
            due_date=due_date,  # now stores datetime if available
            user_id=input_data.user_id
        )
        action = "task_created"

        log_content = f"Task '{created_task.title}' created"
        if due_date:
            log_content += f" with due date {due_date}"
        else:
            log_content += " (no due date parsed)"

        log = crud.create_log(
            db=db,
            user_id=input_data.user_id,
            event_type="task_created",
            content=log_content
        )

    elif intent == "get_tasks":
        retrieved_tasks = crud.get_tasks(db=db, skip=0, limit=100)
        action = "tasks_retrieved"

        log = crud.create_log(
            db=db,
            user_id=input_data.user_id,
            event_type="conversation",
            content=f"User requested tasks"
        )

    elif intent == "delete_task":
        import re
        match = re.search(r"\d+", input_data.text)
        if match:
            task_id = int(match.group())
            db_task = crud.get_task(db=db, task_id=task_id)
            if db_task:
                crud.delete_task(db=db, task_id=task_id)
                deleted_task_id = task_id
                action = "task_deleted"

                log = crud.create_log(
                    db=db,
                    user_id=input_data.user_id,
                    event_type="task_deleted",
                    content=f"Task with ID {task_id} deleted"
                )
            else:
                raise HTTPException(status_code=404, detail="Task not found")
        else:
            raise HTTPException(status_code=400, detail="No task ID found in text")

    else:
        action = "no_crud"
        message = "This input was logged as a conversation but did not trigger an action."
        log = crud.create_log(
            db=db,
            user_id=input_data.user_id,
            event_type="conversation",
            content=f"User said: {input_data.text}"
        )

    return schemas.NLPActOutput(
        intent=intent,
        entities=entities,
        action=action,
        task=created_task,
        tasks=retrieved_tasks,
        task_id=deleted_task_id,
        message=message,
        log=log
    )
