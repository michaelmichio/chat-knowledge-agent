from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from core.config import get_settings

settings = get_settings()

# Engine PostgreSQL
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency untuk FastAPI endpoint."""
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        print("Database error:", e)
        db.rollback()
    finally:
        db.close()
