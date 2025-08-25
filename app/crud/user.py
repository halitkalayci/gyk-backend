from sqlalchemy.orm import Session
from app.models.user import User
import uuid

def get_user_by_email(db: Session, email: str):
    """Email ile kullanıcı getir"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: str):
    """ID ile kullanıcı getir"""
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, email: str, username: str, hashed_password: str):
    """Yeni kullanıcı oluştur"""
    user_id = str(uuid.uuid4())
    db_user = User(
        id=user_id,
        email=email,
        username=username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_all_users(db: Session, skip: int = 0, limit: int = 100):
    """Tüm kullanıcıları getir"""
    return db.query(User).offset(skip).limit(limit).all()

def update_user(db: Session, user_id: str, **kwargs):
    """Kullanıcı bilgilerini güncelle"""
    db_user = get_user_by_id(db, user_id)
    if db_user:
        for key, value in kwargs.items():
            if hasattr(db_user, key):
                setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: str):
    """Kullanıcı sil"""
    db_user = get_user_by_id(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False
