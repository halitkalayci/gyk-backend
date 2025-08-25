from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database.database import get_db
from app.crud.user import get_user_by_email, create_user
from app.schemas.user import UserCreate, UserLogin, User as UserSchema
from app.schemas.token import Token
from app.core.security import create_access_token, hash_password, verify_password
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserSchema)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Yeni kullanıcı kaydı"""
    # Email kontrolü
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu email adresi zaten kayıtlı"
        )
    
    # Şifreyi hash'le
    hashed_password = hash_password(user.password)
    
    # Yeni kullanıcı oluştur
    return create_user(db, user.email, user.username, hashed_password)

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Kullanıcı girişi"""
    user = get_user_by_email(db, user_credentials.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz email veya şifre",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz email veya şifre",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Access token oluştur
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
