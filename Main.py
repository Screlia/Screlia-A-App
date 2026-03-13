import sys
import json
import os
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTabWidget, QLineEdit, QPushButton, 
                             QTextEdit, QLabel, QMessageBox, QScrollArea, 
                             QListWidget, QListWidgetItem, QComboBox, QCheckBox,
                             QSpinBox, QDoubleSpinBox, QFileDialog, QProgressBar,
                             QSplitter, QTreeWidget, QTreeWidgetItem)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QUrl, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QPixmap, QColor
from flask import Flask, jsonify, request
from flask_cors import CORS
from threading import Thread
import logging
from datetime import datetime
from database import Database
from utils import ConfigManager, CacheManager, StatsManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask App Setup
app = Flask(__name__)
CORS(app)

# Initialize Database
db = Database()

def load_metadata():
    try:
        with open('metadata.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def load_index():
    try:
        with open('index.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

# =========== API Routes ===========

@app.route('/api/metadata')
def api_metadata():
    return jsonify(load_metadata())

@app.route('/api/index')
def api_index():
    return jsonify(load_index())

@app.route('/api/query', methods=['POST'])
def api_query():
    start_time = time.time()
    data = request.get_json()
    query = data.get('query', '')
    category = data.get('category', 'general')
    
    response_text = f"Gemini API Response: {query}"
    response_time = time.time() - start_time
    
    # Save to history
    db.add_query_history(query, response_text, category, response_time=response_time)
    
    response = {
        'id': 1,
        'query': query,
        'result': response_text,
        'category': category,
        'timestamp': datetime.now().isoformat(),
        'response_time': response_time
    }
    return jsonify(response)

@app.route('/api/history')
def api_history():
    limit = request.args.get('limit', 50, type=int)
    category = request.args.get('category', None)
    history = db.get_query_history(limit, category)
    return jsonify({'history': history, 'count': len(history)})

@app.route('/api/search', methods=['GET'])
def api_search():
    search_term = request.args.get('q', '')
    if not search_term:
        return jsonify({'error': 'Search term required'}), 400
    
    results = db.search_queries(search_term)
    return jsonify({'results': results, 'count': len(results)})

@app.route('/api/favorites', methods=['GET'])
def api_favorites():
    favorites = db.get_favorites()
    return jsonify({'favorites': favorites})

@app.route('/api/favorites', methods=['POST'])
def api_add_favorite():
    data = request.get_json()
    query = data.get('query', '')
    response = data.get('response', '')
    
    success = db.add_favorite(query, response)
    return jsonify({'success': success, 'message': 'Added to favorites' if success else 'Already favorite'})

@app.route('/api/favorites/<query>', methods=['DELETE'])
def api_remove_favorite(query):
    db.remove_favorite(query)
    return jsonify({'success': True})

@app.route('/api/statistics')
def api_statistics():
    stats = db.get_statistics()
    return jsonify(stats)

@app.route('/api/settings', methods=['GET'])
def api_settings():
    config = ConfigManager.load_config()
    return jsonify(config)

@app.route('/api/settings', methods=['POST'])
def api_save_settings():
    data = request.get_json()
    success = ConfigManager.save_config(data)
    return jsonify({'success': success})

@app.route('/api/export', methods=['GET'])
def api_export():
    export_type = request.args.get('type', 'json')
    history = db.get_query_history(limit=1000)
    
    if export_type == 'json':
        filename = f'export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    
    return jsonify({'success': True, 'filename': filename})

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0'
    })

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

def run_flask():
    app.run(debug=False, port=5000, host='localhost', use_reloader=False, threaded=True)

