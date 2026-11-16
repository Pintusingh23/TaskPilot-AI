
import os
import json
from datetime import datetime

from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient

from gmail_tool import (
    authenticate_gmail,
    send_email,
    read_recent_emails
)

from calendar_tool import (
    authenticate_calendar,
    get_upcoming_events,
    create_calendar_event
)


# ==============================
# INITIALIZATION
# ==============================

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

MODEL = "openai/gpt-oss-20b"

gmail_service = None
calendar_service = None


# ==============================
# BASIC TOOLS
# ==============================

def calculator(a, b, operation):

    if operation == "add":
        return a + b

    elif operation == "subtract":
        return a - b

    elif operation == "multiply":
        return a * b

    elif operation == "divide":
        if b == 0:
            return "Cannot divide by zero"
        return a / b

    return "Invalid operation"


def get_current_datetime():

    return datetime.now().astimezone().isoformat()


def web_search(query):

    response = tavily.search(
        query=query,
        max_results=5
    )

    return response.get("results", [])


# ==============================
# GMAIL TOOLS
# ==============================

def get_gmail_service():

    global gmail_service

    if gmail_service is None:
        gmail_service = authenticate_gmail()

    return gmail_service


def read_inbox(max_results=5):

    service = get_gmail_service()

    return read_recent_emails(
        service,
        max_results=max_results
    )


def send_email_with_confirmation(to, subject, body):

    print("\n===== EMAIL PREVIEW =====")
    print("To:", to)
    print("Subject:", subject)
    print("Message:", body)

    approval = input(
        "\nDo you want to send this email? (yes/no): "
    ).strip().lower()

    if approval not in ["yes", "y"]:
        return "Email cancelled. Nothing was sent."

    service = get_gmail_service()

    result = send_email(
        service,
        to,
        subject,
        body
    )

    return result


# ==============================
# GOOGLE CALENDAR TOOLS
# ==============================

def get_calendar_service():

    global calendar_service

    if calendar_service is None:
        calendar_service = authenticate_calendar()

    return calendar_service


def read_calendar(max_results=10):

    service = get_calendar_service()

    return get_upcoming_events(
        service,
        max_results=max_results
    )


def create_event_with_confirmation(
    summary,
    start_datetime,
    end_datetime,
    description=""
):

    print("\n===== CALENDAR EVENT PREVIEW =====")
    print("Title:", summary)
    print("Start:", start_datetime)
    print("End:", end_datetime)
    print("Description:", description)

    approval = input(
        "\nCreate this event in Google Calendar? (yes/no): "
    ).strip().lower()

    if approval not in ["yes", "y"]:
        return "Event creation cancelled. Nothing was added."

    service = get_calendar_service()

    result = create_calendar_event(
        service,
        summary,
        start_datetime,
        end_datetime,
        description
    )

    return result


# ==============================
# AI TOOL DEFINITIONS
# ==============================

tools = [

    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Perform mathematical calculations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"},
                    "operation": {
                        "type": "string",
                        "enum": [
                            "add",
                            "subtract",
                            "multiply",
                            "divide"
                        ]
                    }
                },
                "required": ["a", "b", "operation"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_current_datetime",
            "description": "Get the current date and time.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the internet for information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "read_inbox",
            "description": "Read recent Gmail messages.",
            "parameters": {
                "type": "object",
                "properties": {
                    "max_results": {"type": "integer"}
                },
                "required": ["max_results"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Prepare and send an email after user confirmation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"}
                },
                "required": ["to", "subject", "body"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "read_calendar",
            "description": "Read upcoming Google Calendar events.",
            "parameters": {
                "type": "object",
                "properties": {
                    "max_results": {"type": "integer"}
                },
                "required": ["max_results"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "create_calendar_event",
            "description": (
                "Create a Google Calendar event. "
                "Use ISO format for start and end datetime, "
                "for example 2026-11-04T10:00:00. "
                "Always ask the user for missing date or time."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "start_datetime": {"type": "string"},
                    "end_datetime": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": [
                    "summary",
                    "start_datetime",
                    "end_datetime",
                    "description"
                ]
            }
        }
    }

]


# ==============================
# TOOL EXECUTION
# ==============================

def execute_tool(function_name, arguments):

    if function_name == "calculator":
        return calculator(**arguments)

    elif function_name == "get_current_datetime":
        return get_current_datetime()

    elif function_name == "web_search":
        return web_search(**arguments)

    elif function_name == "read_inbox":
        return read_inbox(**arguments)

    elif function_name == "send_email":
        return send_email_with_confirmation(**arguments)

    elif function_name == "read_calendar":
        return read_calendar(**arguments)

    elif function_name == "create_calendar_event":
        return create_event_with_confirmation(**arguments)

    return "Tool not found."


# ==============================
# AI AGENT
# ==============================

def run_agent(user_input):

    messages = [

        {
            "role": "system",
            "content": """
You are TaskPilot AI, a helpful personal AI assistant.

You can use these tools:
1. Calculator
2. Current date and time
3. Web search
4. Gmail send
5. Gmail inbox reader
6. Google Calendar reader
7. Google Calendar event creator

IMPORTANT RULES:

- Understand the user's request before choosing a tool.
- Use tools whenever they are needed.
- Never claim an email was sent unless the tool confirms it.
- Never claim a calendar event was created unless the tool confirms it.
- Email sending and calendar event creation require explicit user confirmation.
- If a date or time is missing, ask the user instead of guessing.
- For calendar events, use Asia/Kolkata timezone.
- Use the current date and time tool when interpreting relative dates
  such as tomorrow or next Monday.
- For meetings, if the user does not specify an end time,
  ask for it instead of inventing one.
- Keep responses clear and concise.
- Respond in the language used by the user.
"""
        },

        {
            "role": "user",
            "content": user_input
        }

    ]

    while True:

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        assistant_message = response.choices[0].message

        messages.append(assistant_message)

        if not assistant_message.tool_calls:

            return assistant_message.content

        for tool_call in assistant_message.tool_calls:

            function_name = tool_call.function.name

            arguments = json.loads(
                tool_call.function.arguments
            )

            try:

                result = execute_tool(
                    function_name,
                    arguments
                )

            except Exception as error:

                result = f"Tool error: {str(error)}"

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(
                    result,
                    default=str
                )
            })


# ==============================
# MAIN PROGRAM
# ==============================

def main():

    print("\n===================================")
    print("       Welcome to TaskPilot AI")
    print("===================================\n")

    print("Available Tools:")
    print("1. Calculator")
    print("2. Current Date and Time")
    print("3. Web Search")
    print("4. Gmail Send")
    print("5. Gmail Inbox Reader")
    print("6. Google Calendar Reader")
    print("7. Google Calendar Event Creator")

    print("\nType 'exit' to stop.\n")

    while True:

        user_input = input("You: ").strip()

        if user_input.lower() == "exit":
            print("\nTaskPilot AI stopped. Goodbye!")
            break

        if not user_input:
            continue

        try:

            response = run_agent(user_input)

            print("\nTaskPilot:", response, "\n")

        except Exception as error:

            print("\nError:", str(error), "\n")


if __name__ == "__main__":
    main()
