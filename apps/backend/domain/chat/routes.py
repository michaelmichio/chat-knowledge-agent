from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from infra.db.postgres import get_db
from domain.chat import models, schemas
from domain.documents.embedder import get_client
from sentence_transformers import SentenceTransformer
from domain.documents.llm_client import generate_answer
from domain.chat.title_generator import generate_session_title
import uuid

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/start", response_model=schemas.ChatSessionOut)
def start_chat(db: Session = Depends(get_db)):
    session = models.ChatSession()
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

@router.post("/send")
def send_message(session_id: str, message: str, db: Session = Depends(get_db)):

    # 1. Pastikan session valid
    session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # 2. Simpan pesan user
    user_msg = models.ChatMessage(
        session_id=session_id,
        role="user",
        content=message
    )
    db.add(user_msg)
    db.commit()
    
    # --- RENAME SESSION AUTOMATIS (pesan pertama) ---
    if session.title is None or session.title == "":
        session.title = message[:60]
        db.commit()

    # --- AUTO SUMMARY TITLE (LLM) ---
    # Kita update title hanya jika pesan sudah 2 atau lebih
    all_messages = (
        db.query(models.ChatMessage)
        .filter(models.ChatMessage.session_id == session_id)
        .order_by(models.ChatMessage.created_at.asc())
        .all()
    )

    if len(all_messages) >= 2:
        text_messages = [m.content for m in all_messages]
        new_title = generate_session_title(text_messages)

        if new_title and new_title.strip():
            session.title = new_title[:60]
            db.commit()

    # 3. Ambil seluruh history (10 terakhir)
    history = db.query(models.ChatMessage) \
                .filter(models.ChatMessage.session_id == session_id) \
                .order_by(models.ChatMessage.created_at.asc()) \
                .all()

    history_text = ""
    for msg in history:
        history_text += f"{msg.role.upper()}: {msg.content}\n"

    # 4. RAG — ambil chunk paling relevan
    client = get_client("/data/chroma")
    collection = client.get_or_create_collection("documents")

    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_emb = model.encode([message], convert_to_numpy=True).tolist()[0]

    results = collection.query(query_embeddings=[query_emb], n_results=3)
    contexts = results.get("documents", [[]])[0]
    context_text = "\n\n".join(contexts)

    # 5. Build final prompt
    prompt = f"""
    Ini percakapan sebelumnya:

    {history_text}

    Gunakan konteks ini untuk menjawab user:

    {context_text}

    Pertanyaan user:
    {message}

    Jawab singkat dan jelas dalam bahasa Indonesia.
    """

    # 6. Panggil LLM (OpenAI / Ollama / Custom)
    answer = generate_answer(prompt)

    # 7. Simpan jawaban AI
    ai_msg = models.ChatMessage(
        session_id=session_id,
        role="assistant",
        content=answer
    )
    db.add(ai_msg)
    db.commit()

    return {
        "session_id": session_id,
        "answer": answer,
        "memory_count": len(history),
        "context_used": contexts
    }

@router.delete("/{session_id}")
def delete_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    db.delete(session)
    db.commit()

    return {"message": f"Session {session_id} deleted successfully"}

@router.get("/sessions")
def list_sessions(db: Session = Depends(get_db)):
    sessions = (
        db.query(models.ChatSession)
        .order_by(models.ChatSession.updated_at.desc())
        .all()
    )

    return [
        {
            "id": str(s.id),
            "title": s.title,
            "created_at": s.created_at,
            "updated_at": s.updated_at
        }
        for s in sessions
    ]

@router.get("/{session_id}/messages")
def get_session_messages(session_id: str, db: Session = Depends(get_db)):
    session = (
        db.query(models.ChatSession)
        .filter(models.ChatSession.id == session_id)
        .first()
    )

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = (
        db.query(models.ChatMessage)
        .filter(models.ChatMessage.session_id == session_id)
        .order_by(models.ChatMessage.created_at.asc())
        .all()
    )

    return [
        {
            "id": str(m.id),
            "role": m.role,
            "content": m.content,
            "created_at": m.created_at
        }
        for m in messages
    ]
