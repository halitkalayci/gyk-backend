import cv2
import numpy as np
from ultralytics import YOLO
from fastapi import HTTPException, status
from app.schemas.plaka import PlakaDetection
from app.core.config import settings

class PlakaService:
    def __init__(self):
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """YOLO modelini yükle"""
        try:
            self.model = YOLO(settings.MODEL_PATH)
            print(f"Model başarıyla yüklendi: {settings.MODEL_PATH}")
        except Exception as e:
            print(f"Model yüklenirken hata oluştu: {e}")
            self.model = None
    
    def detect_plates(self, image_array: np.ndarray, confidence_threshold: float = 0.75):
        """
        Görüntüde plaka tespiti yapar
        
        Args:
            image_array: OpenCV formatında görüntü
            confidence_threshold: Güven eşiği (varsayılan: 0.75)
        
        Returns:
            Tuple: (işaretlenmiş görüntü, tespit listesi)
        """
        if self.model is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Model yüklenemedi"
            )
        
        try:
            # YOLO ile tahmin yap
            result = self.model.predict(image_array, verbose=False)
            
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
    
    def get_model_status(self):
        """Model durumunu kontrol eder"""
        return {
            "model_loaded": self.model is not None,
            "model_path": settings.MODEL_PATH,
            "status": "Model yüklendi" if self.model is not None else "Model yüklenemedi"
        }
