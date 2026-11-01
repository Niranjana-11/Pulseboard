from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import Alert, Service
from app.schemas import (
    AlertCreate,
    AlertPage,
    AlertRead,
    AlertStatusUpdate,
    Severity,
    Status,
)

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.post("", response_model=AlertRead, status_code=status.HTTP_201_CREATED)
def create_alert(payload: AlertCreate, db: Session = Depends(get_db)):
    if db.get(Service, payload.service_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Service not found")
    alert = Alert(**payload.model_dump())
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@router.get("", response_model=AlertPage)
def list_alerts(
    service_id: int | None = None,
    severity: Severity | None = None,
    alert_status: Status | None = Query(default=None, alias="status"),
    since: datetime | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    conditions = []
    if service_id is not None:
        conditions.append(Alert.service_id == service_id)
    if severity is not None:
        conditions.append(Alert.severity == severity)
    if alert_status is not None:
        conditions.append(Alert.status == alert_status)
    if since is not None:
        conditions.append(Alert.created_at >= since)

    total = db.scalar(select(func.count(Alert.id)).where(*conditions))
    rows = db.scalars(
        select(Alert)
        .where(*conditions)
        .order_by(Alert.created_at.desc(), Alert.id.desc())
        .limit(limit)
        .offset(offset)
    ).all()
    return AlertPage(
        items=[AlertRead.model_validate(row) for row in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{alert_id}", response_model=AlertRead)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.get(Alert, alert_id)
    if alert is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Alert not found")
    return alert


@router.patch("/{alert_id}/status", response_model=AlertRead)
def update_alert_status(
    alert_id: int, payload: AlertStatusUpdate, db: Session = Depends(get_db)
):
    alert = db.get(Alert, alert_id)
    if alert is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Alert not found")
    alert.status = payload.status
    alert.resolved_at = func.now() if payload.status == "resolved" else None
    db.commit()
    db.refresh(alert)
    return alert