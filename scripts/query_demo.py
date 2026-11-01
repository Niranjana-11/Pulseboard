from datetime import datetime, timedelta, timezone
from sqlalchemy import func, select
from app.database import SessionLocal
from app.models import Alert, Service


def main():
    with SessionLocal() as session:
        # 1. Latest 5 critical alerts for one service (JOIN)
        stmt = (
            select(Alert.id, Alert.title, Alert.created_at)
            .join(Service, Alert.service_id == Service.id)
            .where(Service.name == "payment-service", Alert.severity == "critical")
            .order_by(Alert.created_at.desc())
            .limit(5)
        )
        print("Latest critical alerts for payment-service:")
        for row in session.execute(stmt):
            print("  ", row.id, row.title, row.created_at)

        # 2. Alert counts per service and severity (GROUP BY)
        stmt = (
            select(Service.name, Alert.severity, func.count(Alert.id))
            .join(Alert, Alert.service_id == Service.id)
            .group_by(Service.name, Alert.severity)
            .order_by(Service.name, Alert.severity)
        )
        print("\nCounts per service and severity:")
        for name, severity, count in session.execute(stmt):
            print(f"   {name:18} {severity:9} {count}")

        # 3. Open alerts in the last hour
        since = datetime.now(timezone.utc) - timedelta(hours=1)
        count = session.scalar(
            select(func.count(Alert.id)).where(Alert.status == "open", Alert.created_at >= since)
        )
        print("\nOpen alerts in the last hour:", count)


if __name__ == "__main__":
    main()