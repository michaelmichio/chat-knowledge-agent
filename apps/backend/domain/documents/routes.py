from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from infra.db.postgres import get_db
from domain.documents import models, schemas

router = APIRouter(prefix="/docs", tags=["documents"])


@router.get("/", response_model=list[schemas.DocumentOut])
def get_docs(db: Session = Depends(get_db)):
    """Ambil semua dokumen."""
    return db.query(models.Document).all()
