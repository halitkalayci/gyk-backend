# GYK Backend - Plaka Tespiti API

Bu proje, YOLO modeli kullanarak plaka tespiti yapan bir FastAPI backend uygulamasıdır.

## Özellikler

- JWT tabanlı kimlik doğrulama
- Plaka tespiti için YOLO modeli entegrasyonu
- Görüntü yükleme ve işleme
- Tespit edilen plakaların koordinatlarını döndürme
- İşaretlenmiş görüntü döndürme

## Kurulum

1. Gerekli kütüphaneleri yükleyin:
```bash
pip install -r requirements.txt
```

2. `best.pt` model dosyasının proje kök dizininde olduğundan emin olun.

3. Uygulamayı başlatın:
```bash
python main.py
```

## API Endpoint'leri

### Kimlik Doğrulama

- `POST /register` - Yeni kullanıcı kaydı
- `POST /login` - Kullanıcı girişi
- `GET /me` - Mevcut kullanıcı bilgileri
- `GET /protected` - Korumalı endpoint örneği

### Plaka Tespiti

- `POST /detect-plates` - Plaka tespiti yapar ve JSON formatında sonuç döner
- `POST /detect-plates-image` - Plaka tespiti yapar ve işaretlenmiş görüntü döner
- `GET /model-status` - Model durumunu kontrol eder

## Kullanım Örnekleri

### 1. Kullanıcı Kaydı
```bash
curl -X POST "http://localhost:8000/register" \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "username": "testuser", "password": "password123"}'
```

### 2. Kullanıcı Girişi
```bash
curl -X POST "http://localhost:8000/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "password123"}'
```

### 3. Plaka Tespiti (JSON Sonuç)
```bash
curl -X POST "http://localhost:8000/detect-plates" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "file=@test_image.jpg" \
     -F "confidence=0.75"
```

### 4. Plaka Tespiti (İşaretlenmiş Görüntü)
```bash
curl -X POST "http://localhost:8000/detect-plates-image" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "file=@test_image.jpg" \
     -F "confidence=0.75" \
     --output detected_image.jpg
```

## Parametreler

- `file`: Yüklenecek görüntü dosyası (JPEG, PNG, vb.)
- `confidence`: Güven eşiği (0.0 - 1.0 arası, varsayılan: 0.75)

## Yanıt Formatları

### Plaka Tespiti JSON Yanıtı
```json
{
  "detections": [
    {
      "x1": 100.0,
      "y1": 200.0,
      "x2": 300.0,
      "y2": 250.0,
      "confidence": 0.85
    }
  ],
  "total_detections": 1,
  "message": "1 adet plaka tespit edildi"
}
```

## Güvenlik

- Tüm plaka tespiti endpoint'leri JWT token gerektirir
- Dosya türü kontrolü yapılır
- Güven eşiği parametresi ile yanlış tespitler azaltılabilir

## Hata Kodları

- `400`: Geçersiz dosya türü veya parametre
- `401`: Kimlik doğrulama hatası
- `500`: Sunucu hatası veya model hatası

## Notlar

- Model dosyası (`best.pt`) proje kök dizininde olmalıdır
- Geçici dosyalar otomatik olarak temizlenir
- API dokümantasyonu için `http://localhost:8000/docs` adresini ziyaret edin
