"""
Система поддержки волонтерской деятельности «ВолонтёрПлюс»
С использованием базы данных SQLite
"""

import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from database import db


class VolunteerSystemWithDB:
    """Система с поддержкой базы данных"""
    
    def __init__(self):
        self._current_user = None
        self._current_user_role = None
    
    def _hash_password(self, password: str) -> str:
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def login(self, username: str, password: str) -> Tuple[bool, str]:
        """Авторизация пользователя"""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            password_hash = self._hash_password(password)
            
            cursor.execute(
                "SELECT username, role FROM users WHERE username = ? AND password_hash = ?",
                (username, password_hash)
            )
            user = cursor.fetchone()
            
            if user:
                self._current_user = user[0]
                self._current_user_role = user[1]
                return True, f"Добро пожаловать, {username}!"
            else:
                return False, "Неверный логин или пароль"
    
    def logout(self):
        """Выход из системы"""
        self._current_user = None
        self._current_user_role = None
    
    def get_current_user(self):
        return self._current_user
    
    def has_permission(self, required_role: str) -> bool:
        """Проверка прав доступа"""
        if not self._current_user_role:
            return False
        
        role_hierarchy = {
            'admin': 3,
            'coordinator': 2,
            'volunteer': 1
        }
        
        user_level = role_hierarchy.get(self._current_user_role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        return user_level >= required_level
    
    # ============ РАБОТА С ВОЛОНТЕРАМИ ============
    
    def register_volunteer(self, full_name: str, email: str, phone: str, 
                          skills: List[str]) -> Tuple[bool, str, Optional[int]]:
        """Регистрация нового волонтера"""
        if not self.has_permission('coordinator'):
            return False, "Недостаточно прав для регистрации волонтера", None
        
        # Проверка email
        import re
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return False, "Неверный формат email", None
        
        # Проверка телефона
        if len(phone) < 10:
            return False, "Неверный формат телефона", None
        
        try:
            volunteer_id = db.add_volunteer(full_name, email, phone, skills)
            return True, f"Волонтер {full_name} успешно зарегистрирован", volunteer_id
        except Exception as e:
            if "UNIQUE constraint" in str(e):
                return False, "Волонтер с таким email уже существует", None
            return False, f"Ошибка: {e}", None
    
    def get_all_volunteers(self) -> List[Dict]:
        """Получить всех волонтеров"""
        return db.get_all_volunteers()
    
    def get_volunteer(self, volunteer_id: int) -> Optional[Dict]:
        """Получить волонтера по ID"""
        return db.get_volunteer(volunteer_id)
    
    def delete_volunteer(self, volunteer_id: int) -> Tuple[bool, str]:
        """Удалить волонтера"""
        if not self.has_permission('admin'):
            return False, "Недостаточно прав для удаления волонтера"
        
        if db.delete_volunteer(volunteer_id):
            return True, "Волонтер удален"
        return False, "Волонтер не найден"
    
    # ============ РАБОТА С МЕРОПРИЯТИЯМИ ============
    
    def create_event(self, title: str, event_date: datetime, location: str,
                    description: str, max_participants: int) -> Tuple[bool, str, Optional[int]]:
        """Создание мероприятия"""
        if not self.has_permission('coordinator'):
            return False, "Недостаточно прав для создания мероприятия", None
        
        if max_participants <= 0:
            return False, "Максимальное количество участников должно быть больше 0", None
        
        event_id = db.add_event(title, event_date, location, description, max_participants)
        return True, f"Мероприятие '{title}' создано", event_id
    
    def get_all_events(self) -> List[Dict]:
        """Получить все мероприятия"""
        return db.get_all_events()
    
    def get_event(self, event_id: int) -> Optional[Dict]:
        """Получить мероприятие по ID"""
        return db.get_event(event_id)
    
    def delete_event(self, event_id: int) -> Tuple[bool, str]:
        """Удалить мероприятие"""
        if not self.has_permission('admin'):
            return False, "Недостаточно прав для удаления мероприятия"
        
        if db.delete_event(event_id):
            return True, "Мероприятие удалено"
        return False, "Мероприятие не найдено"
    
    # ============ УЧАСТИЕ В МЕРОПРИЯТИЯХ ============
    
    def register_volunteer_for_event(self, volunteer_id: int, event_id: int) -> Tuple[bool, str]:
        """Запись волонтера на мероприятие"""
        volunteer = self.get_volunteer(volunteer_id)
        if not volunteer:
            return False, "Волонтер не найден"
        
        event = self.get_event(event_id)
        if not event:
            return False, "Мероприятие не найдено"
        
        # Проверка лимита участников
        participants = db.get_participants(event_id)
        if len(participants) >= event['max_participants']:
            return False, "Достигнуто максимальное количество участников"
        
        if db.register_participant(volunteer_id, event_id):
            return True, f"Волонтер {volunteer['full_name']} записан на мероприятие '{event['title']}'"
        else:
            return False, "Волонтер уже записан на это мероприятие"
    
    def record_hours(self, volunteer_id: int, event_id: int, hours: float) -> Tuple[bool, str]:
        """Фиксация отработанных часов"""
        if not self.has_permission('coordinator'):
            return False, "Недостаточно прав для фиксации часов"
        
        volunteer = self.get_volunteer(volunteer_id)
        if not volunteer:
            return False, "Волонтер не найден"
        
        event = self.get_event(event_id)
        if not event:
            return False, "Мероприятие не найдено"
        
        if hours <= 0:
            return False, "Количество часов должно быть положительным"
        
        if hours > 24:
            return False, "Количество часов не может превышать 24"
        
        if db.record_hours(volunteer_id, event_id, hours):
            return True, f"Зафиксировано {hours} часов для {volunteer['full_name']}"
        else:
            return False, "Волонтер не был зарегистрирован на это мероприятие"
    
    def get_participants(self, event_id: int) -> List[Dict]:
        """Получить участников мероприятия"""
        return db.get_participants(event_id)
    
    def get_volunteer_events(self, volunteer_id: int) -> List[Dict]:
        """Получить мероприятия волонтера"""
        return db.get_volunteer_events(volunteer_id)
    
    # ============ ОТЧЕТЫ ============
    
    def generate_report(self, volunteer_id: Optional[int] = None) -> Dict:
        """Формирование отчета"""
        return db.get_report(volunteer_id)
    
    def get_statistics(self) -> Dict:
        """Получить статистику"""
        return db.get_statistics()


# Создаем глобальный экземпляр системы
system = VolunteerSystemWithDB()


def print_menu():
    """Вывод главного меню"""
    print("\n" + "=" * 50)
    print("   СИСТЕМА ПОДДЕРЖКИ ВОЛОНТЕРСКОЙ ДЕЯТЕЛЬНОСТИ")
    print("=" * 50)
    print("1. Войти в систему")
    print("2. Просмотреть всех волонтеров")
    print("3. Просмотреть все мероприятия")
    print("4. Просмотреть статистику")
    print("5. Создать волонтера (требуются права)")
    print("6. Создать мероприятие (требуются права)")
    print("7. Записать волонтера на мероприятие")
    print("9. Просмотреть участников мероприятия")
    print("10. Просмотреть мероприятия волонтера")
    print("11. Сформировать отчет по волонтеру")
    print("12. Просмотреть БД (SQL-запрос)")
    print("0. Выход")
    print("-" * 50)


def print_volunteers_table(volunteers):
    """Вывод таблицы волонтеров"""
    if not volunteers:
        print("Нет зарегистрированных волонтеров")
        return
    
    print("\n" + "-" * 80)
    print(f"{'ID':<5} {'ФИО':<25} {'Email':<25} {'Часы':<8}")
    print("-" * 80)
    for v in volunteers:
        print(f"{v['id']:<5} {v['full_name']:<25} {v['email']:<25} {v['total_hours']:<8.1f}")
    print("-" * 80)


def print_events_table(events):
    """Вывод таблицы мероприятий"""
    if not events:
        print("Нет запланированных мероприятий")
        return
    
    print("\n" + "-" * 100)
    print(f"{'ID':<5} {'Название':<25} {'Дата':<20} {'Место':<25} {'Макс':<8}")
    print("-" * 100)
    for e in events:
        date_str = e['event_date'][:16] if e['event_date'] else ""
        print(f"{e['id']:<5} {e['title']:<25} {date_str:<20} {e['location']:<25} {e['max_participants']:<8}")
    print("-" * 100)


def interactive_mode():
    """Интерактивный режим работы с системой"""
    print("\nДобро пожаловать в систему «ВолонтёрПлюс»!")
    print("Для начала работы войдите в систему.")
    print("Логин по умолчанию: admin, пароль: admin123\n")
    
    while True:
        print_menu()
        choice = input("Выберите действие: ").strip()
        
        if choice == "0":
            print("До свидания!")
            break
        
        elif choice == "1":
            username = input("Логин: ")
            password = input("Пароль: ")
            success, msg = system.login(username, password)
            print(msg)
            if success:
                print(f"Вы вошли как: {system.get_current_user()} (роль: {system._current_user_role})")
        
        elif choice == "2":
            volunteers = system.get_all_volunteers()
            print_volunteers_table(volunteers)
        
        elif choice == "3":
            events = system.get_all_events()
            print_events_table(events)
        
        elif choice == "4":
            stats = system.get_statistics()
            print("\n" + "=" * 40)
            print("СТАТИСТИКА СИСТЕМЫ")
            print("=" * 40)
            print(f"👥 Волонтеров: {stats['total_volunteers']}")
            print(f"📅 Мероприятий: {stats['total_events']}")
            print(f"⏱️ Всего часов: {stats['total_hours']:.1f}")
            print(f"✅ Завершенных участий: {stats['completed_participations']}")
            print("=" * 40)
        
        elif choice == "5":
            if not system._current_user:
                print("Сначала войдите в систему!")
                continue
            print("\n--- Регистрация нового волонтера ---")
            full_name = input("ФИО: ")
            email = input("Email: ")
            phone = input("Телефон: ")
            skills_input = input("Навыки (через запятую): ")
            skills = [s.strip() for s in skills_input.split(",") if s.strip()]
            
            success, msg, vid = system.register_volunteer(full_name, email, phone, skills)
            print(msg)
            if success:
                print(f"ID нового волонтера: {vid}")
        
        elif choice == "6":
            if not system._current_user:
                print("Сначала войдите в систему!")
                continue
            print("\n--- Создание мероприятия ---")
            title = input("Название: ")
            date_str = input("Дата и время (ГГГГ-ММ-ДД ЧЧ:ММ): ")
            location = input("Место: ")
            description = input("Описание: ")
            max_participants = int(input("Максимум участников: "))
            
            try:
                event_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
                success, msg, eid = system.create_event(title, event_date, location, description, max_participants)
                print(msg)
                if success:
                    print(f"ID мероприятия: {eid}")
            except ValueError:
                print("Неверный формат даты!")
        
        elif choice == "7":
            print("\n--- Запись волонтера на мероприятие ---")
            volunteers = system.get_all_volunteers()
            if not volunteers:
                print("Нет волонтеров для записи")
                continue
            print_volunteers_table(volunteers)
            volunteer_id = int(input("ID волонтера: "))
            
            events = system.get_all_events()
            if not events:
                print("Нет мероприятий для записи")
                continue
            print_events_table(events)
            event_id = int(input("ID мероприятия: "))
            
            success, msg = system.register_volunteer_for_event(volunteer_id, event_id)
            print(msg)
        
        elif choice == "8":
            if not system._current_user or not system.has_permission('coordinator'):
                print("Недостаточно прав! Требуются права координатора или администратора")
                continue
            
            print("\n--- Фиксация часов ---")
            volunteer_id = int(input("ID волонтера: "))
            event_id = int(input("ID мероприятия: "))
            hours = float(input("Количество часов: "))
            
            success, msg = system.record_hours(volunteer_id, event_id, hours)
            print(msg)
        
        elif choice == "9":
            event_id = int(input("ID мероприятия: "))
            participants = system.get_participants(event_id)
            
            if participants:
                print(f"\nУчастники мероприятия #{event_id}:")
                print("-" * 60)
                for p in participants:
                    print(f"  {p['full_name']} - часы: {p['hours_worked']} - статус: {p['status']}")
            else:
                print("Нет участников")
        
        elif choice == "10":
            volunteer_id = int(input("ID волонтера: "))
            events = system.get_volunteer_events(volunteer_id)
            
            if events:
                print(f"\nМероприятия волонтера #{volunteer_id}:")
                print("-" * 70)
                for e in events:
                    print(f"  {e['title']} - {e['event_date'][:16]} - часы: {e['hours_worked']}")
            else:
                print("Волонтер не участвовал в мероприятиях")
        
        elif choice == "11":
            volunteer_id = int(input("ID волонтера: "))
            report = system.generate_report(volunteer_id)
            
            if 'error' in report:
                print(report['error'])
            else:
                print("\n" + "=" * 50)
                print(f"ОТЧЕТ ПО ВОЛОНТЕРУ: {report['volunteer']['full_name']}")
                print("=" * 50)
                print(f"Email: {report['volunteer']['email']}")
                print(f"Телефон: {report['volunteer']['phone']}")
                print(f"Навыки: {report['volunteer']['skills']}")
                print(f"Всего часов: {report['volunteer']['total_hours']}")
                print(f"\nУчастие в мероприятиях:")
                for e in report['events']:
                    print(f"  - {e['title']} ({e['event_date'][:16]}) - {e['hours_worked']} часов")
                print("=" * 50)
        
        elif choice == "12":
            print("\n--- Просмотр БД ---")
            print("Доступные таблицы: volunteers, events, event_participants, users")
            query = input("Введите SQL-запрос: ")
            try:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    for row in rows:
                        print(row)
            except Exception as e:
                print(f"Ошибка: {e}")
        
        else:
            print("Неверный выбор!")
1

if __name__ == "__main__":
    interactive_mode()