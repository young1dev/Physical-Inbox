from app.database.base import Base

import uuid
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, func, Uuid, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column


class GoogleConnection(Base):
    __tablename__ = "google_connections"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True
    )
    google_email: Mapped[str] = mapped_column(Text, nullable=False)
    google_sub: Mapped[str] = mapped_column(nullable=False, unique=True)
    access_token: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token: Mapped[str] = mapped_column(Text, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    scopes: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
