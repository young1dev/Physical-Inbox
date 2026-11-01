from app.database.base import Base

import uuid
from datetime import datetime
from sqlalchemy import DateTime, func, Uuid, Text
from sqlalchemy.orm import Mapped, mapped_column


class ConfiguredDevice(Base):
    __tablename__ = "configure_devices"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    device_id: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    credential_hash: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    status: Mapped[bool] = mapped_column(nullable=False, default=False)
    configured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
