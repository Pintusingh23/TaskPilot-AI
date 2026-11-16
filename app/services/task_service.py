from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate, TaskFilter

class TaskService:
    @staticmethod
    def get_tasks(
        db: Session,
        user_id: int,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Task]:
        query = db.query(Task).filter(Task.user_id == user_id)
        
        if status:
            query = query.filter(Task.status == status)
        if priority:
            query = query.filter(Task.priority == priority)
        if search:
            search_fmt = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Task.title.ilike(search_fmt),
                    Task.description.ilike(search_fmt)
                )
            )
        
        return query.order_by(Task.created_at.desc()).all()

    @staticmethod
    def get_task_by_id(db: Session, user_id: int, task_id: int) -> Optional[Task]:
        return db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()

    @staticmethod
    def create_task(db: Session, user_id: int, task_in: TaskCreate) -> Task:
        task = Task(
            user_id=user_id,
            title=task_in.title.strip(),
            description=task_in.description.strip() if task_in.description else None,
            status=task_in.status,
            priority=task_in.priority,
            due_date=task_in.due_date
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def update_task(db: Session, user_id: int, task_id: int, task_update: TaskUpdate) -> Optional[Task]:
        task = TaskService.get_task_by_id(db, user_id, task_id)
        if not task:
            return None
        
        update_data = task_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)
            
        task.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def delete_task(db: Session, user_id: int, task_id: int) -> bool:
        task = TaskService.get_task_by_id(db, user_id, task_id)
        if not task:
            return False
        
        db.delete(task)
        db.commit()
        return True

    @staticmethod
    def mark_completed(db: Session, user_id: int, task_id: int) -> Optional[Task]:
        task = TaskService.get_task_by_id(db, user_id, task_id)
        if not task:
            return None
            
        task.status = "completed"
        task.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(task)
        return task

