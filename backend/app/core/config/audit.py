from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import Session

from backend.database import Base, SessionLocal
from .validators import mask_secret_value


class ConfigAuditLog(Base):
    __tablename__ = "config_audit_log"

    id = Column(Integer, primary_key=True, index=True)
    field = Column(String(255), nullable=False)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    changed_by = Column(String(100), nullable=False, default="system")
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)


@dataclass
class AuditEntry:
    field: str
    old_value: Any
    new_value: Any
    changed_by: str = "system"
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def masked_old_value(self) -> str:
        return mask_secret_value(self.field, str(self.old_value))

    def masked_new_value(self) -> str:
        return mask_secret_value(self.field, str(self.new_value))


async def write_audit_entry(entry: AuditEntry) -> None:
    """Persist an audit entry for configuration changes."""

    def _sync_write() -> None:
        db: Session = SessionLocal()
        try:
            audit_record = ConfigAuditLog(
                field=entry.field,
                old_value=entry.masked_old_value(),
                new_value=entry.masked_new_value(),
                changed_by=entry.changed_by,
                timestamp=entry.timestamp,
            )
            db.add(audit_record)
            db.commit()
        finally:
            db.close()

    await asyncio.to_thread(_sync_write)
