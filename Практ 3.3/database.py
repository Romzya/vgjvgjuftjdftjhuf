"""
Модуль работы с базой данных SQLite для системы «ВолонтёрПлюс»
"""

import sqlite3
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple
import os

DB_PATH = "volunteer_system.db"


class Database:
    """Класс для работы с базой данных"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Получить соединение с БД"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Инициализация базы данных: создание таблиц"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Таблица волонтеров
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS volunteers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    phone TEXT NOT NULL,
                    skills TEXT,
                    registered_date TEXT NOT NULL,
                    total_hours REAL DEFAULT 0
                )
            ''')
            
            # Таблица мероприятий
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    event_date TEXT NOT NULL,
                    location TEXT NOT NULL,
                    description TEXT,
                    max_participants INTEGER DEFAULT 50,
                    created_date TEXT NOT NULL
                )
            ''')
            
            # Таблица участия (связь волонтеров и мероприятий)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS event_participants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    volunteer_id INTEGER NOT NULL,
                    event_id INTEGER NOT NULL,
                    hours_worked REAL DEFAULT 0,
                    status TEXT DEFAULT 'registered',
                    FOREIGN KEY (volunteer_id) REFERENCES volunteers (id),
                    FOREIGN KEY (event_id) REFERENCES events (id),
                    UNIQUE(volunteer_id, event_id)
                )
            ''')
            
            # Таблица пользователей системы
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    volunteer_id INTEGER,
                    FOREIGN KEY (volunteer_id) REFERENCES volunteers (id)
                )
            ''')
            
            # Создание администратора по умолчанию, если не существует
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
            if cursor.fetchone()[0] == 0:
                import hashlib
                password_hash = hashlib.sha256("admin123".encode()).hexdigest()
                cursor.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                    ("admin", password_hash, "admin")
                )
            
            conn.commit()
    
    # ============ РАБОТА С ВОЛОНТЕРАМИ ============
    
    def add_volunteer(self, full_name: str, email: str, phone: str, skills: List[str]) -> int:
        """Добавление волонтера. Возвращает ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            skills_str = ", ".join(skills) if skills else ""
            registered_date = date.today().isoformat()
            
            cursor.execute('''
                INSERT INTO volunteers (full_name, email, phone, skills, registered_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (full_name, email, phone, skills_str, registered_date))
            
            return cursor.lastrowid
    
    def get_all_volunteers(self) -> List[Dict]:
        """Получить всех волонтеров"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM volunteers ORDER BY id')
            rows = cursor.fetchall()
            
            volunteers = []
            for row in rows:
                volunteers.append({
                    'id': row[0],
                    'full_name': row[1],
                    'email': row[2],
                    'phone': row[3],
                    'skills': row[4],
                    'registered_date': row[5],
                    'total_hours': row[6]
                })
            return volunteers
    
    def get_volunteer(self, volunteer_id: int) -> Optional[Dict]:
        """Получить волонтера по ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM volunteers WHERE id = ?', (volunteer_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row[0],
                    'full_name': row[1],
                    'email': row[2],
                    'phone': row[3],
                    'skills': row[4],
                    'registered_date': row[5],
                    'total_hours': row[6]
                }
            return None
    
    def update_volunteer_hours(self, volunteer_id: int, additional_hours: float):
        """Обновить общее количество часов волонтера"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE volunteers 
                SET total_hours = total_hours + ? 
                WHERE id = ?
            ''', (additional_hours, volunteer_id))
            conn.commit()
    
    def delete_volunteer(self, volunteer_id: int) -> bool:
        """Удалить волонтера"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM volunteers WHERE id = ?', (volunteer_id,))
            return cursor.rowcount > 0
    
    # ============ РАБОТА С МЕРОПРИЯТИЯМИ ============
    
    def add_event(self, title: str, event_date: datetime, location: str, 
                  description: str, max_participants: int) -> int:
        """Добавление мероприятия. Возвращает ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            created_date = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO events (title, event_date, location, description, max_participants, created_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (title, event_date.isoformat(), location, description, max_participants, created_date))
            
            return cursor.lastrowid
    
    def get_all_events(self) -> List[Dict]:
        """Получить все мероприятия"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM events ORDER BY event_date')
            rows = cursor.fetchall()
            
            events = []
            for row in rows:
                events.append({
                    'id': row[0],
                    'title': row[1],
                    'event_date': row[2],
                    'location': row[3],
                    'description': row[4],
                    'max_participants': row[5],
                    'created_date': row[6]
                })
            return events
    
    def get_event(self, event_id: int) -> Optional[Dict]:
        """Получить мероприятие по ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM events WHERE id = ?', (event_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row[0],
                    'title': row[1],
                    'event_date': row[2],
                    'location': row[3],
                    'description': row[4],
                    'max_participants': row[5],
                    'created_date': row[6]
                }
            return None
    
    def delete_event(self, event_id: int) -> bool:
        """Удалить мероприятие"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM events WHERE id = ?', (event_id,))
            return cursor.rowcount > 0
    
    # ============ УЧАСТИЕ В МЕРОПРИЯТИЯХ ============
    
    def register_participant(self, volunteer_id: int, event_id: int) -> bool:
        """Записать волонтера на мероприятие"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO event_participants (volunteer_id, event_id)
                    VALUES (?, ?)
                ''', (volunteer_id, event_id))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False
    
    def record_hours(self, volunteer_id: int, event_id: int, hours: float) -> bool:
        """Записать часы волонтера за мероприятие"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Обновляем часы в таблице участия
            cursor.execute('''
                UPDATE event_participants 
                SET hours_worked = ?, status = 'completed'
                WHERE volunteer_id = ? AND event_id = ?
            ''', (hours, volunteer_id, event_id))
            
            if cursor.rowcount > 0:
                # Обновляем общие часы волонтера
                self.update_volunteer_hours(volunteer_id, hours)
                return True
            return False
    
    def get_participants(self, event_id: int) -> List[Dict]:
        """Получить всех участников мероприятия"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT v.id, v.full_name, v.email, v.phone, ep.hours_worked, ep.status
                FROM event_participants ep
                JOIN volunteers v ON ep.volunteer_id = v.id
                WHERE ep.event_id = ?
            ''', (event_id,))
            
            rows = cursor.fetchall()
            participants = []
            for row in rows:
                participants.append({
                    'id': row[0],
                    'full_name': row[1],
                    'email': row[2],
                    'phone': row[3],
                    'hours_worked': row[4],
                    'status': row[5]
                })
            return participants
    
    def get_volunteer_events(self, volunteer_id: int) -> List[Dict]:
        """Получить все мероприятия волонтера"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT e.id, e.title, e.event_date, e.location, ep.hours_worked, ep.status
                FROM event_participants ep
                JOIN events e ON ep.event_id = e.id
                WHERE ep.volunteer_id = ?
                ORDER BY e.event_date
            ''', (volunteer_id,))
            
            rows = cursor.fetchall()
            events = []
            for row in rows:
                events.append({
                    'id': row[0],
                    'title': row[1],
                    'event_date': row[2],
                    'location': row[3],
                    'hours_worked': row[4],
                    'status': row[5]
                })
            return events
    
    # ============ СТАТИСТИКА И ОТЧЕТЫ ============
    
    def get_statistics(self) -> Dict:
        """Получить общую статистику"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Количество волонтеров
            cursor.execute('SELECT COUNT(*) FROM volunteers')
            total_volunteers = cursor.fetchone()[0]
            
            # Количество мероприятий
            cursor.execute('SELECT COUNT(*) FROM events')
            total_events = cursor.fetchone()[0]
            
            # Общее количество часов
            cursor.execute('SELECT SUM(total_hours) FROM volunteers')
            total_hours = cursor.fetchone()[0] or 0
            
            # Количество завершенных участий
            cursor.execute('SELECT COUNT(*) FROM event_participants WHERE status = "completed"')
            completed_participations = cursor.fetchone()[0]
            
            return {
                'total_volunteers': total_volunteers,
                'total_events': total_events,
                'total_hours': total_hours,
                'completed_participations': completed_participations
            }
    
    def get_report(self, volunteer_id: Optional[int] = None) -> Dict:
        """Получить отчет по волонтеру или общий"""
        if volunteer_id:
            volunteer = self.get_volunteer(volunteer_id)
            if volunteer:
                events = self.get_volunteer_events(volunteer_id)
                return {
                    'volunteer': volunteer,
                    'events': events
                }
            return {'error': 'Волонтер не найден'}
        else:
            return {
                'statistics': self.get_statistics(),
                'volunteers': self.get_all_volunteers(),
                'events': self.get_all_events()
            }
    
    def clear_all_data(self):
        """Очистить все данные (для тестирования)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM event_participants')
            cursor.execute('DELETE FROM volunteers')
            cursor.execute('DELETE FROM events')
            cursor.execute("DELETE FROM users WHERE username != 'admin'")
            conn.commit()


# Создаем глобальный экземпляр БД
db = Database()