# PyQt5 Main Application
class ScreliaStudioApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = ConfigManager.load_config()
        self.dark_mode = False
        self.init_ui()
        self.start_flask_server()
        
    def init_ui(self):
        self.setWindowTitle("Screlia Studio AI App v2.0 - Pro Edition")
        self.setGeometry(100, 100, 1400, 850)
        
        # Apply stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 8px 20px;
                margin-right: 2px;
                border-radius: 4px 4px 0 0;
            }
            QTabBar::tab:selected {
                background-color: #667eea;
                color: white;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 4px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #667eea;
            }
            QPushButton {
                background-color: #667eea;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
                cursor: pointer;
            }
            QPushButton:hover {
                background-color: #764ba2;
            }
            QPushButton:pressed {
                background-color: #5568d3;
            }
            QTextEdit {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                font-family: 'Courier New';
                font-size: 11px;
            }
            QLabel {
                color: #333;
            }
        """)
        
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        
        # Header
        header = QLabel("🤖 Screlia Studio AI App - PyQt5 Desktop")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)
        
        # Tabs
        tabs = QTabWidget()
        
        # Tab 1: Gemini Query
        tab1 = self.create_query_tab()
        tabs.addTab(tab1, "💬 Gemini Sorgusu")
        
        # Tab 2: Data Viewer
        tab2 = self.create_data_tab()
        tabs.addTab(tab2, "📊 Veri Görüntüleyici")
        
        # Tab 3: History
        tab3 = self.create_history_tab()
        tabs.addTab(tab3, "📜 Geçmiş")
        
        # Tab 4: Favorites
        tab4 = self.create_favorites_tab()
        tabs.addTab(tab4, "⭐ Favoriler")
        
        # Tab 5: Web View
        tab5 = self.create_web_tab()
        tabs.addTab(tab5, "🌐 Web Arayüzü")
        
        main_layout.addWidget(tabs)
        central_widget.setLayout(main_layout)
        
    def create_query_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Gemini AI'ye Soru Sor")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Query Input
        query_layout = QHBoxLayout()
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("Sorunuzu yazın...")
        self.query_input.returnPressed.connect(self.submit_query)
        
        submit_btn = QPushButton("Gönder")
        submit_btn.clicked.connect(self.submit_query)
        
        query_layout.addWidget(self.query_input)
        query_layout.addWidget(submit_btn)
        layout.addLayout(query_layout)
        
        # Response Area
        response_label = QLabel("Cevap:")
        response_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(response_label)
        
        self.response_text = QTextEdit()
        self.response_text.setReadOnly(True)
        self.response_text.setText("Cevap burada gösterilecek...")
        layout.addWidget(self.response_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        load_meta_btn = QPushButton("📂 Metadata Yükle")
        load_meta_btn.clicked.connect(self.load_metadata)
        
        load_index_btn = QPushButton("📑 Index Yükle")
        load_index_btn.clicked.connect(self.load_index)
        
        clear_btn = QPushButton("🗑️ Temizle")
        clear_btn.clicked.connect(lambda: self.response_text.clear())
        
        button_layout.addWidget(load_meta_btn)
        button_layout.addWidget(load_index_btn)
        button_layout.addWidget(clear_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        widget.setLayout(layout)
        return widget
    
    def create_data_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("📊 İstatistik ve Veri Paneli")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Stats
        stats_layout = QHBoxLayout()
        
        self.stat_pages = QLabel("📄 Sayfalar: 0")
        self.stat_services = QLabel("🔌 Servisler: 0")
        self.stat_features = QLabel("✨ Özellikler: 0")
        self.stat_queries = QLabel("💬 Sorgular: 0")
        
        for label in [self.stat_pages, self.stat_services, self.stat_features, self.stat_queries]:
            label.setFont(QFont("Arial", 11, QFont.Bold))
            label.setStyleSheet("background-color: #667eea; color: white; padding: 15px; border-radius: 5px;")
            stats_layout.addWidget(label)
        
        layout.addLayout(stats_layout)
        
        # Data Display
        data_label = QLabel("Veri Ayrıntıları:")
        data_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(data_label)
        
        self.data_text = QTextEdit()
        self.data_text.setReadOnly(True)
        layout.addWidget(self.data_text)
        
        # Refresh Button
        refresh_btn = QPushButton("🔄 Verileri Yenile")
        refresh_btn.clicked.connect(self.refresh_data)
        layout.addWidget(refresh_btn)
        
        widget.setLayout(layout)
        return widget
    
    def create_history_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("📜 Sorgu Geçmişi")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        search_layout = QHBoxLayout()
        search_input = QLineEdit()
        search_input.setPlaceholderText("Geçmişte ara...")
        search_btn = QPushButton("🔍 Ara")
        search_layout.addWidget(search_input)
        search_layout.addWidget(search_btn)
        layout.addLayout(search_layout)
        
        self.history_list = QListWidget()
        layout.addWidget(self.history_list)
        
        clear_btn = QPushButton("🗑️ Geçmişi Temizle")
        layout.addWidget(clear_btn)
        
        widget.setLayout(layout)
        return widget
    
    def create_favorites_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("⭐ Favori Sorgular")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        self.favorites_list = QListWidget()
        layout.addWidget(self.favorites_list)
        
        button_layout = QHBoxLayout()
        remove_btn = QPushButton("❌ Sil")
        export_btn = QPushButton("📥 Dışa Aktar")
        button_layout.addWidget(remove_btn)
        button_layout.addWidget(export_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_web_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("🌐 Web Arayüzü (http://localhost:5000)")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Web Engine View
        self.web_view = QWebEngineView()
        self.web_view.load(QUrl("http://localhost:5000"))
        layout.addWidget(self.web_view)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        main_btn = QPushButton("Ana Sayfa")
        main_btn.clicked.connect(lambda: self.web_view.load(QUrl("http://localhost:5000")))
        
        react_btn = QPushButton("React Dashboard")
        react_btn.clicked.connect(lambda: self.web_view.load(QUrl("http://localhost:5000/react")))
        
        refresh_btn = QPushButton("🔄 Yenile")
        refresh_btn.clicked.connect(lambda: self.web_view.reload())
        
        button_layout.addWidget(main_btn)
        button_layout.addWidget(react_btn)
        button_layout.addWidget(refresh_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        layout.addWidget(self.web_view)
        
        widget.setLayout(layout)
        return widget
    
    def submit_query(self):
        query = self.query_input.text()
        if not query.strip():
            QMessageBox.warning(self, "Uyarı", "Lütfen bir soru yazın!")
            return
        
        self.response_text.setText("⏳ Gemini işleniyor...")
        
        import requests
        try:
            response = requests.post('http://localhost:5000/api/query', 
                                    json={'query': query})
            data = response.json()
            self.response_text.setText(f"❓ Soru: {data['query']}\n\n✅ Cevap:\n{data['result']}")
            self.query_input.clear()
        except Exception as e:
            self.response_text.setText(f"❌ Hata: {str(e)}")
    
    def load_metadata(self):
        try:
            with open('metadata.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.response_text.setText(json.dumps(data, indent=2, ensure_ascii=False))
        except Exception as e:
            self.response_text.setText(f"❌ Hata: {str(e)}")
    
    def load_index(self):
        try:
            with open('index.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.response_text.setText(json.dumps(data, indent=2, ensure_ascii=False))
        except Exception as e:
            self.response_text.setText(f"❌ Hata: {str(e)}")
    
    def refresh_data(self):
        try:
            import requests
            index_data = requests.get('http://localhost:5000/api/index').json()
            meta_data = requests.get('http://localhost:5000/api/metadata').json()
            
            pages = len(index_data.get('pages', []))
            services = len(index_data.get('services', []))
            features = len(meta_data.get('features', []))
            
            self.stat_pages.setText(f"📄 Sayfalar: {pages}")
            self.stat_services.setText(f"🔌 Servisler: {services}")
            self.stat_features.setText(f"✨ Özellikler: {features}")
            
            data_text = f"""
