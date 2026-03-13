import sqlite3
from datetime import datetime
from utils import logger

class Database:
    """Enhanced database operations"""
    
    def __init__(self, db_path='screlia_app.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with all required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Query History
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS query_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                response TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                category TEXT DEFAULT 'general',
                tokens_used INTEGER,
                response_time REAL
            )
        ''')
        
        # Settings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT,
                data_type TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # API Logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                endpoint TEXT NOT NULL,
                method TEXT NOT NULL,
                status_code INTEGER,
                response_time REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Favorites
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL UNIQUE,
                response TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized")
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def add_query_history(self, query, response, category='general', tokens=0, response_time=0):
        """Add query to history"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO query_history 
               (query, response, category, tokens_used, response_time) 
               VALUES (?, ?, ?, ?, ?)''',
            (query, response, category, tokens, response_time)
        )
        conn.commit()
        conn.close()
    
    def get_query_history(self, limit=100, category=None):
        """Get query history"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if category:
            cursor.execute(
                '''SELECT id, query, response, timestamp, category, tokens_used, response_time 
                   FROM query_history 
                   WHERE category = ? 
                   ORDER BY timestamp DESC LIMIT ?''',
                (category, limit)
            )
        else:
            cursor.execute(
                '''SELECT id, query, response, timestamp, category, tokens_used, response_time 
                   FROM query_history 
                   ORDER BY timestamp DESC LIMIT ?''',
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
                'category': row[4],
                'tokens': row[5],
                'response_time': row[6]
            }
            for row in rows
        ]
    
    def search_queries(self, search_term):
        """Search in query history"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT id, query, response, timestamp, category 
               FROM query_history 
               WHERE query LIKE ? OR response LIKE ?
               ORDER BY timestamp DESC LIMIT 50''',
            (f'%{search_term}%', f'%{search_term}%')
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
    
    def add_favorite(self, query, response):
        """Add to favorites"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO favorites (query, response) VALUES (?, ?)',
                (query, response)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_favorites(self):
        """Get favorite queries"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, query, response, created_at FROM favorites ORDER BY created_at DESC'
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'query': row[1],
                'response': row[2],
                'created_at': row[3]
            }
            for row in rows
        ]
    
    def remove_favorite(self, query):
        """Remove from favorites"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM favorites WHERE query = ?', (query,))
        conn.commit()
        conn.close()
    
    def log_api_request(self, endpoint, method, status_code, response_time):
        """Log API request"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO api_logs 
               (endpoint, method, status_code, response_time) 
               VALUES (?, ?, ?, ?)''',
            (endpoint, method, status_code, response_time)
        )
        conn.commit()
        conn.close()
    
    def clear_history(self):
        """Clear all history"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM query_history')
        conn.commit()
        conn.close()
    
    def get_statistics(self):
        """Get database statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM query_history')
        total_queries = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM favorites')
        total_favorites = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(tokens_used) FROM query_history')
        total_tokens = cursor.fetchone()[0] or 0
        
        cursor.execute(
            'SELECT COUNT(*) FROM query_history WHERE timestamp > datetime("now", "-1 day")'
        )
        today_queries = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_queries': total_queries,
            'total_favorites': total_favorites,
            'total_tokens': total_tokens,
            'today_queries': today_queries
        }
