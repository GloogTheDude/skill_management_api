import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise RuntimeError("DATABASE_URL manquant dans .env")

engine = create_engine(
    DATABASE_URL,
    echo=True,  # Affiche le SQL généré
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

def get_session():
    with SessionLocal() as session:
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise