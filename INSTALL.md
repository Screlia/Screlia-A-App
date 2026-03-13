#  Screlia Studio - Yükleme Rehberi

##  Kurulum Adımları

### Step 1: Python Paketlerini Yükle
```bash
pip install -r requirements.txt
```

### Step 2: Uygulamayı Başlat
```bash
python main.py
```

### Step 3: İnterfacelere Erişim

#### PyQt5 Desktop App
- Otomatik olarak açılacak
- İçinde Flask server'da çalışıyor
- 5 sekme ile tüm özelliklere erişim

#### Web Interface
- http://localhost:5000
- Tailwind CSS ile tasarlanmış modern arayüz
- 5 tab: Sorgular, Geçmiş, Favoriler, Ara, İstatistikler

#### React Dashboard
- http://localhost:5000/react
- Canlı veri paneli
- Otomatik 5 saniyede yenilenir

##  Gemini API Setup (İsteğe Bağlı)

Eğer Gemini API kullanmak istiyorsanız:

1. [Google Console](https://console.cloud.google.com/) git
2. Generative AI API'yi enable et
3. API Key oluştur
4. main.py'de entegrasyon yap

```python
import google.generativeai as genai
genai.configure(api_key="YOUR_KEY")
```

Detaylı bilgi için: `GEMINI_INTEGRATION.md`

##  Kontrol Listesi

- [ ] Python 3.8+ kurulu mu?
- [ ] requirements.txt yüklendi mi?
- [ ] main.py çalışıyor mu?
- [ ] PyQt5 penceresi açıldı mı?
- [ ] http://localhost:5000 erişilebiliyor mu?
- [ ] http://localhost:5000/react erişilebiliyor mu?

##  Sorun Giderme

### Port zaten kullanılıyor
```bash
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Database hatasında
```bash
del screlia_app.db
python main.py
```

### PyQt5 hatası
```bash
pip install --upgrade PyQt5 PyQtWebEngine
```

##  Proje Dosyaları

 `main.py` - Flask + PyQt5 Ana Uygulama
 `database.py` - SQLite İşlemleri
 `utils.py` - Yardımcı Fonksiyonlar
 `index.html` - Web Arayüzü (Tailwind)
 `react.html` - React Dashboard
 `index.css` - Fallback Stiller
`config.json` - Yapılandırma
 `metadata.json` - Uygulama MetaverisI
 `index.json` - Data Index
 `requirements.txt` - Python Paketleri
 `README.md` - Tam Dokümantasyon
 `GEMINI_INTEGRATION.md` - Gemini API Rehberi
 `.gitignore` - Git Ignore Kuralları

##  Özellikler Özeti

| Feature | Status | Location |
|---------|--------|----------|
|  Gemini Sorguları |  | All Interfaces |
|  Sorgu Geçmişi |  | Web / Desktop / React |
|  Favoriler |  | Web / Desktop / React |
|  Arama |  | Web / React |
|  İstatistikler | | Web / Desktop / React |
|  Dışa Aktarma |  | Web / Desktop |
|  Database |  | SQLite |
|  API |  | Flask REST |

##  Teknoloji Stack

- **Backend**: Python Flask + SQLite
- **Desktop**: PyQt5 + QWebEngine
- **Frontend**: HTML5 + JavaScript + Tailwind CSS
- **Dashboard**: React 18 + Tailwind CSS
- **Styling**: Tailwind CSS v3
- **API**: REST API + CORS

##  Dokümantasyon

- `README.md` - Tam Project Dokümantasyonu
- `GEMINI_INTEGRATION.md` - Gemini API Setup & Integration
- `INSTALL.md` - Bu dosya (Kurulum Rehberi)

##  Başlangıç İpuçları

1. **İlk kez çalıştırırında**
   - Database otomatik oluşturulacak
   - Server 2 saniye sonra başlayacak
   - Tüm interfaces otomatik açılacak

2. **Veri tabanı**
   - Sorguları otomatik kaydeder
   - Favori yönetimi eksik
   - JSON dışa aktarma mevcut

3. **API Testleri**
   ```bash
   curl http://localhost:5000/api/health
   curl http://localhost:5000/api/statistics
   ```

4. **Logging**
   - `screlia_app.log` dosyasında loglar
   - İlk çalıştırmada kontrol et

## Next Steps

1. Gemini API'yi entegre et
2. Daha fazla özellik ekle
3. Database'i genişlet
4. Authentication ekle
5. Multi-user support ekle

##  İletişim

Screlia Studio
- 🌐 www.screlia-studio.com
- 📧 info@screlia-studio.com

##  Lisans
© 2026 GNU project.tüm hakları saklıdır
© 2026 Screlia Studio. Tüm haklar saklıdır.
