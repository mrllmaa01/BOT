import sqlite3
import datetime
from pathlib import Path

# Путь к файлу базы данных
DB_PATH = Path(__file__).parent / "bot_database.db"

def init_db():
    """Создает таблицы в базе данных, если их нет"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP
        )
    ''')
    
    # Таблица сообщений
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message_text TEXT,
            emotion TEXT,
            sentiment REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ База данных инициализирована")

def add_user(user_id, username, first_name, last_name):
    """Добавляет нового пользователя или обновляет время активности"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO users (user_id, username, first_name, last_name, last_active)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_id) DO UPDATE SET
            username = excluded.username,
            first_name = excluded.first_name,
            last_name = excluded.last_name,
            last_active = CURRENT_TIMESTAMP
    ''', (user_id, username, first_name, last_name))
    
    conn.commit()
    conn.close()

def save_message(user_id, message_text):
    """Сохраняет сообщение пользователя и возвращает его ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO messages (user_id, message_text, created_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
    ''', (user_id, message_text))
    
    message_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return message_id

def update_message_emotion(message_id, emotion, confidence):
    """Обновляет сообщение с результатами анализа эмоций"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE messages 
        SET emotion = ?, sentiment = ? 
        WHERE id = ?
    ''', (emotion, confidence, message_id))
    
    conn.commit()
    conn.close()

def get_user_history(user_id, limit=10):
    """Получает последние сообщения пользователя"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT message_text, emotion, sentiment, created_at
        FROM messages
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    ''', (user_id, limit))
    
    results = cursor.fetchall()
    conn.close()
    return results

def save_diary_entry(user_id, emotion, message_text):
    """Сохраняет запись в дневник"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Создаём таблицу для дневника, если её нет
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS diary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            emotion TEXT,
            message_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        INSERT INTO diary (user_id, emotion, message_text, created_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    ''', (user_id, emotion, message_text))
    
    conn.commit()
    conn.close()
    return cursor.lastrowid

def get_diary_entries(user_id, limit=10):
    """Получает последние записи из дневника"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT emotion, message_text, created_at
        FROM diary
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    ''', (user_id, limit))
    
    results = cursor.fetchall()
    conn.close()
    return results

def get_emotion_stats(user_id):
    """Получает статистику эмоций пользователя"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT emotion, COUNT(*) as count
        FROM messages
        WHERE user_id = ? AND emotion IS NOT NULL
        GROUP BY emotion
        ORDER BY count DESC
    ''', (user_id,))
    
    results = cursor.fetchall()
    
    cursor.execute('''
        SELECT COUNT(*) FROM messages WHERE user_id = ?
    ''', (user_id,))
    
    total = cursor.fetchone()[0]
    conn.close()
    
    return results, total

from datetime import datetime, timedelta

def get_week_emotions(user_id):
    """Получает статистику эмоций за последние 7 дней"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Дата 7 дней назад
    week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute('''
        SELECT emotion, created_at
        FROM messages
        WHERE user_id = ? AND created_at >= ? AND emotion IS NOT NULL
        ORDER BY created_at
    ''', (user_id, week_ago))
    
    results = cursor.fetchall()
    conn.close()
    return results
    return results

# При запуске файла создаем таблицы
if __name__ == "__main__":
    init_db()

    