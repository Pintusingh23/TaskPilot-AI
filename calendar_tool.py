
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os

SCOPES = [
    "https://www.googleapis.com/auth/calendar"
]


def authenticate_calendar():
    creds = None

    if os.path.exists("calendar_token.json"):
        creds = Credentials.from_authorized_user_file(
            "calendar_token.json", SCOPES
        )

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token: 
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("calendar_token.json", "w") as token:
            token.write(creds.to_json())

    print("Google Calendar authentication successful!")
    return build("calendar", "v3", credentials=creds)


def get_upcoming_events(service, max_results=10):
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
        return "No upcoming events found."

    result = []

    for event in events:
        start = event["start"].get(
            "dateTime", event["start"].get("date")
        )

        result.append({
            "title": event.get("summary", "No title"),
            "start": start,
            "description": event.get("description", "")
        })

    return result


def create_calendar_event(
    service,
    summary,
    start_datetime,
    end_datetime,
    description=""
):
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
        "link": created_event.get("htmlLink")
    }


if __name__ == "__main__":
    service = authenticate_calendar()

    print("\n===== YOUR UPCOMING EVENTS =====")

    events = get_upcoming_events(service)

    if isinstance(events, str):
        print(events)
    else:
        for event in events:
            print(event)

    print("\nCalendar reading completed!")
