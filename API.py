# Backend API

# Defining API
from fastapi import FastAPI, HTTPException
# Type hint
from typing import Dict
# Data schemas
from pydantic import BaseModel
# Miscellaneous
from datetime import datetime
import json
import os

# Data file
DATA_FILE = "data.json"
# API name
app = FastAPI(title="To-Do List API")

# ----------- Utilities for JSON storage -----------

def load_tasks() -> Dict[str, dict]:
    """Load tasks from JSON file safely"""
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return {}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        #This makes sure to create a brand new Json if the format is wrong -- not the optimal way but will fix
        return {}

def save_tasks(tasks: Dict[str, dict]):
    # Ensure datetime is stored as string
    def default(o):
        if isinstance(o, datetime):
            return o.isoformat()
        raise TypeError(f"Type {type(o)} not serializable")
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f, indent=4, default=default)

# Load tasks at startup
tasks = load_tasks()
task_counter = max([int(k) for k in tasks.keys()], default=0) + 1

# ----------- Task schema -----------
class Task(BaseModel):
    id: int | None = None
    title: str
    description: str | None = None
    #start_date: datetime | None = None
    #due_date: datetime | None = None
    status: bool = False

# Helper: rebuild Task with ID
def build_task(task_id: str, data: dict) -> Task:
    return Task(id=int(task_id), **data)

# ----------- API Endpoints -----------

# Get all tasks
@app.get("/tasks", response_model=Dict[int, Task])
def get_tasks():
    return {int(tid): build_task(tid, data) for tid, data in tasks.items()}

# Create new task
@app.post("/tasks", response_model=Task)
def create_task(task: Task):
    global task_counter
    task_id = str(task_counter)
    task_counter += 1
    tasks[task_id] = {
        "title": task.title,
        "description": task.description,
        "start_date": task.start_date,
        "due_date": task.due_date,
        "status": task.status,
    }
    save_tasks(tasks)
    return build_task(task_id, tasks[task_id])

# Get single task
@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    task = tasks.get(str(task_id))
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return build_task(str(task_id), task)

# Update task
@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, updated_task: Task):
    if str(task_id) not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    tasks[str(task_id)] = {
        "title": updated_task.title,
        "description": updated_task.description,
        "start_date": updated_task.start_date,
        "due_date": updated_task.due_date,
        "status": updated_task.status,
    }
    save_tasks(tasks)
    return build_task(str(task_id), tasks[str(task_id)])

# Delete task
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    if str(task_id) not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    del tasks[str(task_id)]
    save_tasks(tasks)
    return {"message": "Task deleted"}


