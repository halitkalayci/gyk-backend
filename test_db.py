from app.database.database import engine, SessionLocal
from app.models.user import User
from app.crud.user import create_user, get_user_by_email, get_all_users
import bcrypt

def test_database_connection():
    """Veritabanı bağlantısını test et"""
    try:
        # Bağlantıyı test et
        with engine.connect() as connection:
            result = connection.execute("SELECT 1")
            print("✅ PostgreSQL bağlantısı başarılı!")
        
        # Tabloları oluştur
        from app.database.database import Base
        Base.metadata.create_all(bind=engine)
        print("✅ Tablolar başarıyla oluşturuldu!")
        
        # Test kullanıcısı oluştur
        db = SessionLocal()
        try:
            # Test kullanıcısı var mı kontrol et
            test_user = get_user_by_email(db, "test@example.com")
            if not test_user:
                # Şifreyi hash'le
                hashed_password = bcrypt.hashpw("test123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                # Test kullanıcısı oluştur
                test_user = create_user(db, "test@example.com", "testuser", hashed_password)
                print(f"✅ Test kullanıcısı oluşturuldu: {test_user.username}")
            else:
                print(f"✅ Test kullanıcısı zaten mevcut: {test_user.username}")
            
            # Tüm kullanıcıları listele
            users = get_all_users(db)
            print(f"✅ Toplam {len(users)} kullanıcı bulundu:")
            for user in users:
                print(f"  - {user.username} ({user.email})")
                
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Veritabanı bağlantı hatası: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_database_connection()
