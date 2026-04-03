"""
Система поддержки волонтерской деятельности «ВолонтёрПлюс»
Реализация основных функций учета волонтеров, мероприятий и часов
"""

import json
import hashlib
import re
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class UserRole(Enum):
    ADMIN = "admin"
    COORDINATOR = "coordinator"
    VOLUNTEER = "volunteer"


@dataclass
class Volunteer:
    id: int
    full_name: str
    email: str
    phone: str
    skills: List[str]
    registered_date: date
    total_hours: float = 0.0


@dataclass
class Event:
    id: int
    title: str
    date: datetime
    location: str
    description: str
    max_participants: int
    participants: List[int] = None  # list of volunteer ids
    hours_per_participant: Dict[int, float] = None  # volunteer_id -> hours
    
    def __post_init__(self):
        if self.participants is None:
            self.participants = []
        if self.hours_per_participant is None:
            self.hours_per_participant = {}


@dataclass
class User:
    username: str
    password_hash: str
    role: UserRole
    volunteer_id: Optional[int] = None  # если волонтер, то ссылка на профиль


class VolunteerSystem:
    """Основная система управления волонтерской деятельностью"""
    
    def __init__(self):
        self.volunteers: Dict[int, Volunteer] = {}
        self.events: Dict[int, Event] = {}
        self.users: Dict[str, User] = {}
        self._next_volunteer_id = 1
        self._next_event_id = 1
        self._current_user: Optional[User] = None
        
        # Создание администратора по умолчанию
        self._create_default_admin()
    
    def _hash_password(self, password: str) -> str:
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _validate_email(self, email: str) -> bool:
        """Проверка формата email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _create_default_admin(self):
        """Создание администратора по умолчанию"""
        self.users["admin"] = User(
            username="admin",
            password_hash=self._hash_password("admin123"),
            role=UserRole.ADMIN
        )
    
    def login(self, username: str, password: str) -> Tuple[bool, str]:
        """
        Авторизация пользователя
        Возвращает: (успех, сообщение)
        """
        if username not in self.users:
            return False, "Неверный логин или пароль"
        
        user = self.users[username]
        if user.password_hash != self._hash_password(password):
            return False, "Неверный логин или пароль"
        
        self._current_user = user
        return True, f"Добро пожаловать, {username}!"
    
    def logout(self):
        """Выход из системы"""
        self._current_user = None
    
    def get_current_user(self) -> Optional[User]:
        """Получить текущего пользователя"""
        return self._current_user
    
    def has_permission(self, required_role: UserRole) -> bool:
        """Проверка прав доступа"""
        if not self._current_user:
            return False
        
        role_hierarchy = {
            UserRole.ADMIN: 3,
            UserRole.COORDINATOR: 2,
            UserRole.VOLUNTEER: 1
        }
        
        return role_hierarchy[self._current_user.role] >= role_hierarchy[required_role]
    
    def register_volunteer(self, full_name: str, email: str, phone: str, 
                          skills: List[str]) -> Tuple[bool, str, Optional[int]]:
        """
        Регистрация нового волонтера (требуются права ADMIN или COORDINATOR)
        Возвращает: (успех, сообщение, id волонтера)
        """
        if not self.has_permission(UserRole.COORDINATOR):
            return False, "Недостаточно прав для регистрации волонтера", None
        
        if not self._validate_email(email):
            return False, "Неверный формат email", None
        
        if not phone or len(phone) < 10:
            return False, "Неверный формат телефона", None
        
        volunteer = Volunteer(
            id=self._next_volunteer_id,
            full_name=full_name,
            email=email,
            phone=phone,
            skills=skills,
            registered_date=date.today(),
            total_hours=0.0
        )
        
        self.volunteers[self._next_volunteer_id] = volunteer
        self._next_volunteer_id += 1
        
        return True, f"Волонтер {full_name} успешно зарегистрирован", volunteer.id
    
    def get_volunteer(self, volunteer_id: int) -> Optional[Volunteer]:
        """Получить данные волонтера"""
        return self.volunteers.get(volunteer_id)
    
    def list_volunteers(self) -> List[Volunteer]:
        """Получить список всех волонтеров"""
        return list(self.volunteers.values())
    
    def create_event(self, title: str, event_date: datetime, location: str,
                    description: str, max_participants: int) -> Tuple[bool, str, Optional[int]]:
        """
        Создание мероприятия (требуются права ADMIN или COORDINATOR)
        """
        if not self.has_permission(UserRole.COORDINATOR):
            return False, "Недостаточно прав для создания мероприятия", None
        
        if max_participants <= 0:
            return False, "Максимальное количество участников должно быть больше 0", None
        
        event = Event(
            id=self._next_event_id,
            title=title,
            date=event_date,
            location=location,
            description=description,
            max_participants=max_participants
        )
        
        self.events[self._next_event_id] = event
        self._next_event_id += 1
        
        return True, f"Мероприятие '{title}' создано", event.id
    
    def get_event(self, event_id: int) -> Optional[Event]:
        """Получить мероприятие по id"""
        return self.events.get(event_id)
    
    def list_events(self) -> List[Event]:
        """Получить список всех мероприятий"""
        return list(self.events.values())
    
    def register_volunteer_for_event(self, volunteer_id: int, event_id: int) -> Tuple[bool, str]:
        """
        Запись волонтера на мероприятие
        """
        volunteer = self.get_volunteer(volunteer_id)
        if not volunteer:
            return False, "Волонтер не найден"
        
        event = self.get_event(event_id)
        if not event:
            return False, "Мероприятие не найдено"
        
        if volunteer_id in event.participants:
            return False, "Волонтер уже записан на это мероприятие"
        
        if len(event.participants) >= event.max_participants:
            return False, "Достигнуто максимальное количество участников"
        
        event.participants.append(volunteer_id)
        return True, f"Волонтер {volunteer.full_name} записан на мероприятие '{event.title}'"
    
    def record_hours(self, volunteer_id: int, event_id: int, hours: float) -> Tuple[bool, str]:
        """
        Фиксация отработанных часов (требуются права COORDINATOR или ADMIN)
        """
        if not self.has_permission(UserRole.COORDINATOR):
            return False, "Недостаточно прав для фиксации часов"
        
        volunteer = self.get_volunteer(volunteer_id)
        if not volunteer:
            return False, "Волонтер не найден"
        
        event = self.get_event(event_id)
        if not event:
            return False, "Мероприятие не найдено"
        
        if volunteer_id not in event.participants:
            return False, "Волонтер не был зарегистрирован на это мероприятие"
        
        if hours <= 0:
            return False, "Количество часов должно быть положительным"
        
        if hours > 24:
            return False, "Количество часов не может превышать 24"
        
        event.hours_per_participant[volunteer_id] = hours
        volunteer.total_hours += hours
        
        return True, f"Зафиксировано {hours} часов для {volunteer.full_name}"
    
    def get_volunteer_hours(self, volunteer_id: int) -> float:
        """Получить общее количество часов волонтера"""
        volunteer = self.get_volunteer(volunteer_id)
        return volunteer.total_hours if volunteer else 0.0
    
    def generate_report(self, volunteer_id: Optional[int] = None) -> Dict:
        """
        Формирование отчета по активности волонтеров
        """
        if volunteer_id:
            volunteer = self.get_volunteer(volunteer_id)
            if not volunteer:
                return {"error": "Волонтер не найден"}
            
            events_participated = []
            for event in self.events.values():
                if volunteer_id in event.participants:
                    events_participated.append({
                        "event_title": event.title,
                        "date": event.date.isoformat(),
                        "hours": event.hours_per_participant.get(volunteer_id, 0)
                    })
            
            return {
                "volunteer": {
                    "id": volunteer.id,
                    "full_name": volunteer.full_name,
                    "email": volunteer.email,
                    "skills": volunteer.skills,
                    "total_hours": volunteer.total_hours
                },
                "events": events_participated
            }
        else:
            # Отчет по всем волонтерам
            report = {
                "total_volunteers": len(self.volunteers),
                "total_events": len(self.events),
                "volunteers_summary": []
            }
            
            for volunteer in self.volunteers.values():
                report["volunteers_summary"].append({
                    "id": volunteer.id,
                    "name": volunteer.full_name,
                    "total_hours": volunteer.total_hours
                })
            
            return report
    
    def send_notification(self, volunteer_id: int, message: str, method: str = "email") -> Tuple[bool, str]:
        """
        Отправка уведомления (симуляция)
        """
        volunteer = self.get_volunteer(volunteer_id)
        if not volunteer:
            return False, "Волонтер не найден"
        
        if method not in ["email", "sms"]:
            return False, "Неверный метод уведомления"
        
        # Симуляция отправки
        print(f"[УВЕДОМЛЕНИЕ] {method.upper()} -> {volunteer.email if method == 'email' else volunteer.phone}")
        print(f"Сообщение: {message}")
        
        return True, f"Уведомление отправлено волонтеру {volunteer.full_name} через {method}"
    
    def create_user(self, username: str, password: str, role: UserRole, 
                   volunteer_id: Optional[int] = None) -> Tuple[bool, str]:
        """
        Создание пользователя системы (только ADMIN)
        """
        if not self.has_permission(UserRole.ADMIN):
            return False, "Недостаточно прав для создания пользователя"
        
        if username in self.users:
            return False, "Пользователь с таким именем уже существует"
        
        if role == UserRole.VOLUNTEER and volunteer_id is None:
            return False, "Для роли 'волонтер' необходимо указать volunteer_id"
        
        self.users[username] = User(
            username=username,
            password_hash=self._hash_password(password),
            role=role,
            volunteer_id=volunteer_id
        )
        
        return True, f"Пользователь {username} создан с ролью {role.value}"


# Пример использования
if __name__ == "__main__":
    system = VolunteerSystem()
    
    # Авторизация
    print(system.login("admin", "admin123"))
    
    # Регистрация волонтера
    success, msg, vid = system.register_volunteer(
        "Иван Петров", "ivan@example.com", "+79123456789", ["Python", "Организация"]
    )
    print(msg)
    
    # Создание мероприятия
    success, msg, eid = system.create_event(
        "Субботник в парке",
        datetime(2026, 4, 15, 10, 0),
        "Центральный парк",
        "Уборка территории",
        20
    )
    print(msg)
    
    # Запись на мероприятие
    print(system.register_volunteer_for_event(vid, eid))
    
    # Фиксация часов
    print(system.record_hours(vid, eid, 4.5))
    
    # Отчет
    print(json.dumps(system.generate_report(vid), indent=2, default=str))