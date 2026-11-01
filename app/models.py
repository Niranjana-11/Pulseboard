from datetime import datetime
from sqlalchemy import (
    BigInteger, CheckConstraint, DateTime, ForeignKey,
    Index, Integer, String, Text, func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Service(Base):
    __tablename__ = "services"                       # actual table name in Postgres

    id: Mapped[int] = mapped_column(Integer, primary_key=True)   # auto-incrementing PK
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)       # str | None means nullable
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    alerts: Mapped[list["Alert"]] = relationship(back_populates="service")


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    service_id: Mapped[int] = mapped_column(
        ForeignKey("services.id", ondelete="RESTRICT"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str | None] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, server_default="info")
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="open")
    labels: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    source: Mapped[str | None] = mapped_column(String(50))
    service: Mapped["Service"] = relationship(back_populates="alerts")

    __table_args__ = (
        CheckConstraint("severity IN ('info','warning','error','critical')", name="ck_alerts_severity"),
        CheckConstraint("status IN ('open','acknowledged','resolved')", name="ck_alerts_status"),
        CheckConstraint("resolved_at IS NULL OR resolved_at >= created_at",
                        name="ck_alerts_resolved_after_created"),
        Index("ix_alerts_service_created", "service_id", "created_at"),
        Index("ix_alerts_status_created", "status", "created_at"),
    )