# GYK Backend - Plaka Tespiti API

Bu proje, YOLO modeli kullanarak plaka tespiti yapan bir FastAPI backend uygulamasıdır.

## Özellikler

- JWT tabanlı kimlik doğrulama
- PostgreSQL veritabanı entegrasyonu (SQLAlchemy ORM)
- Plaka tespiti için YOLO modeli entegrasyonu
- Görüntü yükleme ve işleme
- Tespit edilen plakaların koordinatlarını döndürme
- İşaretlenmiş görüntü döndürme
- Kullanıcı yönetimi (CRUD işlemleri)

## Kurulum

### 1. PostgreSQL Veritabanı Kurulumu

PostgreSQL sunucusunun çalıştığından ve `aiapp` veritabanının oluşturulduğundan emin olun:

```sql
-- PostgreSQL'de veritabanı oluştur
CREATE DATABASE aiapp;
```

### 2. Python Bağımlılıkları

Gerekli kütüphaneleri yükleyin:
```bash
pip install -r requirements.txt
```

### 3. Veritabanı Tablolarını Oluştur

```bash
python create_tables.py
```

### 4. Veritabanı Bağlantısını Test Et

```bash
python test_db.py
```

### 5. Model Dosyası

`best.pt` model dosyasının proje kök dizininde olduğundan emin olun.

### 6. Uygulamayı Başlat

```bash
python main.py
```

## Proje Yapısı

```
gyk-backend/
├── app/
│   ├── api/                 # API endpoint'leri
│   │   ├── auth.py         # Kimlik doğrulama
│   │   ├── users.py        # Kullanıcı yönetimi
│   │   └── plaka.py        # Plaka tespiti
│   ├── core/               # Temel ayarlar
│   │   ├── config.py       # Konfigürasyon
│   │   └── security.py     # Güvenlik fonksiyonları
│   ├── crud/               # Veritabanı işlemleri
│   │   └── user.py         # User CRUD işlemleri
│   ├── database/           # Veritabanı bağlantısı
│   │   └── database.py     # SQLAlchemy ayarları
│   ├── models/             # Veritabanı modelleri
│   │   └── user.py         # User modeli
│   ├── schemas/            # Pydantic şemaları
│   │   ├── user.py         # User şemaları
│   │   ├── token.py        # Token şemaları
│   │   └── plaka.py        # Plaka şemaları
│   ├── services/           # İş mantığı servisleri
│   │   └── plaka_service.py # Plaka tespiti servisi
│   └── utils/              # Yardımcı fonksiyonlar
│       └── file_utils.py   # Dosya işlemleri
├── main.py                 # Ana uygulama
├── create_tables.py        # Tablo oluşturma scripti
├── test_db.py             # Veritabanı test scripti
└── requirements.txt        # Bağımlılıklar
```

## API Endpoint'leri

### Kimlik Doğrulama (`/auth`)

- `POST /auth/register` - Yeni kullanıcı kaydı
- `POST /auth/login` - Kullanıcı girişi

### Kullanıcı Yönetimi (`/users`)

- `GET /users/me` - Mevcut kullanıcı bilgileri
- `GET /users/` - Tüm kullanıcıları listele
- `GET /users/{user_id}` - Belirli bir kullanıcıyı getir
- `PUT /users/{user_id}` - Kullanıcı bilgilerini güncelle
- `DELETE /users/{user_id}` - Kullanıcı hesabını sil

### Plaka Tespiti (`/plaka`)

- `POST /plaka/detect` - Plaka tespiti yapar ve JSON formatında sonuç döner
- `POST /plaka/detect-image` - Plaka tespiti yapar ve işaretlenmiş görüntü döner
- `GET /plaka/model-status` - Model durumunu kontrol eder

## Kullanım Örnekleri

### 1. Kullanıcı Kaydı
```bash
curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "username": "testuser", "password": "password123"}'
```

### 2. Kullanıcı Girişi
```bash
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "password123"}'
```

### 3. Kullanıcı Bilgilerini Getir
```bash
curl -X GET "http://localhost:8000/users/me" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Plaka Tespiti (JSON Sonuç)
```bash
curl -X POST "http://localhost:8000/plaka/detect" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "file=@test_image.jpg" \
     -F "confidence=0.75"
```

### 5. Plaka Tespiti (İşaretlenmiş Görüntü)
```bash
curl -X POST "http://localhost:8000/plaka/detect-image" \
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

## Veritabanı Yapılandırması

### Bağlantı Bilgileri
- **Host**: localhost
- **Port**: 5433
- **Database**: aiapp
- **Username**: postgres
- **Password**: postgres

### Tablo Yapısı

#### Users Tablosu
- `id` (String, Primary Key): Kullanıcı ID'si
- `email` (String, Unique): Email adresi
- `username` (String): Kullanıcı adı
- `hashed_password` (String): Hash'lenmiş şifre
- `is_active` (Boolean): Hesap aktif mi?
- `created_at` (DateTime): Oluşturulma tarihi
- `updated_at` (DateTime): Güncellenme tarihi

## Notlar

- Model dosyası (`best.pt`) proje kök dizininde olmalıdır
- Geçici dosyalar otomatik olarak temizlenir
- API dokümantasyonu için `http://localhost:8000/docs` adresini ziyaret edin
- Veritabanı bağlantısı için PostgreSQL sunucusunun çalışır durumda olması gerekir
