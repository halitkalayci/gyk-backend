from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth_router, users_router, plaka_router
from app.utils.file_utils import cleanup_temp_files

# FastAPI uygulaması oluştur
app = FastAPI(
    title="GYK Backend API", 
    description="JWT Auth ile CRUD API ve Plaka Tespiti", 
    version="1.0.0"
)

# CORS middleware ekle
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Güvenlik için production'da spesifik origin'ler belirtin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router'ları ekle
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(plaka_router)

# Ana endpoint
@app.get("/")
async def root():
    """API ana sayfası"""
    return {"message": "GYK Backend API'ye hoş geldiniz!"}

# Korumalı endpoint örneği
@app.get("/protected")
async def protected_route():
    """Sadece giriş yapmış kullanıcıların erişebileceği endpoint"""
    return {
        "message": "Bu korumalı bir endpoint!",
        "note": "Bu endpoint artık /users/me endpoint'i ile değiştirildi"
    }

# Uygulama başlatıldığında geçici dosyaları temizle
cleanup_temp_files()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)