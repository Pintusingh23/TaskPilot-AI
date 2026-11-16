import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from groq import Groq

from app.core.config import settings
from app.models.conversation import Conversation
from app.models.message import ChatMessage
from app.tools.agent_tools import (
    AGENT_TOOLS_SCHEMA,
    calculator,
    get_current_datetime,
    web_search,
    read_inbox,
    send_email_tool,
    read_calendar,
    create_calendar_event_tool,
    create_task_tool,
    list_tasks_tool,
    update_task_tool,
    complete_task_tool,
    delete_task_tool
)

logger = logging.getLogger("taskpilot.agent")

groq_client = None
if settings.GROQ_API_KEY:
    try:
        groq_client = Groq(api_key=settings.GROQ_API_KEY)
    except Exception as e:
        logger.error(f"Failed to initialize Groq client: {e}")

PRIMARY_MODEL = "openai/gpt-oss-20b"
FALLBACK_MODELS = ["openai/gpt-oss-120b", "qwen/qwen3.8-27b"]

SYSTEM_PROMPT = """You are TaskPilot AI, an elite personal AI productivity assistant.
You help users manage tasks, organize their schedule, search the web, read inbox emails, send emails, and create calendar events.

AVAILABLE TOOLS:
1. calculator(a, b, operation)
2. get_current_datetime() - always use this before interpreting relative dates like 'tomorrow', 'next week', 'Friday'.
3. web_search(query) - search the web via Tavily.
4. read_inbox(max_results) - read recent Gmail messages.
5. send_email(to, subject, body, confirmed) - prepare or send email.
6. read_calendar(max_results) - read upcoming Google Calendar events.
7. create_calendar_event(summary, start_datetime, end_datetime, description, confirmed) - schedule calendar events.
8. create_task(title, description, priority, due_date) - add new tasks to TaskPilot.
9. list_tasks(status, priority, search) - view pending, in_progress, or completed tasks.
10. update_task(task_id, title, description, status, priority, due_date) - update task details.
11. complete_task(task_id) - mark a task as completed.
12. delete_task(task_id, confirmed) - delete a task.

CRITICAL SAFETY & EXECUTION RULES:
- IMPORTANT: Sending emails and creating calendar events require explicit user confirmation.
  When the user asks to send an email or create a calendar event, call the corresponding tool with confirmed=False (or without confirmed) to generate an action preview.
  Only pass confirmed=True if the user has explicitly confirmed the action in the conversation.
- Deleting tasks also requires user confirmation: call delete_task with confirmed=False unless the user explicitly said 'yes, delete it' or confirmed.
- When scheduling meetings or calendar events, always assume timezone is Asia/Kolkata unless specified. If the user doesn't specify an end time, ask or default to 1 hour after start datetime.
- For task queries like 'show my pending tasks' or 'create a task', immediately call the appropriate task management tool.
- Provide clean, polite, markdown-formatted responses explaining the outcome clearly.
"""

def execute_agent_tool(
    name: str,
    args: Dict[str, Any],
    db: Session,
    user_id: int
) -> Any:
    try:
        if name == "calculator":
            return calculator(**args)
        elif name == "get_current_datetime":
            return get_current_datetime()
        elif name == "web_search":
            return web_search(**args)
        elif name == "read_inbox":
            return read_inbox(**args)
        elif name == "send_email":
            return send_email_tool(**args)
        elif name == "read_calendar":
            return read_calendar(**args)
        elif name == "create_calendar_event":
            return create_calendar_event_tool(**args)
        elif name == "create_task":
            return create_task_tool(db=db, user_id=user_id, **args)
        elif name == "list_tasks":
            return list_tasks_tool(db=db, user_id=user_id, **args)
        elif name == "update_task":
            return update_task_tool(db=db, user_id=user_id, **args)
        elif name == "complete_task":
            return complete_task_tool(db=db, user_id=user_id, **args)
        elif name == "delete_task":
            return delete_task_tool(db=db, user_id=user_id, **args)
        else:
            return {"error": f"Tool '{name}' not found."}
    except Exception as e:
        logger.error(f"Error executing tool '{name}': {e}")
        return {"error": f"Tool execution failed: {str(e)}"}

class AgentService:
    @staticmethod
    def process_chat(
        db: Session,
        user_id: int,
        user_message: str,
        conversation_id: Optional[int] = None
    ) -> Dict[str, Any]:
        if not groq_client:
            raise RuntimeError("Groq API client is not configured. Please check GROQ_API_KEY in .env.")

        # 1. Retrieve or create conversation
        conversation = None
        if conversation_id:
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            ).first()

        if not conversation:
            # Create new conversation with title based on first user message
            title = user_message[:40] + ("..." if len(user_message) > 40 else "")
            conversation = Conversation(
                user_id=user_id,
                title=title
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)

        # 2. Persist user message in DB
        db_user_msg = ChatMessage(
            conversation_id=conversation.id,
            role="user",
            content=user_message
        )
        db.add(db_user_msg)
        db.commit()

        # 3. Load recent context (last 10 messages)
        history_msgs = (
            db.query(ChatMessage)
            .filter(ChatMessage.conversation_id == conversation.id)
            .order_by(ChatMessage.created_at.asc())
            .all()
        )

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for m in history_msgs:
            if m.role in ["user", "assistant"]:
                messages.append({"role": m.role, "content": m.content})

        # 4. Multi-step LLM Tool Loop
        step = 0
        max_steps = 5
        executed_tool_calls: List[dict] = []
        action_preview = None

        while step < max_steps:
            step += 1

            # Call Groq with primary or fallback model
            response = None
            models_to_try = [PRIMARY_MODEL] + FALLBACK_MODELS
            last_err = None

            for m in models_to_try:
                try:
                    response = groq_client.chat.completions.create(
                        model=m,
                        messages=messages,
                        tools=AGENT_TOOLS_SCHEMA,
                        tool_choice="auto",
                        temperature=0.2
                    )
                    break
                except Exception as err:
                    last_err = err
                    continue

            if not response:
                final_response_text = f"I encountered an error communicating with the AI service: {str(last_err)}"
                break

            assistant_msg = response.choices[0].message
            messages.append(assistant_msg)

            # If no tool calls, this is the final natural language answer
            if not assistant_msg.tool_calls:
                final_response_text = assistant_msg.content or "Done."
                break

            # Execute tools
            for tool_call in assistant_msg.tool_calls:
                fn_name = tool_call.function.name
                raw_args = tool_call.function.arguments
                try:
                    args = json.loads(raw_args)
                except Exception:
                    args = {}

                tool_result = execute_agent_tool(
                    name=fn_name,
                    args=args,
                    db=db,
                    user_id=user_id
                )

                executed_tool_calls.append({
                    "tool": fn_name,
                    "arguments": args,
                    "result": tool_result
                })

                # Check if this tool generated a confirmation preview
                if isinstance(tool_result, dict) and tool_result.get("status") == "requires_confirmation":
                    action_preview = tool_result

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result, default=str)
                })

        # 5. Persist assistant response in DB
        db_assistant_msg = ChatMessage(
            conversation_id=conversation.id,
            role="assistant",
            content=final_response_text
        )
        db.add(db_assistant_msg)
        conversation.updated_at = datetime.now(timezone.utc)
        db.commit()

        return {
            "response": final_response_text,
            "conversation_id": conversation.id,
            "tool_calls": executed_tool_calls,
            "action_preview": action_preview
        }

