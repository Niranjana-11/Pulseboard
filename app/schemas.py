from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

Severity = Literal["info", "warning", "error", "critical"]
Status = Literal["open", "acknowledged", "resolved"]


class ServiceCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)
    description: str | None = None


class ServiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    created_at: datetime


class AlertCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    service_id: int
    title: str = Field(min_length=1, max_length=200)
    message: str | None = None
    severity: Severity = "info"
    labels: dict[str, Any] | None = None
    source: str | None = Field(default=None, max_length=50)


class AlertRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    service_id: int
    title: str
    message: str | None
    severity: Severity
    status: Status
    labels: dict[str, Any] | None
    source: str | None
    created_at: datetime
    resolved_at: datetime | None


class AlertStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Status


class AlertPage(BaseModel):
    items: list[AlertRead]
    total: int
    limit: int
    offset: int


class SummaryRead(BaseModel):
    open_by_severity: dict[str, int]
    total_open: int