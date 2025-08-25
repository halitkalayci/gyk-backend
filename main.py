from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime, timedelta
import jwt
import bcrypt
import uuid
import cv2
import numpy as np
from ultralytics import YOLO
import os
import tempfile
from PIL import Image
import io
from sqlalchemy.orm import Session
from database import get_db
from models import User
from crud import get_user_by_email, create_user, get_user_by_id

# JWT ayarları
SECRET_KEY = "gyk-super-secret-key-2024-jwt-auth-system"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# YOLO model yolu
MODEL_PATH = "best.pt"

app = FastAPI(title="GYK Backend API", description="JWT Auth ile CRUD API ve Plaka Tespiti", version="1.0.0")

# Security
security = HTTPBearer()

# YOLO modelini yükle
try:
    model = YOLO(MODEL_PATH)
    print(f"Model başarıyla yüklendi: {MODEL_PATH}")
except Exception as e:
    print(f"Model yüklenirken hata oluştu: {e}")
    model = None

# Pydantic modelleri
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: str
    is_active: bool = True
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class PlakaDetection(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float

class PlakaResponse(BaseModel):
    detections: List[PlakaDetection]
    total_detections: int
    message: str

# Veritabanı bağlantısı artık SQLAlchemy ile sağlanıyor
# Geçici kullanıcı veritabanı kaldırıldı

# Plaka tespiti fonksiyonu
def detect_plates(image_array: np.ndarray, confidence_threshold: float = 0.75):
    """
    Görüntüde plaka tespiti yapar
    
    Args:
        image_array: OpenCV formatında görüntü
        confidence_threshold: Güven eşiği (varsayılan: 0.75)
    
    Returns:
        Tuple: (işaretlenmiş görüntü, tespit listesi)
    """
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Model yüklenemedi"
        )
    
    try:
        # YOLO ile tahmin yap
        result = model.predict(image_array, verbose=False)
        
        detections = []
        marked_image = image_array.copy()
        
        if len(result) > 0 and result[0].boxes is not None:
            boxes = result[0].boxes
            
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = box.conf[0].cpu().numpy()
                
                if conf > confidence_threshold:
                    # Görüntüye dikdörtgen çiz
                    cv2.rectangle(marked_image, 
                                (int(x1), int(y1)), 
                                (int(x2), int(y2)), 
                                (0, 0, 255), 2)
                    
                    # Etiket ekle
                    label = f"Plaka - {conf:.2f}"
                    cv2.putText(marked_image, label, 
                              (int(x1), int(y1) - 10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    
                    # Tespit bilgilerini kaydet
                    detections.append(PlakaDetection(
                        x1=float(x1),
                        y1=float(y1),
                        x2=float(x2),
                        y2=float(y2),
                        confidence=float(conf)
                    ))
        
        return marked_image, detections
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Plaka tespiti sırasında hata oluştu: {str(e)}"
        )

# JWT fonksiyonları
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Geçersiz token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = TokenData(email=email)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_data

def get_current_user(token_data: TokenData = Depends(verify_token), db: Session = Depends(get_db)):
    email = token_data.email
    user = get_user_by_email(db, email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kullanıcı bulunamadı",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# Şifre hash'leme fonksiyonu
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# Auth endpoint'leri
@app.post("/register", response_model=User)
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

@app.post("/login", response_model=Token)
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
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Mevcut kullanıcı bilgilerini getir"""
    return current_user

# Korumalı endpoint örneği
@app.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    """Sadece giriş yapmış kullanıcıların erişebileceği endpoint"""
    return {
        "message": "Bu korumalı bir endpoint!",
        "user": current_user.username,
        "email": current_user.email
    }

@app.get("/")
async def root():
    """API ana sayfası"""
    return {"message": "GYK Backend API'ye hoş geldiniz!"}

# Plaka tespiti endpoint'leri
@app.post("/detect-plates", response_model=PlakaResponse)
async def detect_plates_endpoint(
    file: UploadFile = File(...),
    confidence: float = 0.75,
    current_user: User = Depends(get_current_user)
):
    """
    Yüklenen görüntüde plaka tespiti yapar
    
    Args:
        file: Yüklenecek görüntü dosyası
        confidence: Güven eşiği (0.0 - 1.0 arası)
        current_user: Giriş yapmış kullanıcı
    
    Returns:
        PlakaResponse: Tespit edilen plakaların bilgileri
    """
    # Dosya türü kontrolü
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sadece görüntü dosyaları kabul edilir"
        )
    
    try:
        # Dosyayı oku
        contents = await file.read()
        
        # OpenCV formatına çevir
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Görüntü okunamadı"
            )
        
        # Plaka tespiti yap
        marked_image, detections = detect_plates(image, confidence)
        
        return PlakaResponse(
            detections=detections,
            total_detections=len(detections),
            message=f"{len(detections)} adet plaka tespit edildi"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"İşlem sırasında hata oluştu: {str(e)}"
        )

@app.post("/detect-plates-image")
async def detect_plates_with_image(
    file: UploadFile = File(...),
    confidence: float = 0.75,
    current_user: User = Depends(get_current_user)
):
    """
    Yüklenen görüntüde plaka tespiti yapar ve işaretlenmiş görüntüyü döner
    
    Args:
        file: Yüklenecek görüntü dosyası
        confidence: Güven eşiği (0.0 - 1.0 arası)
        current_user: Giriş yapmış kullanıcı
    
    Returns:
        FileResponse: İşaretlenmiş görüntü dosyası
    """
    # Dosya türü kontrolü
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sadece görüntü dosyaları kabul edilir"
        )
    
    try:
        # Dosyayı oku
        contents = await file.read()
        
        # OpenCV formatına çevir
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Görüntü okunamadı"
            )
        
        # Plaka tespiti yap
        marked_image, detections = detect_plates(image, confidence)
        
        # İşaretlenmiş görüntüyü JPEG formatına çevir
        success, buffer = cv2.imencode('.jpg', marked_image)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Görüntü işlenemedi"
            )
        
        # Geçici dosya oluştur
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            tmp_file.write(buffer.tobytes())
            tmp_file_path = tmp_file.name
        
        return FileResponse(
            path=tmp_file_path,
            media_type='image/jpeg',
            filename=f"detected_plates_{current_user.username}.jpg"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"İşlem sırasında hata oluştu: {str(e)}"
        )

@app.get("/model-status")
async def get_model_status():
    """Model durumunu kontrol eder"""
    return {
        "model_loaded": model is not None,
        "model_path": MODEL_PATH,
        "status": "Model yüklendi" if model is not None else "Model yüklenemedi"
    }

# Kullanıcı yönetimi endpoint'leri
@app.get("/users", response_model=List[User])
async def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Tüm kullanıcıları listele (admin için)"""
    from crud import get_all_users
    users = get_all_users(db, skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str, db: Session = Depends(get_db)):
    """Belirli bir kullanıcıyı getir"""
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    return user

@app.put("/users/{user_id}", response_model=User)
async def update_user_info(
    user_id: str, 
    user_update: UserBase, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Kullanıcı bilgilerini güncelle"""
    from crud import update_user
    
    # Sadece kendi bilgilerini güncelleyebilir
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Sadece kendi bilgilerinizi güncelleyebilirsiniz")
    
    updated_user = update_user(db, user_id, username=user_update.username)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    return updated_user

@app.delete("/users/{user_id}")
async def delete_user_account(
    user_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Kullanıcı hesabını sil"""
    from crud import delete_user
    
    # Sadece kendi hesabını silebilir
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Sadece kendi hesabınızı silebilirsiniz")
    
    success = delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    return {"message": "Kullanıcı başarıyla silindi"}

# Geçici dosyaları temizleme fonksiyonu
def cleanup_temp_files():
    """Geçici dosyaları temizler"""
    temp_dir = tempfile.gettempdir()
    for filename in os.listdir(temp_dir):
        if filename.startswith('detected_plates_') and filename.endswith('.jpg'):
            try:
                os.remove(os.path.join(temp_dir, filename))
            except:
                pass

# Uygulama başlatıldığında geçici dosyaları temizle
cleanup_temp_files()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


# 1. -> Ekstra özellikler (Veritabanı)
# 2. -> Flutter client örneği
# 3. -> Flask client örneği