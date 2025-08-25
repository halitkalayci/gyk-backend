from app.database.database import engine
from app.models.user import User
from app.database.database import Base

def create_tables():
    """Veritabanı tablolarını oluştur"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Veritabanı tabloları başarıyla oluşturuldu!")
    except Exception as e:
        print(f"❌ Tablolar oluşturulurken hata oluştu: {e}")

if __name__ == "__main__":
    create_tables()
