from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # JWT ayarları
    SECRET_KEY: str = "gyk-super-secret-key-2024-jwt-auth-system"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # YOLO model yolu
    MODEL_PATH: str = "best.pt"
    
    # Veritabanı ayarları
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5433/aiapp"
    
    class Config:
        env_file = ".env"

settings = Settings()
