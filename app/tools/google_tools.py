import os
import base64
import logging
from pathlib import Path
from datetime import datetime
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

logger = logging.getLogger("taskpilot.google")

BASE_DIR = Path(__file__).resolve().parent.parent.parent

GMAIL_TOKEN_PATH = BASE_DIR / "token.json"
CALENDAR_TOKEN_PATH = BASE_DIR / "calendar_token.json"
CREDENTIALS_PATH = BASE_DIR / "credentials.json"

GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly"
]

CALENDAR_SCOPES = [
    "https://www.googleapis.com/auth/calendar"
]

_gmail_service = None
_calendar_service = None

def get_gmail_service():
    global _gmail_service
    if _gmail_service is not None:
        return _gmail_service

    if not GMAIL_TOKEN_PATH.exists() and not CREDENTIALS_PATH.exists():
        logger.warning("Neither token.json nor credentials.json found for Gmail.")
        return None

    try:
        creds = None
        if GMAIL_TOKEN_PATH.exists():
            creds = Credentials.from_authorized_user_file(str(GMAIL_TOKEN_PATH), GMAIL_SCOPES)

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(GMAIL_TOKEN_PATH, "w") as token:
                token.write(creds.to_json())

        if not creds or not creds.valid:
            if CREDENTIALS_PATH.exists():
                flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), GMAIL_SCOPES)
                creds = flow.run_local_server(port=0)
                with open(GMAIL_TOKEN_PATH, "w") as token:
                    token.write(creds.to_json())

        if creds and creds.valid:
            _gmail_service = build("gmail", "v1", credentials=creds)
            return _gmail_service
    except Exception as e:
        logger.error(f"Error authenticating Gmail: {e}")
        return None

    return None

def get_calendar_service():
    global _calendar_service
    if _calendar_service is not None:
        return _calendar_service

    if not CALENDAR_TOKEN_PATH.exists() and not CREDENTIALS_PATH.exists():
        logger.warning("Neither calendar_token.json nor credentials.json found for Calendar.")
        return None

    try:
        creds = None
        if CALENDAR_TOKEN_PATH.exists():
            creds = Credentials.from_authorized_user_file(str(CALENDAR_TOKEN_PATH), CALENDAR_SCOPES)

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(CALENDAR_TOKEN_PATH, "w") as token:
                token.write(creds.to_json())

        if not creds or not creds.valid:
            if CREDENTIALS_PATH.exists():
                flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), CALENDAR_SCOPES)
                creds = flow.run_local_server(port=0)
                with open(CALENDAR_TOKEN_PATH, "w") as token:
                    token.write(creds.to_json())

        if creds and creds.valid:
            _calendar_service = build("calendar", "v3", credentials=creds)
            return _calendar_service
    except Exception as e:
        logger.error(f"Error authenticating Calendar: {e}")
        return None

    return None

def safe_read_emails(max_results: int = 5):
    service = get_gmail_service()
    if not service:
        return {"error": "Gmail service is not authenticated or unavailable."}

    try:
        results = service.users().messages().list(userId="me", maxResults=max_results, q="in:inbox").execute()
        messages = results.get("messages", [])
        if not messages:
            return []

        email_list = []
        for msg in messages:
            detail = service.users().messages().get(
                userId="me",
                id=msg["id"],
                format="metadata",
                metadataHeaders=["From", "Subject", "Date"]
            ).execute()

            headers = detail.get("payload", {}).get("headers", [])
            email_data = {}
            for h in headers:
                email_data[h["name"]] = h["value"]

            email_list.append({
                "id": msg["id"],
                "from": email_data.get("From", "Unknown"),
                "subject": email_data.get("Subject", "No Subject"),
                "date": email_data.get("Date", "Unknown")
            })

        return email_list
    except Exception as e:
        return {"error": f"Failed to read emails: {str(e)}"}

def safe_send_email(recipient: str, subject: str, body: str):
    service = get_gmail_service()
    if not service:
        return {"error": "Gmail service is not authenticated or unavailable."}

    try:
        message = MIMEText(body)
        message["to"] = recipient
        message["subject"] = subject

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        result = service.users().messages().send(
            userId="me",
            body={"raw": encoded_message}
        ).execute()

        return {
            "status": "success",
            "message_id": result.get("id"),
            "to": recipient,
            "subject": subject
        }
    except Exception as e:
        return {"error": f"Failed to send email: {str(e)}"}

def safe_read_calendar(max_results: int = 10):
    service = get_calendar_service()
    if not service:
        return {"error": "Google Calendar service is not authenticated or unavailable."}

    try:
        now = datetime.now().astimezone().isoformat()
        events_result = service.events().list(
            calendarId="primary",
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        events = events_result.get("items", [])
        if not events:
            return []

        result = []
        for event in events:
            start = event.get("start", {}).get("dateTime", event.get("start", {}).get("date"))
            end = event.get("end", {}).get("dateTime", event.get("end", {}).get("date"))
            result.append({
                "id": event.get("id"),
                "title": event.get("summary", "No title"),
                "start": start,
                "end": end,
                "description": event.get("description", ""),
                "htmlLink": event.get("htmlLink", "")
            })

        return result
    except Exception as e:
        return {"error": f"Failed to read calendar: {str(e)}"}

def safe_create_calendar_event(summary: str, start_datetime: str, end_datetime: str, description: str = ""):
    service = get_calendar_service()
    if not service:
        return {"error": "Google Calendar service is not authenticated or unavailable."}

    try:
        event = {
            "summary": summary,
            "description": description,
            "start": {
                "dateTime": start_datetime,
                "timeZone": "Asia/Kolkata"
            },
            "end": {
                "dateTime": end_datetime,
                "timeZone": "Asia/Kolkata"
            }
        }

        created_event = service.events().insert(
            calendarId="primary",
            body=event
        ).execute()

        return {
            "status": "success",
            "event": created_event.get("summary"),
            "start": start_datetime,
            "end": end_datetime,
            "link": created_event.get("htmlLink")
        }
    except Exception as e:
        return {"error": f"Failed to create calendar event: {str(e)}"}

def get_integrations_status():
    return {
        "gmail": {
            "token_exists": GMAIL_TOKEN_PATH.exists(),
            "credentials_exists": CREDENTIALS_PATH.exists()
        },
        "calendar": {
            "token_exists": CALENDAR_TOKEN_PATH.exists(),
            "credentials_exists": CREDENTIALS_PATH.exists()
        }
    }

