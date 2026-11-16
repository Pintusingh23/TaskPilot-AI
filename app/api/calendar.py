from fastapi import APIRouter, Depends, HTTPException, Query
from app.models.user import User
from app.api.deps import get_current_user
from app.schemas.calendar_gmail import CalendarEventCreate
from app.tools.google_tools import safe_read_calendar, safe_create_calendar_event

router = APIRouter(prefix="/calendar", tags=["Google Calendar"])

@router.get("/events")
def get_events(
    max_results: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user)
):
    result = safe_read_calendar(max_results=max_results)
    if isinstance(result, dict) and "error" in result:
        return {"events": [], "warning": result["error"]}
    return {"events": result}

@router.post("/create")
def create_event(
    event_in: CalendarEventCreate,
    current_user: User = Depends(get_current_user)
):
    if not event_in.confirmed:
        return {
            "status": "requires_confirmation",
            "message": f"Please confirm creating event '{event_in.summary}' from {event_in.start_datetime} to {event_in.end_datetime}.",
            "event_data": event_in.model_dump()
        }

    res = safe_create_calendar_event(
        summary=event_in.summary,
        start_datetime=event_in.start_datetime,
        end_datetime=event_in.end_datetime,
        description=event_in.description or ""
    )
    if isinstance(res, dict) and "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return res

