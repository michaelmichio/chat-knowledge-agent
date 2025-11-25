# STACK
```bash
🧱 Backend: FastAPI
🎨 Frontend: Next.js (v15+ dengan App Router + Tailwind + React Query)
🧠 Vector DB: Chroma
🗃️ Database: PostgreSQL
⚡ Cache: Redis
🐳 Orchestrator: Docker Compose
```

# PIPELINE DATA SINGKAT
```bash
Frontend (Next.js)
   ↓ upload
Backend FastAPI (/upload)
   ↓ ekstraksi dokumen
   ↓ embedding via service
   ↓ simpan ke vector DB
   ↓ metadata ke PostgreSQL
   ↓ Redis cache untuk session
   ↓ chat Q&A (context retrieval)
```

# STRUKTUR FOLDER AWAL
```bash
chat-knowledge-agent/
│
├── apps/
│   ├── backend/
│   │   ├── main.py                        # Entry point FastAPI
│   │   │
│   │   ├── core/
│   │   │   ├── config.py                 # Konfigurasi global (ENV, path, constants)
│   │   │   ├── logger.py                 # Logger setup (structlog / logging)
│   │   │   └── exceptions.py             # Custom error handler + middleware
│   │   │
│   │   ├── domain/
│   │   │   ├── documents/
│   │   │   │   ├── routes.py             # Endpoint upload, index, get docs
│   │   │   │   ├── service.py            # Logika ekstraksi + penyimpanan metadata
│   │   │   │   ├── schemas.py            # Pydantic schema (request/response)
│   │   │   │   └── models.py             # SQLAlchemy model dokumen
│   │   │   │
│   │   │   └── chat/
│   │   │       ├── routes.py             # Endpoint /chat
│   │   │       ├── service.py            # Logika retrieval + LLM client
│   │   │       ├── schemas.py            # Schema pertanyaan & jawaban
│   │   │       └── prompt_template.py    # Template prompt RAG
│   │   │
│   │   ├── infra/
│   │   │   ├── db/
│   │   │   │   ├── postgres.py           # Koneksi PostgreSQL (SQLAlchemy)
│   │   │   │   ├── redis.py              # Redis client (cache & session)
│   │   │   │   └── vector_store.py       # Chroma/FAISS wrapper
│   │   │   │
│   │   │   └── llm/
│   │   │       ├── client.py             # HTTP client ke LLM API
│   │   │       └── embedder.py           # Panggilan ke embedding service
│   │   │
│   │   ├── tests/
│   │   │   ├── test_upload.py
│   │   │   ├── test_chat.py
│   │   │   └── conftest.py
│   │   │
│   │   ├── requirements.txt              # Dependensi backend
│   │   ├── Dockerfile                    # Dockerfile FastAPI
│   │   └── README.md
│   │
│   └── web/
│       ├── app/
│       │   ├── layout.tsx
│       │   ├── page.tsx
│       │   ├── upload/page.tsx
│       │   ├── chat/page.tsx
│       │   └── docs/page.tsx
│       │
│       ├── components/
│       │   ├── chat/ChatBox.tsx
│       │   ├── uploader/FileUploader.tsx
│       │   ├── doc-viewer/DocViewer.tsx
│       │   └── ui/Button.tsx
│       │
│       ├── lib/
│       │   ├── api.ts                    # Helper panggil API backend
│       │   ├── hooks/useChat.ts          # Hook react-query untuk chat
│       │   └── utils.ts
│       │
│       ├── styles/
│       │   ├── globals.css
│       │   └── tailwind.css
│       │
│       ├── next.config.js
│       ├── package.json
│       ├── tsconfig.json
│       ├── Dockerfile                    # Dockerfile Next.js
│       └── README.md
│
├── packages/
│   ├── shared/
│   │   ├── types/
│   │   │   ├── document.ts
│   │   │   ├── chat.ts
│   │   │   └── api.ts
│   │   │
│   │   ├── constants/
│   │   │   ├── endpoints.ts
│   │   │   └── config.ts
│   │   │
│   │   └── utils/
│   │       ├── format.ts
│   │       └── sanitize.ts
│   │
│   └── embeddings/                       # opsional: jika ingin local embedding runner
│       ├── runner.py
│       └── README.md
│
├── infra/
│   ├── migrations/                       # Alembic migrations (backend/db)
│   ├── compose/
│   │   ├── base.yml
│   │   ├── dev.yml
│   │   ├── prod.yml
│   │   └── networks.yml
│   └── scripts/
│       ├── backup_db.sh
│       ├── reindex_docs.sh
│       └── init_db.sh
│
├── docker/
│   ├── backend/
│   │   └── Dockerfile
│   ├── web/
│   │   └── Dockerfile
│   ├── chroma/
│   │   └── Dockerfile
│   └── init/
│       └── seed.sql
│
├── .env.example
├── docker-compose.yml
├── README.md
└── LICENSE
```