from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from infra.db.postgres import get_db
from domain.documents import models, schemas
from core.config import get_settings
from datetime import datetime
import os
import shutil
import uuid

router = APIRouter(prefix="/docs", tags=["documents"])

@router.get("/", response_model=list[schemas.DocumentOut])
def get_docs(db: Session = Depends(get_db)):
    """Ambil semua dokumen."""
    return db.query(models.Document).all()

@router.post("/upload", response_model=schemas.DocumentOut)
async def upload_doc(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    settings = get_settings()

    # Validasi mime
    allowed = [m.strip() for m in settings.ALLOWED_MIME.split(",") if m.strip()]
    if file.content_type not in allowed:
        raise HTTPException(status_code=415, detail=f"Unsupported file type: {file.content_type}")

    # Validasi ukuran (jika client mengirim content-length)
    # Catatan: untuk jaga-jaga, kita batasi saat write stream juga.
    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    ext = {
        "application/pdf": ".pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
        "text/csv": ".csv",
    }.get(file.content_type, "")

    doc_id = uuid.uuid4()
    filename = f"{doc_id}{ext}"
    dest_path = os.path.join(settings.UPLOAD_DIR, filename)

    # Tulis file ke disk dengan streaming + guard ukuran
    written = 0
    with open(dest_path, "wb") as out:
        while True:
            chunk = await file.read(1024 * 1024)  # 1MB
            if not chunk:
                break
            written += len(chunk)
            if written > max_bytes:
                out.close()
                os.remove(dest_path)
                raise HTTPException(status_code=413, detail="File too large")
            out.write(chunk)

    # Simpan metadata dokumen
    doc = models.Document(
        id=doc_id,
        filename=file.filename,
        filetype=file.content_type,
        status="uploaded",  # nanti akan menjadi 'indexed' setelah ekstraksi+embedding
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return doc
