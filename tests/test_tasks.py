def test_task_crud_lifecycle(client, auth_headers):
    # 1. Create a task
    task_payload = {
        "title": "Complete TaskPilot AI Architecture",
        "description": "Refactor backend and build modern React dashboard",
        "priority": "high",
        "status": "in_progress"
    }
    create_res = client.post("/api/tasks", json=task_payload, headers=auth_headers)
    assert create_res.status_code == 201
    task_data = create_res.json()
    task_id = task_data["id"]
    assert task_data["title"] == task_payload["title"]
    assert task_data["priority"] == "high"
    assert task_data["status"] == "in_progress"

    # 2. Get task by ID
    get_res = client.get(f"/api/tasks/{task_id}", headers=auth_headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == task_id

    # 3. List tasks
    list_res = client.get("/api/tasks", headers=auth_headers)
    assert list_res.status_code == 200
    tasks = list_res.json()
    assert len(tasks) >= 1

    # 4. Filter tasks by priority
    filter_res = client.get("/api/tasks?priority=high", headers=auth_headers)
    assert filter_res.status_code == 200
    assert all(t["priority"] == "high" for t in filter_res.json())

    # 5. Mark task as completed
    complete_res = client.patch(f"/api/tasks/{task_id}/complete", headers=auth_headers)
    assert complete_res.status_code == 200
    assert complete_res.json()["status"] == "completed"

    # 6. Update task title
    update_res = client.put(f"/api/tasks/{task_id}", json={"title": "Updated Title"}, headers=auth_headers)
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Updated Title"

    # 7. Delete task
    delete_res = client.delete(f"/api/tasks/{task_id}", headers=auth_headers)
    assert delete_res.status_code == 200

    # 8. Confirm deletion
    get_deleted = client.get(f"/api/tasks/{task_id}", headers=auth_headers)
    assert get_deleted.status_code == 404

def test_user_task_isolation(client, auth_headers):
    # Create task with user 1
    t1 = client.post("/api/tasks", json={"title": "User 1 Task"}, headers=auth_headers).json()

    # Create user 2
    u2_resp = client.post("/api/auth/register", json={
        "name": "User Two",
        "email": "user2@example.com",
        "password": "Password123"
    })
    u2_headers = {"Authorization": f"Bearer {u2_resp.json()['access_token']}"}

    # User 2 shouldn't see User 1's task
    u2_tasks = client.get("/api/tasks", headers=u2_headers).json()
    assert len(u2_tasks) == 0

    # User 2 shouldn't be able to delete User 1's task
    del_res = client.delete(f"/api/tasks/{t1['id']}", headers=u2_headers)
    assert del_res.status_code == 404

