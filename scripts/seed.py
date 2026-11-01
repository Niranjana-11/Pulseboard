from sqlalchemy import select
from app.database import SessionLocal
from app.models import Alert, Service

SERVICES = [
    ("payment-service", "Handles card and UPI payments"),
    ("auth-service", "Login and token issuing"),
    ("orders-db", "Primary orders database"),
]


def main():
    with SessionLocal() as session:                        # session closes automatically
        existing = session.scalars(select(Service)).all()
        if existing:
            print("Services already exist, skipping seed.")
            return

        services = [Service(name=n, description=d) for n, d in SERVICES]
        session.add_all(services)
        session.flush()                                    # sends INSERTs so ids are assigned

        session.add_all([
            Alert(service_id=services[0].id, title="High latency on /charge",
                  severity="warning", labels={"region": "ap-south-1"}),
            Alert(service_id=services[0].id, title="Payment gateway timeout",
                  severity="critical", message="3 consecutive timeouts"),
            Alert(service_id=services[1].id, title="Login error rate above 5%",
                  severity="error"),
            Alert(service_id=services[2].id, title="Disk usage at 85%",
                  severity="info", status="acknowledged"),
        ])
        session.commit()                                   # makes everything permanent
        print("Seeded.")


if __name__ == "__main__":
    main()