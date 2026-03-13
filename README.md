# Screlia Studio AI App Public

> Gemini-tabanlı profesyonel akıllı uygulama. PyQt5 Desktop + Web Interface + React Dashboard

## Özellikler

### Core Features
- **Gemini AI Integration** - Google Gemini API ile AI sorgular
- **PyQt5 Desktop App** - Modern PyQt5 arayüzü
- **Web Interface** - Tailwind CSS ile tasarlanan web arayüzü
- **React Dashboard** - Canlı veri paneli React ile
- **SQLite Database** - Sorgu geçmiş ve favori yönetimi
- **Flask REST API** - Modern API endpoints
- **CORS Support** - Cross-origin istekler için destek

###  Veri Yönetimi
- Sorgu Geçmişi Tracking
-  Favori Sorgular
-  Arama Fonksiyonu
-  İstatistik Paneli
-  Token Takibi
-  JSON Dışa Aktarma

###  UI/UX
-  Tailwind CSS Framework
-  Modern Glass Effect Design
-  Responsive Design
-  Dark Mode Support
-  Smooth Animations
-  Professional Layout

##  Proje Yapısı

```
screlia-app/
├── main.py                 # PyQt5 Desktop App + Flask Server
├── database.py            # SQLite Manager
├── utils.py               # Utilities & Helpers
├── index.html             # Web Interface (Tailwind CSS)
├── react.html             # React Dashboard
├── index.css              # Fallback Styles
├── index.json             # Data Index
├── metadata.json          # App Metadata
├── config.json            # Configuration
├── requirements.txt       # Python Dependencies
└── screlia_app.log        # Application Logs
```

##  Kurulum & Çalıştırma

### 1. Gerekli Paketleri Yükle
```bash
pip install -r requirements.txt
```

### 2. Uygulamayı Çalıştır
```bash
python main.py
```

### 3. Tarayıcıda Aç
- **Web Interface**: http://localhost:5000
- **React Dashboard**: http://localhost:5000/react

##  API Endpoints

### Query Endpoints
- `POST /api/query` - Gemini'ye soru gönder
- `GET /api/history?limit=50` - Geçmişi getir
- `GET /api/search?q=term` - Geçmişte ara

### Data Endpoints
- `GET /api/index` - Index verisini getir
- `GET /api/metadata` - Metadata getir
- `GET /api/statistics` - İstatistikleri getir

### Favorites Endpoints
- `GET /api/favorites` - Favorileri listele
- `POST /api/favorites` - Favoriye ekle
- `DELETE /api/favorites/<query>` - Favoriden sil

### Settings & Export
- `GET /api/settings` - Ayarları getir
- `POST /api/settings` - Ayarları kaydet
- `GET /api/export?type=json` - Veri dışa aktar
- `GET /api/health` - Server sağlığını kontrol et

##  Konfigürasyon

`config.json` dosyasında uygulama ayarlarını yapabilirsiniz:

```json
{
  "app": {
    "name": "Screlia Studio AI App",
    "version": "2.0.0"
  },
  "server": {
    "host": "localhost",
    "port": 5000,
    "debug": false
  },
  "database": {
    "type": "sqlite",
    "path": "screlia_app.db"
  },
  "features": {
    "history_tracking": true,
    "dark_mode": true,
    "export_support": true
  }
}
```

##  Gemini API Integration

`main.py`'deki `/api/query` endpoint'ini Gemini API ile entegre etmek için:

```python
import google.generativeai as genai

@app.route('/api/query', methods=['POST'])
def api_query():
    data = request.get_json()
    query = data.get('query', '')
    
    # Gemini Integration
    model = genai.GenerativeModel('gemini-pro')
    response_text = model.generate_content(query).text
    
    # Database'e kaydet
    db.add_query_history(query, response_text, category)
    
    return jsonify({
        'query': query,
        'result': response_text
    })
```

Gemini API key'i ayarlamak için:
```bash
set GOOGLE_API_KEY=your_api_key_here
```

##  Veritabanı Şeması

### query_history
```sql
- id (INTEGER PRIMARY KEY)
- query (TEXT)
- response (TEXT)
- timestamp (DATETIME)
- category (TEXT)
- tokens_used (INTEGER)
- response_time (REAL)
```

### favorites
```sql
- id (INTEGER PRIMARY KEY)
- query (TEXT UNIQUE)
- response (TEXT)
- created_at (DATETIME)
```

### api_logs
```sql
- id (INTEGER PRIMARY KEY)
- endpoint (TEXT)
- method (TEXT)
- status_code (INTEGER)
- response_time (REAL)
- timestamp (DATETIME)
```

##  Tasarım

### Color Palette
- Primary: #667eea
- Secondary: #764ba2
- Success: #28a745
- Danger: #dc3545
- Light: #f8f9fa

### Typography
- Font: Poppins
- Sizes: 12px, 14px, 16px, 20px, 24px, 32px, 40px

##  Responsive Breakpoints
- Mobile: 320px - 768px
- Tablet: 768px - 1024px
- Desktop: 1024px+

##  Testing

### Manual Testing
1. Web Interface test: http://localhost:5000
2. React Dashboard test: http://localhost:5000/react
3. API test: `curl http://localhost:5000/api/health`

### Sample Queries
```python
import requests

# Query Example
response = requests.post('http://localhost:5000/api/query', 
    json={'query': 'Python nedir?', 'category': 'coding'})

# History Example
history = requests.get('http://localhost:5000/api/history?limit=10')

# Search Example
results = requests.get('http://localhost:5000/api/search?q=python')
```

##  Dependencies

```
Flask==2.3.2
Flask-CORS==4.0.0
PyQt5==5.15.9
PyQtWebEngine==5.15.6
requests==2.31.0
python-dotenv==1.0.0
google-generativeai==0.3.0  # (İsteğe bağlı)
```

##  Troubleshooting

### Server port zaten kullanımda
```bash
# Port 5000'i boşalt veya başka port kullan
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Database hatası
```bash
# Database'i resetle
del screlia_app.db
python main.py  # Otomatik olarak yeniden oluşturulacak
```

### PyQt5 penceresi açılmıyor
```bash
# PyQt5 paketini yeniden yükle
pip install --upgrade PyQt5 PyQtWebEngine
```

##  Logging

Uygulamanın logları `screlia_app.log` dosyasında saklanır:

```
2026-03-13 10:30:45,123 - __main__ - INFO - Database initialized
2026-03-13 10:30:46,456 - __main__ - INFO -  Flask server başarıyla başlatıldı!
```

##  Updates & Maintenance

- **v2.0.0** (2026-03-13) - Initial Pro Release
  - Tailwind CSS Integration
  - React Dashboard
  - SQLite Database
  - Advanced API
  - PyQt5 Desktop App
  - Export Features

##  Lisans

© 2026 Screlia Studio. Tüm haklar saklıdır.

## 👥 İletişim

-  Email: info@screlia-studio.com
-  Website: www.screlia.netlify.app
-  Support: support@screlia-studio.com

##  Frameworks

- Google Gemini API
- Tailwind CSS
- PyQt5 & Flask
- React.js Community
