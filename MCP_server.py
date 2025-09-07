from mcp.server.fastmcp import FastMCP
from typing import List
import requests
import logging

# URL of your FastAPI backend
BACKEND_URL = "http://localhost:8000"

# Initialize an MCP server instance
mcp = FastMCP("ToDo List MCP Server")

# ------------------- Tools -------------------

# Note that all of the tool returns "dict" as an input to Claude, it's been shown that its better to do this rather than raw string
@mcp.tool()
def list_tasks() -> List[dict]:
    """List all tasks in to-do list"""
    try:
        resp = requests.get(f"{BACKEND_URL}/tasks")
        resp.raise_for_status()
        return list(resp.json().values())
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching tasks: {e}")
        return {"message: No task present"}

@mcp.tool()
def add_task(title: str, description: str = None, str = None) -> dict:
    """Add a new task"""
    payload = {"title": title}
    if description is not None: payload["description"] = description
    #if start_date is not None: payload["start_date"] = start_date
    #if due_date is not None: payload["due_date"] = due_date
    try:
        resp = requests.post(f"{BACKEND_URL}/tasks", json=payload)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error adding task: {e}")
        return {"message": "Failed to add task"}

@mcp.tool()
def update_task(task_id: int, title: str, description: str = None, status: bool = False) -> dict:
    """Update an existing task"""
    payload = {"title": title, "status": status}
    if description is not None: payload["description"] = description
    #if start_date is not None: payload["start_date"] = start_date
    #if due_date is not None: payload["due_date"] = due_date
    try:
        resp = requests.put(f"{BACKEND_URL}/tasks/{task_id}", json=payload)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error updating task {task_id}: {e}")
        return {"message": "Failed to update task"}

@mcp.tool()
def delete_task(task_id: int) -> dict:
    """Delete a task"""
    try:
        resp = requests.delete(f"{BACKEND_URL}/tasks/{task_id}")
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error deleting task {task_id}: {e}")
        return {"message": "Failed to delete task"}

if __name__ == "__main__":
    mcp.run()

