"""Conexão SQLAlchemy do backend ReViver.

Por padrão usa SQLite local para facilitar a avaliação em Linux/Windows.
Se DATABASE_URL estiver no .env, usa a conexão informada (por exemplo PostgreSQL).
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

BACKEND_DIR = Path(__file__).resolve().parent
load_dotenv(BACKEND_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BACKEND_DIR / 'reviver.db'}")
_engine_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=_engine_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
Base = declarative_base()


def get_db():
    """Fornece uma sessão por requisição e sempre a fecha no final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
