from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session
from infra.db.postgres import get_db
from domain.documents import models, schemas
from core.config import get_settings
from datetime import datetime
import os
import shutil
import uuid
from domain.documents.extractor import extract_text
from domain.documents.embedder import store_embeddings, get_client
from sentence_transformers import SentenceTransformer
from domain.documents.llm_client import generate_answer
from domain.documents.embedder import delete_document_embeddings, chunk_text
from domain.documents.models import Document

router = APIRouter(prefix="/docs", tags=["documents"])

UPLOAD_DIR = "/data/uploads"
CHROMA_DIR = "/data/chroma"
CACHE_DIR = "/data/cache"  # if exists (opsional)

@router.get("/inspect")
def inspect_documents(db: Session = Depends(get_db)):
    # 1. Uploaded files
    uploads = []
    if os.path.exists(UPLOAD_DIR):
        uploads = os.listdir(UPLOAD_DIR)

    # 2. Metadata from DB
    docs = db.query(Document).all()
    metadata = [
        {
            "id": str(doc.id),
            "filename": doc.filename,
            "filetype": doc.filetype,
            "status": doc.status,
            "has_extracted_text": doc.extracted_text is not None and len(doc.extracted_text) > 0,
            "created_at": doc.created_at
        }
        for doc in docs
    ]

    # 3. Embeddings (list ids stored in Chroma)
    try:
        client = get_client(CHROMA_DIR)
        collection = client.get_or_create_collection("documents")
        embeddings_ids = collection.get()["ids"]
    except Exception:
        embeddings_ids = []

    # 4. Cache folder (opsional)
    cache_files = []
    if os.path.exists(CACHE_DIR):
        cache_files = os.listdir(CACHE_DIR)

    return {
        "uploads": uploads,
        "metadata_count": len(metadata),
        "metadata": metadata,
        "embeddings": embeddings_ids,
        "cache": cache_files
    }

# @router.post("/reindex")
# def reindex_documents(db: Session = Depends(get_db)):
#     # INIT CLIENT
#     client = get_client("/data/chroma")
#     collection = client.get_or_create_collection("documents")

#     # 1. CLEAR ALL EMBEDDINGS
#     try:
#         collection.delete(where={})  # hapus semua vector
#     except Exception as e:
#         print("Error clearing Chroma:", e)

#     # 2. LOAD ALL DOCS
#     docs = db.query(Document).all()

#     model = SentenceTransformer("all-MiniLM-L6-v2")

#     total_chunks = 0

#     # 3. RE-EMBED
#     for doc in docs:
#         if not doc.extracted_text:
#             continue

#         chunks = chunk_text(doc.extracted_text)
#         embeddings = model.encode(chunks, convert_to_numpy=True).tolist()

#         ids = [f"{doc.id}-{i}" for i in range(len(chunks))]

#         collection.add(ids=ids, documents=chunks, embeddings=embeddings)
#         total_chunks += len(chunks)

#     return {
#         "message": "Reindex complete",
#         "documents": len(docs),
#         "chunks_created": total_chunks
#     }


# @router.get("/", response_model=list[schemas.DocumentOut])
# def get_docs(db: Session = Depends(get_db)):
#     """Ambil semua dokumen."""
#     return db.query(models.Document).all()

@router.get("/ask")
def ask_question(q: str = Query(..., description="Pertanyaan user"), top_k: int = 3):
    client = get_client("/data/chroma")
    collection = client.get_or_create_collection("documents")

    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_emb = model.encode([q], convert_to_numpy=True).tolist()[0]

    results = collection.query(query_embeddings=[query_emb], n_results=top_k)

    docs = results.get("documents", [[]])[0]
    context = "\n\n".join(docs)

    prompt = f"""
    Gunakan konteks berikut untuk menjawab pertanyaan.

    KONTEKS:
    {context}

    PERTANYAAN:
    {q}

    Jawab dengan jelas dan ringkas dalam bahasa Indonesia.
    """

    answer = generate_answer(prompt)
    return {"question": q, "answer": answer, "context_used": docs}

