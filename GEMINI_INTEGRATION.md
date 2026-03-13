#  Gemini AI Integration Guide

##  Gemini API Setup

### 1. Google Cloud Project Oluştur

1. [Google Cloud Console](https://console.cloud.google.com/) aç
2. Yeni proje oluştur: "Screlia Studio"
3. Generative AI API'yi enable et

### 2. API Key Oluştur

1. Console'de **APIs & Services** → **Credentials** git
2. **Create Credentials** → **API Key** seç
3. Key'i kopyala ve güvenli yerde sakla

### 3. Python Paketi Yükle

```bash
pip install google-generativeai
```

##  Integration Kodu

### Basic Implementation

```python
import google.generativeai as genai

# API Key'i ayarla
genai.configure(api_key="YOUR_API_KEY")

# Model seç
model = genai.GenerativeModel('gemini-pro')

# Sorgu gönder
def query_gemini(prompt):
    response = model.generate_content(prompt)
    return response.text
```

### Flask Integration

```python
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel('gemini-pro')

@app.route('/api/query', methods=['POST'])
def api_query():
    data = request.get_json()
    query = data.get('query', '')
    category = data.get('category', 'general')
    
    try:
        # Gemini'ye soru gönder
        response = model.generate_content(query)
        result = response.text
        
        # Veritabanına kaydet
        db.add_query_history(query, result, category)
        
        return jsonify({
            'query': query,
            'result': result,
            'category': category,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

##  Advanced Features

### Stream Response (Canlı Yanıt)

```python
def stream_query(prompt):
    response = model.generate_content(prompt, stream=True)
    
    for chunk in response:
        print(chunk.text, end='', flush=True)
```

### Multi-turn Conversation

```python
chat = model.start_chat(history=[])

response = chat.send_message("Merhaba")
print(response.text)

response = chat.send_message("Python nedir?")
print(response.text)
```

### System Instructions

```python
model = genai.GenerativeModel(
    model_name='gemini-pro',
    system_instruction="""
    Sen Screlia Studio AI Assistant'sın.
    Türkçe cevaplar ver.
    Kısa ve öz cevaplar ver.
    """
)
```

### Custom Parameters

```python
generation_config = {
    "temperature": 0.7,
    "top_p": 0.9,
    "max_output_tokens": 2000,
}

model = genai.GenerativeModel(
    model_name='gemini-pro',
    generation_config=generation_config
)
```

##  Rate Limiting

```python
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_requests=100, time_window=3600):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = {}
    
    def is_allowed(self, client_id):
        now = datetime.now()
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        # Pencereyi temizle
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if (now - req_time).total_seconds() < self.time_window
        ]
        
        if len(self.requests[client_id]) < self.max_requests:
            self.requests[client_id].append(now)
            return True
        return False

limiter = RateLimiter(max_requests=100, time_window=3600)

@app.route('/api/query', methods=['POST'])
def api_query():
    client_id = request.remote_addr
    
    if not limiter.is_allowed(client_id):
        return jsonify({'error': 'Rate limit exceeded'}), 429
    
    # ... rest of code
```

##  Error Handling

```python
import google.generativeai as genai
from google.api_core import exceptions

@app.route('/api/query', methods=['POST'])
def api_query():
    data = request.get_json()
    query = data.get('query', '')
    
    try:
        response = model.generate_content(query)
        return jsonify({
            'query': query,
            'result': response.text,
            'status': 'success'
        })
    
    except exceptions.InvalidArgument as e:
        logger.error(f"Invalid argument: {e}")
        return jsonify({'error': 'Geçersiz sorgu'}), 400
    
    except exceptions.PermissionDenied as e:
        logger.error(f"Permission denied: {e}")
        return jsonify({'error': 'API key hatası'}), 403
    
    except exceptions.ResourceExhausted as e:
        logger.error(f"Quota exceeded: {e}")
        return jsonify({'error': 'API quota aşıldı'}), 429
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({'error': 'Beklenmeyen hata'}), 500
```

##  Caching Strategy

```python
from functools import lru_cache
from datetime import datetime, timedelta

