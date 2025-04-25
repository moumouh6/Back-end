from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import os
from pathlib import Path

# Créer le dossier data s'il n'existe pas
data_dir = Path(__file__).parent / "data"
data_dir.mkdir(exist_ok=True)

# Utiliser un seul emplacement pour la base de données
SQLALCHEMY_DATABASE_URL = f"sqlite:///{data_dir}/platform.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 