from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.crud.user import get_user_by_id, get_all_users, update_user, delete_user
from app.schemas.user import UserBase, User as UserSchema
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserSchema)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Mevcut kullanıcı bilgilerini getir"""
    return current_user

@router.get("/", response_model=List[UserSchema])
async def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Tüm kullanıcıları listele (admin için)"""
    users = get_all_users(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=UserSchema)
async def get_user(user_id: str, db: Session = Depends(get_db)):
    """Belirli bir kullanıcıyı getir"""
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    return user

@router.put("/{user_id}", response_model=UserSchema)
async def update_user_info(
    user_id: str, 
    user_update: UserBase, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Kullanıcı bilgilerini güncelle"""
    # Sadece kendi bilgilerini güncelleyebilir
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Sadece kendi bilgilerinizi güncelleyebilirsiniz")
    
    updated_user = update_user(db, user_id, username=user_update.username)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    return updated_user

@router.delete("/{user_id}")
async def delete_user_account(
    user_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Kullanıcı hesabını sil"""
    # Sadece kendi hesabını silebilir
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Sadece kendi hesabınızı silebilirsiniz")
    
    success = delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    return {"message": "Kullanıcı başarıyla silindi"}