📦 Uygulama: {meta_data.get('app_name', 'N/A')}
📌 Versiyon: {meta_data.get('version', 'N/A')}
🤖 AI Sağlayıcı: {meta_data.get('services', {}).get('ai_provider', 'N/A')}

📄 Sayfalar ({pages}):
{json.dumps(index_data.get('pages', []), indent=2, ensure_ascii=False)}

🔌 Servisler ({services}):
{json.dumps(index_data.get('services', []), indent=2, ensure_ascii=False)}

✨ Özellikler:
{json.dumps(meta_data.get('features', []), indent=2, ensure_ascii=False)}
            """
            self.data_text.setText(data_text)
        except Exception as e:
            self.data_text.setText(f"❌ Veri yüklenemedi: {str(e)}")
    
    def start_flask_server(self):
        # Start Flask in a separate thread
        flask_thread = Thread(target=run_flask, daemon=True)
        flask_thread.start()
        
        # Wait for server to start
        QTimer.singleShot(2000, self.on_server_started)
    
    def on_server_started(self):
        try:
            import requests
            requests.get('http://localhost:5000/api/metadata')
            logging.info("✅ Flask server başarıyla başlatıldı!")
            self.refresh_data()
        except:
            logging.warning("⚠️ Server henüz hazır değil...")
            QTimer.singleShot(1000, self.on_server_started)

if __name__ == '__main__':
    qt_app = QApplication(sys.argv)
    window = ScreliaStudioApp()
    window.show()
    sys.exit(qt_app.exec_())
