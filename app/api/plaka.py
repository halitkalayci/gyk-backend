from fastapi import APIRouter, HTTPException, Depends, status, File, UploadFile
from fastapi.responses import FileResponse
import cv2
import numpy as np
import os
import tempfile

from app.core.security import get_current_user
from app.models.user import User
from app.schemas.plaka import PlakaResponse
from app.services.plaka_service import PlakaService

router = APIRouter(prefix="/plaka", tags=["Plaka Detection"])

# Plaka servisi instance'ı
plaka_service = PlakaService()

@router.post("/detect", response_model=PlakaResponse)
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
        marked_image, detections = plaka_service.detect_plates(image, confidence)
        
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

@router.post("/detect-image")
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
        marked_image, detections = plaka_service.detect_plates(image, confidence)
        
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

@router.get("/model-status")
async def get_model_status():
    """Model durumunu kontrol eder"""
    return plaka_service.get_model_status()
