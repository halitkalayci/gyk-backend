from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# PostgreSQL bağlantı bilgileri
DATABASE_URL = "postgresql://postgres:postgres@localhost:5433/aiapp"

# SQLAlchemy engine oluştur
engine = create_engine(DATABASE_URL)

# SessionLocal sınıfı oluştur
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base sınıfı oluştur
Base = declarative_base()

# Veritabanı bağlantısı için dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
