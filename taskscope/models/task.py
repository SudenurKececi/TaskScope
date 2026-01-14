from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from taskscope.db.database import Base


class SubTask(Base):
    __tablename__ = "subtasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    is_done: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # İlişki: Parent Task
    task: Mapped["Task"] = relationship("Task", back_populates="subtasks")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)

    due_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_done: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # İlişki: Subtasks (Alt Görevler)
    # cascade="all, delete-orphan": Ana görev silinirse alt görevler de silinsin
    subtasks: Mapped[List[SubTask]] = relationship(
        "SubTask", back_populates="task", cascade="all, delete-orphan", lazy="joined"
    )