import random
from datetime import datetime, timedelta, timezone
from sqlalchemy import insert, select
from app.database import SessionLocal
from app.models import Alert, Service

TOTAL = 200_000
BATCH = 10_000
SEVERITIES = ["info"] * 60 + ["warning"] * 25 + ["error"] * 10 + ["critical"] * 5   # realistic mix
STATUSES = ["open"] * 30 + ["acknowledged"] * 10 + ["resolved"] * 60


def main():
    now = datetime.now(timezone.utc)
    with SessionLocal() as session:
        service_ids = session.scalars(select(Service.id)).all()
        for start in range(0, TOTAL, BATCH):
            rows = [
                {
                    "service_id": random.choice(service_ids),
                    "title": f"Synthetic alert {start + i}",
                    "severity": random.choice(SEVERITIES),
                    "status": random.choice(STATUSES),
                    "created_at": now - timedelta(seconds=random.randint(0, 30 * 24 * 3600)),
                }
                for i in range(BATCH)
            ]
            session.execute(insert(Alert), rows)           # one batched insert per 10,000 rows
            session.commit()
            print(f"Inserted {start + BATCH:,}")


if __name__ == "__main__":
    main()