@router.get("/query")
def query_docs(q: str = Query(..., description="Pertanyaan atau kata kunci"),
               top_k: int = 3):
    client = get_client("/data/chroma")
    collection = client.get_or_create_collection("documents")

    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_emb = model.encode([q], convert_to_numpy=True).tolist()[0]

    results = collection.query(
        query_embeddings=[query_emb],
        n_results=top_k
    )

    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]

    combined = []
    for i, d in enumerate(docs):
        meta = metas[i] if i < len(metas) else {}
        combined.append({
            "rank": i + 1,
            "document_id": meta.get("document_id"),
            "chunk_index": meta.get("chunk_index"),
            "content": d
        })

    return {"query": q, "results": combined}

@router.post("/embed/{doc_id}")
def embed_doc(doc_id: str, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if not doc.extracted_text:
        raise HTTPException(status_code=400, detail="Document has no extracted text yet")

    count = store_embeddings(str(doc.id), doc.extracted_text)
    doc.status = "embedded"
    db.commit()
    db.refresh(doc)

    return {"message": f"{count} chunks embedded for document {doc.filename}"}


@router.post("/extract/{doc_id}", response_model=schemas.DocumentOut)
def extract_doc(doc_id: str, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    settings = get_settings()
    path = os.path.join(settings.UPLOAD_DIR, f"{doc.id}{os.path.splitext(doc.filename)[1]}")

    try:
        content = extract_text(path, doc.filetype)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    doc.extracted_text = content
    doc.status = "extracted"
    db.commit()
    db.refresh(doc)
    return doc

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

@router.delete("/{doc_id}")
def delete_document(doc_id: str, db: Session = Depends(get_db)):

    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # 1. Hapus file upload
    file_path = os.path.join(UPLOAD_DIR, doc.filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    # 2. Hapus embeddings
    delete_document_embeddings(doc_id)

    # 3. Hapus row metadata
    db.delete(doc)
    db.commit()

    return {
        "message": f"Document {doc_id} deleted completely",
        "deleted": {
            "file": True,
            "embeddings": True,
            "metadata": True,
            "extract": True,
        }
    }

# @router.delete("/")
# def delete_all_documents(db: Session = Depends(get_db)):

#     # 1. Hapus semua file upload
#     for f in os.listdir(UPLOAD_DIR):
#         path = os.path.join(UPLOAD_DIR, f)
#         if os.path.isfile(path):
#             os.remove(path)

#     # 2. Hapus semua embeddings (reset chroma)
#     chroma_dir = "/data/chroma"
#     if os.path.exists(chroma_dir):
#         import shutil
#         shutil.rmtree(chroma_dir)
#         os.makedirs(chroma_dir)

#     # 3. Hapus extracted_text + rows
#     db.query(Document).delete()
#     db.commit()

#     return {"message": "All documents + extract + embeddings deleted successfully"}

@router.post("/process")
async def process_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # -------------------------------
    # 1. UPLOAD
    # -------------------------------
    filename = file.filename
    save_path = os.path.join(UPLOAD_DIR, filename)

    # simpan file fisik
    with open(save_path, "wb") as f:
        f.write(await file.read())

    # buat metadata di DB
    doc = Document(filename=filename, filetype=file.content_type)
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # -------------------------------
    # 2. EXTRACT
    # -------------------------------
    extracted_text = extract_text(save_path, file.content_type)

    if not extracted_text or len(extracted_text.strip()) < 5:
        raise HTTPException(status_code=400, detail="Failed to extract text")

    doc.extracted_text = extracted_text
    doc.status = "extracted"
    db.commit()

    # -------------------------------
    # 3. EMBED
    # -------------------------------
    # chunking
    chunks = chunk_text(extracted_text)

    # embedding
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(chunks, convert_to_numpy=True).tolist()

    # simpan ke Chroma
    client = get_client("/data/chroma")
    collection = client.get_or_create_collection("documents")

    ids = [f"{doc.id}-{i}" for i in range(len(chunks))]
    collection.add(ids=ids, documents=chunks, embeddings=embeddings)

    doc.status = "embedded"
    db.commit()

    return {
        "doc_id": str(doc.id),
        "filename": filename,
        "message": "Upload + extract + embed completed",
        "chunks_created": len(chunks)
    }



