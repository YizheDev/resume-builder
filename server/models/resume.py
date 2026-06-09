"""简历 ORM 模型"""

import datetime
from sqlalchemy import JSON, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from server.database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), default="未命名简历")
    role: Mapped[str] = mapped_column(String(100))
    template: Mapped[str] = mapped_column(String(50), default="classic")
    data: Mapped[dict] = mapped_column(JSON, default=dict)
    selections: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    chat_history: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="chatting")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )
