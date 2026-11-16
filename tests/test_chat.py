from unittest.mock import patch, MagicMock

def test_conversations_crud(client, auth_headers):
    # 1. Create a conversation
    create_res = client.post("/api/conversations", json={"title": "Planning Week 48"}, headers=auth_headers)
    assert create_res.status_code == 201
    conv = create_res.json()
    conv_id = conv["id"]
    assert conv["title"] == "Planning Week 48"

    # 2. List conversations
    list_res = client.get("/api/conversations", headers=auth_headers)
    assert list_res.status_code == 200
    assert any(c["id"] == conv_id for c in list_res.json())

    # 3. Get conversation detail
    detail_res = client.get(f"/api/conversations/{conv_id}", headers=auth_headers)
    assert detail_res.status_code == 200
    assert detail_res.json()["title"] == "Planning Week 48"
    assert detail_res.json()["messages"] == []

    # 4. Delete conversation
    del_res = client.delete(f"/api/conversations/{conv_id}", headers=auth_headers)
    assert del_res.status_code == 200

    # 5. Confirm deleted
    get_del = client.get(f"/api/conversations/{conv_id}", headers=auth_headers)
    assert get_del.status_code == 404

def test_chat_endpoint_with_mock_agent(client, auth_headers):
    mock_agent_result = {
        "response": "I have created your task 'Prepare slide deck'.",
        "conversation_id": 1,
        "tool_calls": [
            {
                "tool": "create_task",
                "arguments": {"title": "Prepare slide deck"},
                "result": {"status": "success", "task_id": 1}
            }
        ],
        "action_preview": None
    }

    with patch("app.api.chat.AgentService.process_chat", return_value=mock_agent_result):
        chat_req = {
            "message": "Create a task to prepare slide deck"
        }
        res = client.post("/api/chat", json=chat_req, headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert "Prepare slide deck" in data["response"]
        assert len(data["tool_calls"]) == 1
        assert data["tool_calls"][0]["tool"] == "create_task"

