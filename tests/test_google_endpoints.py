from unittest.mock import patch

def test_calendar_endpoints(client, auth_headers):
    # 1. Get calendar events (mocked)
    mock_events = [
        {
            "id": "ev1",
            "title": "Weekly Standup",
            "start": "2026-11-20T09:00:00+05:30",
            "end": "2026-11-20T09:30:00+05:30"
        }
    ]
    with patch("app.api.calendar.safe_read_calendar", return_value=mock_events):
        res = client.get("/api/calendar/events", headers=auth_headers)
        assert res.status_code == 200
        assert len(res.json()["events"]) == 1
        assert res.json()["events"][0]["title"] == "Weekly Standup"

    # 2. Create calendar event without confirmation -> requires_confirmation
    ev_payload = {
        "summary": "Doctor Appointment",
        "start_datetime": "2026-11-21T15:00:00",
        "end_datetime": "2026-11-21T16:00:00",
        "confirmed": False
    }
    unconfirmed_res = client.post("/api/calendar/create", json=ev_payload, headers=auth_headers)
    assert unconfirmed_res.status_code == 200
    assert unconfirmed_res.json()["status"] == "requires_confirmation"

    # 3. Create calendar event with confirmation
    ev_payload["confirmed"] = True
    with patch("app.api.calendar.safe_create_calendar_event", return_value={"status": "success", "event": "Doctor Appointment"}):
        confirmed_res = client.post("/api/calendar/create", json=ev_payload, headers=auth_headers)
        assert confirmed_res.status_code == 200
        assert confirmed_res.json()["status"] == "success"

def test_gmail_endpoints(client, auth_headers):
    # 1. Read inbox (mocked)
    mock_emails = [
        {
            "id": "msg1",
            "from": "alice@example.com",
            "subject": "Project Update",
            "date": "2026-11-16"
        }
    ]
    with patch("app.api.gmail.safe_read_emails", return_value=mock_emails):
        res = client.get("/api/gmail/recent", headers=auth_headers)
        assert res.status_code == 200
        assert len(res.json()["emails"]) == 1
        assert res.json()["emails"][0]["subject"] == "Project Update"

    # 2. Send email without confirmation -> requires_confirmation
    mail_payload = {
        "to": "bob@example.com",
        "subject": "Greetings",
        "body": "Hello Bob!",
        "confirmed": False
    }
    unconfirmed_res = client.post("/api/gmail/send", json=mail_payload, headers=auth_headers)
    assert unconfirmed_res.status_code == 200
    assert unconfirmed_res.json()["status"] == "requires_confirmation"

    # 3. Send email with confirmation
    mail_payload["confirmed"] = True
    with patch("app.api.gmail.safe_send_email", return_value={"status": "success", "to": "bob@example.com"}):
        confirmed_res = client.post("/api/gmail/send", json=mail_payload, headers=auth_headers)
        assert confirmed_res.status_code == 200
        assert confirmed_res.json()["status"] == "success"

