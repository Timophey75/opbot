import sqlite3
import json
import random
from datetime import datetime
from typing import List, Dict, Optional

class Database:
    def __init__(self, db_path: str = 'schedule.db'):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Таблица пользователей (админов и операторов)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                user_id INTEGER UNIQUE,
                name TEXT NOT NULL,
                surname TEXT NOT NULL,
                code TEXT UNIQUE NOT NULL,
                color_emoji TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Таблица мероприятий
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                title TEXT NOT NULL,
                period TEXT NOT NULL,
                operator_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (operator_id) REFERENCES users(id)
            )
        ''')

        # Таблица отказов от смен
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shift_refusals (
                id INTEGER PRIMARY KEY,
                operator_id INTEGER NOT NULL,
                event_id INTEGER NOT NULL,
                reason TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (operator_id) REFERENCES users(id),
                FOREIGN KEY (event_id) REFERENCES events(id)
            )
        ''')

        # Таблица напоминаний
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                time_morning TEXT DEFAULT '10:00',
                time_evening TEXT DEFAULT '19:00',
                enabled INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        conn.commit()
        conn.close()

    # Пользователи
    def create_user(self, user_id: int, name: str, surname: str, code: str, is_admin: int = 0) -> int:
        colors = ['🟦', '🟧', '🟥', '⬛️', '🟩', '🟪', '🟨', '🟫']
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Проверяем сколько доступных цветов
        used_colors = cursor.execute('SELECT color_emoji FROM users').fetchall()
        used = {c[0] for c in used_colors if c[0]}
        available = [c for c in colors if c not in used]
        
        color = random.choice(available) if available else random.choice(colors)
        
        cursor.execute('''
            INSERT INTO users (user_id, name, surname, code, color_emoji, is_admin)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, name, surname, code, color, is_admin))
        
        conn.commit()
        user_id_db = cursor.lastrowid
        conn.close()
        return user_id_db

    def get_user_by_code(self, code: str) -> Optional[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE code = ?', (code,))
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None

    def get_user_by_tg_id(self, tg_user_id: int) -> Optional[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (tg_user_id,))
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None

    def get_all_users(self) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users ORDER BY id')
        results = cursor.fetchall()
        conn.close()
        return [dict(r) for r in results]

    def get_all_operators(self) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE is_admin = 0 ORDER BY name')
        results = cursor.fetchall()
        conn.close()
        return [dict(r) for r in results]

    def update_user(self, user_id: int, name: str, surname: str) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET name = ?, surname = ? WHERE id = ?
        ''', (name, surname, user_id))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success

    def delete_user(self, user_id: int) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success

    def generate_operator_code(self) -> str:
        """Генерирует уникальный 4-значный код"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        while True:
            code = str(random.randint(1000, 9999))
            cursor.execute('SELECT id FROM users WHERE code = ?', (code,))
            if not cursor.fetchone():
                conn.close()
                return code

    # Мероприятия
    def create_event(self, date: str, time: str, title: str, period: str, operator_id: Optional[int] = None) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO events (date, time, title, period, operator_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (date, time, title, period, operator_id))
        conn.commit()
        event_id = cursor.lastrowid
        conn.close()
        return event_id

    def get_events_by_date(self, date: str) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM events WHERE date = ? ORDER BY period, time', (date,))
        results = cursor.fetchall()
        conn.close()
        return [dict(r) for r in results]

    def get_events_by_date_and_period(self, date: str, period: str) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM events WHERE date = ? AND period = ?
        ''', (date, period))
        results = cursor.fetchall()
        conn.close()
        return [dict(r) for r in results]

    def update_event(self, event_id: int, title: str = None, time: str = None, operator_id: int = None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if title:
            cursor.execute('UPDATE events SET title = ? WHERE id = ?', (title, event_id))
        if time:
            cursor.execute('UPDATE events SET time = ? WHERE id = ?', (time, event_id))
        if operator_id:
            cursor.execute('UPDATE events SET operator_id = ? WHERE id = ?', (operator_id, event_id))
        
        conn.commit()
        conn.close()

    def delete_event(self, event_id: int) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM events WHERE id = ?', (event_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success

    def assign_operator_to_event(self, event_id: int, operator_id: int):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE events SET operator_id = ? WHERE id = ?', (operator_id, event_id))
        conn.commit()
        conn.close()

    # Отказы от смен
    def create_refusal(self, operator_id: int, event_id: int, reason: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO shift_refusals (operator_id, event_id, reason)
            VALUES (?, ?, ?)
        ''', (operator_id, event_id, reason))
        conn.commit()
        conn.close()

    def get_refusals(self) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT sf.*, u.name, u.surname, e.date, e.time, e.title, e.period
            FROM shift_refusals sf
            JOIN users u ON sf.operator_id = u.id
            JOIN events e ON sf.event_id = e.id
            ORDER BY sf.created_at DESC
        ''')
        results = cursor.fetchall()
        conn.close()
        return [dict(r) for r in results]

    # Напоминания
    def create_or_update_reminder(self, user_id: int, reminder_type: str, time_morning: str = '10:00', time_evening: str = '19:00', enabled: int = 1):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id FROM reminders WHERE user_id = ? AND type = ?
        ''', (user_id, reminder_type))
        
        if cursor.fetchone():
            cursor.execute('''
                UPDATE reminders 
                SET time_morning = ?, time_evening = ?, enabled = ?
                WHERE user_id = ? AND type = ?
            ''', (time_morning, time_evening, enabled, user_id, reminder_type))
        else:
            cursor.execute('''
                INSERT INTO reminders (user_id, type, time_morning, time_evening, enabled)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, reminder_type, time_morning, time_evening, enabled))
        
        conn.commit()
        conn.close()

    def get_reminders_by_user(self, user_id: int) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM reminders WHERE user_id = ?', (user_id,))
        results = cursor.fetchall()
        conn.close()
        return [dict(r) for r in results]

    def get_reminders_by_type(self, reminder_type: str) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM reminders WHERE type = ? AND enabled = 1', (reminder_type,))
        results = cursor.fetchall()
        conn.close()
        return [dict(r) for r in results]
