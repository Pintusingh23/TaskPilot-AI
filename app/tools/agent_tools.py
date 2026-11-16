import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from tavily import TavilyClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.tools.google_tools import (
    safe_read_emails,
    safe_send_email,
    safe_read_calendar,
    safe_create_calendar_event
)
from app.services.task_service import TaskService
from app.schemas.task import TaskCreate, TaskUpdate

# Tavily Client
tavily_client = None
if settings.TAVILY_API_KEY:
    try:
        tavily_client = TavilyClient(api_key=settings.TAVILY_API_KEY)
    except Exception:
        tavily_client = None

def calculator(a: float, b: float, operation: str) -> Any:
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        if b == 0:
            return "Error: Cannot divide by zero"
        return a / b
    return "Error: Invalid operation. Supported operations: add, subtract, multiply, divide"

def get_current_datetime() -> str:
    return datetime.now().astimezone().isoformat()

def web_search(query: str) -> Any:
    if not tavily_client:
        return {"error": "Tavily search API key is not configured or unavailable."}
    try:
        response = tavily_client.search(query=query, max_results=5)
        return response.get("results", [])
    except Exception as e:
        return {"error": f"Search failed: {str(e)}"}

def read_inbox(max_results: int = 5) -> Any:
    return safe_read_emails(max_results=max_results)

def send_email_tool(to: str, subject: str, body: str, confirmed: bool = False) -> Any:
    if not confirmed:
        return {
            "status": "requires_confirmation",
            "action": "send_email",
            "preview": {
                "recipient": to,
                "subject": subject,
                "body": body
            },
            "message": f"I have prepared an email to {to} with subject '{subject}'. Please confirm if you would like me to send it."
        }
    return safe_send_email(to, subject, body)

def read_calendar(max_results: int = 10) -> Any:
    return safe_read_calendar(max_results=max_results)

def create_calendar_event_tool(
    summary: str,
    start_datetime: str,
    end_datetime: str,
    description: str = "",
    confirmed: bool = False
) -> Any:
    if not confirmed:
        return {
            "status": "requires_confirmation",
            "action": "create_calendar_event",
            "preview": {
                "summary": summary,
                "start": start_datetime,
                "end": end_datetime,
                "description": description
            },
            "message": f"I have prepared calendar event '{summary}' from {start_datetime} to {end_datetime}. Please confirm if you want me to add it to your Google Calendar."
        }
    return safe_create_calendar_event(summary, start_datetime, end_datetime, description)

def create_task_tool(
    db: Session,
    user_id: int,
    title: str,
    description: Optional[str] = None,
    priority: str = "medium",
    due_date: Optional[str] = None
) -> Any:
    due_dt = None
    if due_date:
        try:
            due_dt = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
        except Exception:
            due_dt = None

    task_in = TaskCreate(
        title=title,
        description=description,
        status="pending",
        priority=priority if priority in ["low", "medium", "high"] else "medium",
        due_date=due_dt
    )
    task = TaskService.create_task(db=db, user_id=user_id, task_in=task_in)
    return {
        "status": "success",
        "task_id": task.id,
        "title": task.title,
        "priority": task.priority,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "message": f"Task '{task.title}' created successfully."
    }

def list_tasks_tool(
    db: Session,
    user_id: int,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    search: Optional[str] = None
) -> Any:
    tasks = TaskService.get_tasks(db=db, user_id=user_id, status=status, priority=priority, search=search)
    return [
        {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "status": t.status,
            "priority": t.priority,
            "due_date": t.due_date.isoformat() if t.due_date else None
        }
        for t in tasks
    ]

def update_task_tool(
    db: Session,
    user_id: int,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None
) -> Any:
    due_dt = None
    if due_date:
        try:
            due_dt = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
        except Exception:
            due_dt = None

    update_in = TaskUpdate(
        title=title,
        description=description,
        status=status,
        priority=priority,
        due_date=due_dt
    )
    updated = TaskService.update_task(db=db, user_id=user_id, task_id=task_id, task_update=update_in)
    if not updated:
        return {"error": f"Task with ID {task_id} not found."}
    return {
        "status": "success",
        "task_id": updated.id,
        "title": updated.title,
        "task_status": updated.status,
        "message": f"Task #{task_id} updated successfully."
    }

