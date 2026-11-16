from fastapi import APIRouter, Depends, HTTPException, Query
from app.models.user import User
from app.api.deps import get_current_user
from app.schemas.calendar_gmail import EmailSendRequest
from app.tools.google_tools import safe_read_emails, safe_send_email, get_integrations_status

router = APIRouter(prefix="/gmail", tags=["Gmail"])

@router.get("/recent")
def get_recent_emails(
    max_results: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user)
):
    result = safe_read_emails(max_results=max_results)
    if isinstance(result, dict) and "error" in result:
        return {"emails": [], "warning": result["error"]}
    return {"emails": result}

@router.post("/send")
def send_email_endpoint(
    email_req: EmailSendRequest,
    current_user: User = Depends(get_current_user)
):
    if not email_req.confirmed:
        return {
            "status": "requires_confirmation",
            "message": f"Please confirm sending email to '{email_req.to}' with subject '{email_req.subject}'.",
            "email_data": email_req.model_dump()
        }

    res = safe_send_email(
        recipient=email_req.to,
        subject=email_req.subject,
        body=email_req.body
    )
    if isinstance(res, dict) and "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return res

@router.get("/status")
def integrations_status(current_user: User = Depends(get_current_user)):
    return get_integrations_status()

