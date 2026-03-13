import json
import logging
import os
from datetime import datetime
from functools import wraps
import sqlite3

# Logger Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('screlia_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ConfigManager:
    """Manage application configuration"""
    
    @staticmethod
    def load_config():
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Config yükleme hatası: {e}")
            return {}
    
    @staticmethod
    def save_config(config):
        try:
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Config kaydetme hatası: {e}")
            return False

class DatabaseManager:
    """Manage SQLite database operations"""
    
    DB_FILE = 'screlia_app.db'
    
    @staticmethod
    def init_db():
        """Initialize database with tables"""
        conn = sqlite3.connect(DatabaseManager.DB_FILE)
        cursor = conn.cursor()
        
        # Query History Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS query_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                response TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                category TEXT
            )
        ''')
        
        # User Settings Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # API Logs Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                endpoint TEXT,
                method TEXT,
                status_code INTEGER,
                response_time REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    
    @staticmethod
    def save_query(query, response, category='general'):
        """Save query to history"""
        try:
            conn = sqlite3.connect(DatabaseManager.DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO query_history (query, response, category) VALUES (?, ?, ?)',
                (query, response, category)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Query kaydetme hatası: {e}")
            return False
    
    @staticmethod
    def get_history(limit=50):
        """Get query history"""
        try:
            conn = sqlite3.connect(DatabaseManager.DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id, query, response, timestamp, category FROM query_history ORDER BY timestamp DESC LIMIT ?',
                (limit,)
            )
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'id': row[0],
                    'query': row[1],
                    'response': row[2],
                    'timestamp': row[3],
                    'category': row[4]
                }
                for row in rows
            ]
        except Exception as e:
            logger.error(f"History getirme hatası: {e}")
            return []
    
    @staticmethod
    def clear_history():
        """Clear all history"""
        try:
            conn = sqlite3.connect(DatabaseManager.DB_FILE)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM query_history')
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"History temizleme hatası: {e}")
            return False

class CacheManager:
    """Simple in-memory cache"""
    
    _cache = {}
    
    @staticmethod
    def set(key, value, ttl=300):
        """Set cache value"""
        CacheManager._cache[key] = {
            'value': value,
            'timestamp': datetime.now(),
            'ttl': ttl
        }
    
    @staticmethod
    def get(key):
        """Get cache value"""
        if key not in CacheManager._cache:
            return None
        
        cache_item = CacheManager._cache[key]
        elapsed = (datetime.now() - cache_item['timestamp']).total_seconds()
        
        if elapsed > cache_item['ttl']:
            del CacheManager._cache[key]
            return None
        
        return cache_item['value']
    
    @staticmethod
    def clear():
        """Clear all cache"""
        CacheManager._cache.clear()

class StatsManager:
    """Manage application statistics"""
    
    @staticmethod
    def get_stats():
        """Get application statistics"""
        try:
            conn = sqlite3.connect(DatabaseManager.DB_FILE)
            cursor = conn.cursor()
            
            # Total queries
            cursor.execute('SELECT COUNT(*) FROM query_history')
            total_queries = cursor.fetchone()[0]
            
            # Queries by category
            cursor.execute('SELECT category, COUNT(*) FROM query_history GROUP BY category')
            categories = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Recent queries
            cursor.execute('SELECT COUNT(*) FROM query_history WHERE timestamp > datetime("now", "-1 day")')
            recent_queries = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_queries': total_queries,
                'recent_queries': recent_queries,
                'categories': categories,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Stats getirme hatası: {e}")
            return {
                'total_queries': 0,
                'recent_queries': 0,
                'categories': {},
                'timestamp': datetime.now().isoformat()
            }

def load_metadata():
    """Load metadata from file"""
    try:
        with open('metadata.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Metadata yükleme hatası: {e}")
        return {}

def load_index():
    """Load index from file"""
    try:
        with open('index.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Index yükleme hatası: {e}")
        return {}

def export_to_json(data, filename):
    """Export data to JSON file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Veri {filename} dosyasına kaydedildi")
        return True
    except Exception as e:
        logger.error(f"Export hatası: {e}")
        return False

def export_to_csv(data, filename):
    """Export data to CSV file"""
    try:
        import csv
        if not data:
            return False
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        logger.info(f"Veri {filename} dosyasına kaydedildi")
        return True
    except Exception as e:
        logger.error(f"CSV export hatası: {e}")
        return False
