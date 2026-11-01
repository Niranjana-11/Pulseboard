from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import Alert
from app.schemas import SummaryRead

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/summary", response_model=SummaryRead)
def summary(db: Session = Depends(get_db)):
    rows = db.execute(
        select(Alert.severity, func.count(Alert.id))
        .where(Alert.status == "open")
        .group_by(Alert.severity)
    ).all()
    by_severity = {severity: count for severity, count in rows}
    return SummaryRead(
        open_by_severity=by_severity,
        total_open=sum(by_severity.values()),
    )