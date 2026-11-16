from app.tools.agent_tools import (
    calculator,
    get_current_datetime,
    send_email_tool,
    create_calendar_event_tool,
    create_task_tool,
    list_tasks_tool,
    complete_task_tool,
    delete_task_tool
)

def test_calculator_operations():
    assert calculator(10, 5, "add") == 15
    assert calculator(10, 5, "subtract") == 5
    assert calculator(10, 5, "multiply") == 50
    assert calculator(10, 5, "divide") == 2.0
    assert "Cannot divide by zero" in str(calculator(10, 0, "divide"))
    assert "Invalid operation" in str(calculator(10, 5, "modulus"))

def test_get_current_datetime():
    dt_str = get_current_datetime()
    assert isinstance(dt_str, str)
    assert len(dt_str) > 10

def test_send_email_confirmation_required():
    # Without confirmation -> must return preview
    preview = send_email_tool(to="boss@example.com", subject="Report", body="Attached", confirmed=False)
    assert preview["status"] == "requires_confirmation"
    assert preview["action"] == "send_email"
    assert preview["preview"]["recipient"] == "boss@example.com"

def test_create_calendar_confirmation_required():
    preview = create_calendar_event_tool(
        summary="Sprint Review",
        start_datetime="2026-11-20T10:00:00",
        end_datetime="2026-11-20T11:00:00",
        confirmed=False
    )
    assert preview["status"] == "requires_confirmation"
    assert preview["action"] == "create_calendar_event"
    assert preview["preview"]["summary"] == "Sprint Review"

def test_agent_task_tools_lifecycle(db_session):
    user_id = 999
    # 1. Create task
    created = create_task_tool(
        db=db_session,
        user_id=user_id,
        title="Agent Task",
        description="Created via tool",
        priority="high"
    )
    assert created["status"] == "success"
    task_id = created["task_id"]

    # 2. List tasks
    tasks = list_tasks_tool(db=db_session, user_id=user_id)
    assert len(tasks) == 1
    assert tasks[0]["id"] == task_id
    assert tasks[0]["priority"] == "high"

    # 3. Complete task
    completed = complete_task_tool(db=db_session, user_id=user_id, task_id=task_id)
    assert completed["status"] == "success"

    # 4. Delete task without confirmation -> requires_confirmation
    del_preview = delete_task_tool(db=db_session, user_id=user_id, task_id=task_id, confirmed=False)
    assert del_preview["status"] == "requires_confirmation"

    # 5. Delete task with confirmation
    del_res = delete_task_tool(db=db_session, user_id=user_id, task_id=task_id, confirmed=True)
    assert del_res["status"] == "success"

