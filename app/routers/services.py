from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import Service
from app.schemas import ServiceCreate, ServiceRead

router = APIRouter(prefix="/services", tags=["services"])


@router.post("", response_model=ServiceRead, status_code=status.HTTP_201_CREATED)
def create_service(payload: ServiceCreate, db: Session = Depends(get_db)):
    service = Service(**payload.model_dump())
    db.add(service)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Service name already exists")
    db.refresh(service)
    return service


@router.get("", response_model=list[ServiceRead])
def list_services(db: Session = Depends(get_db)):
    return db.scalars(select(Service).order_by(Service.name)).all()


@router.get("/{service_id}", response_model=ServiceRead)
def get_service(service_id: int, db: Session = Depends(get_db)):
    service = db.get(Service, service_id)
    if service is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Service not found")
    return service


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(service_id: int, db: Session = Depends(get_db)):
    try:
        result = db.execute(delete(Service).where(Service.id == service_id))
        if result.rowcount == 0:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Service not found")
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail="Service still has alerts and cannot be deleted",
        )