class CacheManager:
    def __init__(self, ttl=300):
        self.cache = {}
        self.ttl = ttl
    
    def get(self, key):
        if key in self.cache:
            value, timestamp = self.cache[key]
            if (datetime.now() - timestamp).total_seconds() < self.ttl:
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key, value):
        self.cache[key] = (value, datetime.now())
    
    def clear(self):
        self.cache.clear()

cache = CacheManager(ttl=300)

@app.route('/api/query', methods=['POST'])
def api_query():
    query = request.json.get('query', '')
    
    # Cache'den kontrol et
    cached = cache.get(query)
    if cached:
        return jsonify(cached)
    
    # Gemini'dan al
    response = model.generate_content(query)
    result = response.text
    
    response_data = {
        'query': query,
        'result': result,
        'cached': False
    }
    
    # Cache'e kaydet
    cache.set(query, response_data)
    
    return jsonify(response_data)
```

##  Test Cases

```python
import unittest
import requests

class TestGeminiAPI(unittest.TestCase):
    def setUp(self):
        self.api_url = "http://localhost:5000/api/query"
    
    def test_query(self):
        payload = {
            'query': 'Python nedir?',
            'category': 'coding'
        }
        response = requests.post(self.api_url, json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn('result', response.json())
    
    def test_empty_query(self):
        payload = {'query': ''}
        response = requests.post(self.api_url, json=payload)
        self.assertEqual(response.status_code, 400)
    
    def test_rate_limit(self):
        for i in range(101):
            requests.post(self.api_url, json={'query': f'Test {i}'})
        
        response = requests.post(self.api_url, json={'query': 'Test'})
        self.assertEqual(response.status_code, 429)

if __name__ == '__main__':
    unittest.main()
```

## Model Options

```python
# Text Generation
model_pro = genai.GenerativeModel('gemini-pro')

# Vision (Image Analysis)
model_vision = genai.GenerativeModel('gemini-pro-vision')
```

## Async Operation

```python
import asyncio
import google.generativeai as genai

async def async_query(prompt):
    model = genai.GenerativeModel('gemini-pro')
    # Senkron API olduğu için thread pool ile işleme alınmalı
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None, 
        lambda: model.generate_content(prompt).text
    )
    return result
```

## Detailed Documentation

- [Google AI Documentation](https://ai.google.dev/)
- [Gemini API Docs](https://ai.google.dev/tutorials/python_quickstart)
- [Rate Limits](https://ai.google.dev/quotas)

## Best Practices

1. **API Key güvenliği**
   - Environment variable kullan
   - .env dosyasında sakla
   - Kodu commit'lemeden önce kontrol et

2. **Error Handling**
   - Her API çağrısını try-except'e koy
   - Rate limit hatalarını yönet
   - Timeout'ları ayarla

3. **Performance**
   - Yanıtları cache'le
   - Connection reuse et
   - Batch işlemleri gruplama

4. **Monitoring**
   - API usage'ı logla
   - Error rates'i takip et
   - Response time'ları ölç

## Common Issues

### Issue: "Invalid API key"
```python
# Çözüm: API key'i kontrol et
import os
api_key = os.getenv('GOOGLE_AI_API_KEY')
genai.configure(api_key=api_key)
```

### Issue: "Rate limit exceeded"
```python
# Çözüm: Rate limiting implement et
import time
time.sleep(1)  # Retry ile bekle
```

### Issue: "Model not found"
```python
# Çözüm: Doğru model adını kullan
model = genai.GenerativeModel('gemini-pro')  # ✓
# NOT: model_name='gemini'  # ✗
```

##  Support

- API Issues: https://issuetracker.google.com/issues?q=componentid:187172
- Community: https://github.com/google/generative-ai-python
