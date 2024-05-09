from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Database simulation
db = {}

class Task(BaseModel):
    id: int
    name: str
    status: str  # 'completed' or 'not completed'

@app.post("/tasks/", status_code=201)
def create_task(task: Task):
    if task.id in db or any(t.name == task.name for t in db.values()):
        raise HTTPException(status_code=400, detail="Task with the same ID or name already exists")
    db[task.id] = task
    return task

@app.get("/tasks/id/{task_id}", response_model=Task)
def get_task_by_id(task_id: int):
    if task_id in db:
        return db[task_id]
    raise HTTPException(status_code=404, detail="Task not found")

@app.get("/tasks/name/", response_model=List[Task])
def get_tasks_by_name(name: str):
    tasks = [task for task in db.values() if task.name == name]
    return tasks

@app.get("/tasks/", response_model=List[Task])
def get_all_tasks():
    return list(db.values())

@app.put("/tasks/id/{task_id}", response_model=Task)
def update_task_by_id(task_id: int, task_update: Task):
    if task_id not in db:
        raise HTTPException(status_code=404, detail="Task not found")
    if task_update.id != task_id:
        raise HTTPException(status_code=400, detail="ID cannot be changed")
    db[task_id] = task_update
    return task_update

@app.put("/tasks/name/{task_name}", response_model=List[Task])
def update_tasks_by_name(task_name: str, task_update: Task):
    updated_tasks = []
    for task in db.values():
        if task.name == task_name:
            task_id = task.id
            task_update.id = task_id  # Retain the original ID
            db[task_id] = task_update
            updated_tasks.append(task_update)
    if not updated_tasks:
        raise HTTPException(status_code=404, detail="No tasks found with this name")
    return updated_tasks

@app.delete("/tasks/id/{task_id}", status_code=204)
def delete_task_by_id(task_id: int):
    if task_id in db:
        del db[task_id]
        return
    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/tasks/name/{task_name}", status_code=204)
def delete_tasks_by_name(task_name: str):
    deleted = False
    for task_id, task in list(db.items()):
        if task.name == task_name:
            del db[task_id]
            deleted = True
    if not deleted:
        raise HTTPException(status_code=404, detail="No tasks found with this name")