def complete_task_tool(db: Session, user_id: int, task_id: int) -> Any:
    task = TaskService.mark_completed(db=db, user_id=user_id, task_id=task_id)
    if not task:
        return {"error": f"Task with ID {task_id} not found."}
    return {
        "status": "success",
        "task_id": task.id,
        "title": task.title,
        "message": f"Task '{task.title}' has been marked as completed."
    }

def delete_task_tool(db: Session, user_id: int, task_id: int, confirmed: bool = False) -> Any:
    task = TaskService.get_task_by_id(db=db, user_id=user_id, task_id=task_id)
    if not task:
        return {"error": f"Task with ID {task_id} not found."}

    if not confirmed:
        return {
            "status": "requires_confirmation",
            "action": "delete_task",
            "preview": {
                "task_id": task.id,
                "title": task.title
            },
            "message": f"Are you sure you want to permanently delete task '{task.title}' (ID #{task.id})? Please confirm."
        }

    TaskService.delete_task(db=db, user_id=user_id, task_id=task_id)
    return {
        "status": "success",
        "message": f"Task '{task.title}' (ID #{task_id}) deleted successfully."
    }

# Tool schemas for Groq LLM function calling
AGENT_TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Perform mathematical calculations: add, subtract, multiply, divide.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"},
                    "operation": {"type": "string", "enum": ["add", "subtract", "multiply", "divide"]}
                },
                "required": ["a", "b", "operation"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_datetime",
            "description": "Get current date and time with timezone.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the live internet for recent information, facts, or news using Tavily.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_inbox",
            "description": "Read recent Gmail messages from the user's inbox.",
            "parameters": {
                "type": "object",
                "properties": {
                    "max_results": {"type": "integer", "description": "Number of emails to fetch (default 5)"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Send an email via Gmail. Set confirmed=True only if the user explicitly agreed/confirmed sending.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Recipient email address"},
                    "subject": {"type": "string", "description": "Email subject line"},
                    "body": {"type": "string", "description": "Email body content"},
                    "confirmed": {"type": "boolean", "description": "Whether the user explicitly confirmed sending this email"}
                },
                "required": ["to", "subject", "body"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_calendar",
            "description": "Read upcoming events from the user's Google Calendar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "max_results": {"type": "integer", "description": "Number of events to retrieve (default 10)"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_calendar_event",
            "description": "Create an event in Google Calendar. Set confirmed=True only if the user explicitly confirmed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string", "description": "Title or summary of event"},
                    "start_datetime": {"type": "string", "description": "Start ISO 8601 datetime e.g. 2026-11-17T10:00:00"},
                    "end_datetime": {"type": "string", "description": "End ISO 8601 datetime e.g. 2026-11-17T11:00:00"},
                    "description": {"type": "string", "description": "Event description (optional)"},
                    "confirmed": {"type": "boolean", "description": "Whether the user explicitly confirmed creating the event"}
                },
                "required": ["summary", "start_datetime", "end_datetime"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Create a new task in the user's task management system.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task title"},
                    "description": {"type": "string", "description": "Optional details or notes"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high"], "description": "Task priority"},
                    "due_date": {"type": "string", "description": "ISO 8601 due date if specified"}
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "Retrieve tasks belonging to the current user, optionally filtered by status, priority, or search term.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["pending", "in_progress", "completed"]},
                    "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                    "search": {"type": "string", "description": "Keyword to search in task titles"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update an existing task by its ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "ID of task to update"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "status": {"type": "string", "enum": ["pending", "in_progress", "completed"]},
                    "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                    "due_date": {"type": "string"}
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a task as completed by task ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "ID of the task to mark as completed"}
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task by ID. Set confirmed=True only if the user explicitly confirmed deletion.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer", "description": "ID of the task to delete"},
                    "confirmed": {"type": "boolean", "description": "Whether user explicitly confirmed deletion"}
                },
                "required": ["task_id"]
            }
        }
    }
]

