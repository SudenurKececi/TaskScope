from __future__ import annotations
from datetime import datetime, timedelta
from sqlalchemy import select, update, delete, or_, distinct
from sqlalchemy.orm import Session
from taskscope.models.task import Task, SubTask

class TaskRepo:
    def __init__(self, session: Session):
        self.session = session

    def create_task(self, title: str, description: str, due_at: datetime | None, 
                   priority: str = "Orta", tags: str = "", subtasks: list[str] = None) -> Task:
        
        task = Task(
            title=title.strip(), 
            description=description.strip(), 
            due_at=due_at,
            priority=priority,
            tags=tags,
            status="todo", # Varsayılan durum
            is_done=False
        )
        
        if subtasks:
            for st in subtasks:
                if st.strip():
                    task.subtasks.append(SubTask(title=st.strip(), is_done=False))

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def update_task(self, task_id: int, title: str, description: str, due_at: datetime | None,
                   priority: str, tags: str) -> None:
        stmt = (
            update(Task).where(Task.id == task_id)
            .values(title=title.strip(), description=description.strip(), due_at=due_at,
                    priority=priority, tags=tags, updated_at=datetime.utcnow())
        )
        self.session.execute(stmt)
        self.session.commit()

    # --- KANBAN İÇİN GEREKLİ OLAN FONKSİYON ---
    def update_status(self, task_id: int, new_status: str) -> None:
        is_done = (new_status == "done")
        stmt = update(Task).where(Task.id == task_id).values(status=new_status, is_done=is_done)
        self.session.execute(stmt)
        self.session.commit()
    # ------------------------------------------

    def delete_task(self, task_id: int) -> None:
        stmt = delete(Task).where(Task.id == task_id)
        self.session.execute(stmt)
        self.session.commit()

    def set_done(self, task_id: int, is_done: bool) -> None:
        new_status = "done" if is_done else "todo"
        stmt = update(Task).where(Task.id == task_id).values(is_done=is_done, status=new_status, updated_at=datetime.utcnow())
        self.session.execute(stmt)
        self.session.commit()
        
    def set_subtask_done(self, subtask_id: int, is_done: bool) -> None:
        stmt = update(SubTask).where(SubTask.id == subtask_id).values(is_done=is_done)
        self.session.execute(stmt)
        self.session.commit()

    def get_task(self, task_id: int) -> Task | None:
        return self.session.execute(select(Task).where(Task.id == task_id)).scalars().first()

    def get_projects(self) -> list[str]:
        return []

    def list_tasks(self, search_text: str = "", filter_mode: str = "all") -> list[Task]:
        stmt = select(Task)
        s = search_text.strip()
        if s:
            like = f"%{s}%"
            stmt = stmt.where(or_(
                Task.title.like(like), 
                Task.description.like(like), 
                Task.tags.like(like)
            ))

        now = datetime.now()
        if filter_mode == "today":
            start = datetime(now.year, now.month, now.day)
            end = start + timedelta(days=1)
            stmt = stmt.where(Task.due_at.is_not(None), Task.due_at >= start, Task.due_at < end)
        elif filter_mode == "week":
            start = datetime(now.year, now.month, now.day)
            end = start + timedelta(days=7)
            stmt = stmt.where(Task.due_at.is_not(None), Task.due_at >= start, Task.due_at < end)
        elif filter_mode == "done":
            stmt = stmt.where(Task.is_done == True)
        elif filter_mode == "undone":
            stmt = stmt.where(Task.is_done == False)

        stmt = stmt.order_by(Task.is_done.asc(), Task.due_at.is_(None).asc(), Task.created_at.desc())
        return list(self.session.execute(stmt).unique().scalars().all())
