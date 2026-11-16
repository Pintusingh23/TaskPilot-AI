from typing import Optional, List, Any
from pydantic import BaseModel, Field

class EmailSendRequest(BaseModel):
    to: str = Field(..., min_length=1)
    subject: str = Field(..., min_length=1)
    body: str = Field(..., min_length=1)
    confirmed: bool = False

class CalendarEventCreate(BaseModel):
    summary: str = Field(..., min_length=1)
    start_datetime: str = Field(..., description="ISO 8601 formatted datetime")
    end_datetime: str = Field(..., description="ISO 8601 formatted datetime")
    description: Optional[str] = ""
    confirmed: bool = False

class ToolConfirmationAction(BaseModel):
    tool_name: str
    arguments: dict
    confirmed: bool

