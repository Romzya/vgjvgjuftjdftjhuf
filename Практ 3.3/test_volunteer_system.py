"""
Автоматизированные тест-кейсы для системы «ВолонтёрПлюс»
Используется pytest
"""

import pytest
from datetime import datetime, date
from volunteer_system import VolunteerSystem, UserRole


class TestVolunteerSystem:
    
    @pytest.fixture
    def system(self):
        """Фикстура: создание новой системы перед каждым тестом"""
        return VolunteerSystem()
    
    @pytest.fixture
    def admin_logged_in(self, system):
        """Фикстура: администратор авторизован"""
        system.login("admin", "admin123")
        return system
    
    # ==================== TC-01: Регистрация волонтера ====================
    def test_register_volunteer_success(self, admin_logged_in):
        """TC-01: Успешная регистрация волонтера администратором"""
        success, msg, vid = admin_logged_in.register_volunteer(
            "Анна Смирнова", "anna@example.com", "+79201234567", ["Рисование", "Помощь детям"]
        )
        
        assert success is True
        assert "успешно зарегистрирован" in msg
        assert vid is not None
        
        volunteer = admin_logged_in.get_volunteer(vid)
        assert volunteer is not None
        assert volunteer.full_name == "Анна Смирнова"
        assert volunteer.email == "anna@example.com"
    
    def test_register_volunteer_invalid_email(self, admin_logged_in):
        """TC-01_негатив: Регистрация с неверным email"""
        success, msg, _ = admin_logged_in.register_volunteer(
            "Тест Тестов", "invalid-email", "+79201234567", []
        )
        
        assert success is False
        assert "Неверный формат email" in msg
    
    def test_register_volunteer_invalid_phone(self, admin_logged_in):
        """TC-01_негатив: Регистрация с неверным телефоном"""
        success, msg, _ = admin_logged_in.register_volunteer(
            "Тест Тестов", "test@example.com", "123", []
        )
        
        assert success is False
        assert "Неверный формат телефона" in msg
    
    # ==================== TC-02: Просмотр профиля волонтера ====================
    def test_get_volunteer_profile(self, admin_logged_in):
        """TC-02: Просмотр профиля существующего волонтера"""
        success, _, vid = admin_logged_in.register_volunteer(
            "Дмитрий Иванов", "dima@example.com", "+79123456789", ["Вождение"]
        )
        
        volunteer = admin_logged_in.get_volunteer(vid)
        assert volunteer is not None
        assert volunteer.full_name == "Дмитрий Иванов"
        assert volunteer.total_hours == 0.0
        assert volunteer.registered_date == date.today()
    
    def test_get_nonexistent_volunteer(self, admin_logged_in):
        """TC-02_негатив: Просмотр несуществующего волонтера"""
        volunteer = admin_logged_in.get_volunteer(999)
        assert volunteer is None
    
    # ==================== TC-03: Создание мероприятия ====================
    def test_create_event_success(self, admin_logged_in):
        """TC-03: Успешное создание мероприятия координатором"""
        success, msg, eid = admin_logged_in.create_event(
            "Благотворительный забег",
            datetime(2026, 5, 10, 9, 0),
            "Набережная",
            "Забег в поддержку детей",
            50
        )
        
        assert success is True
        assert "создано" in msg
        assert eid is not None
        
        event = admin_logged_in.get_event(eid)
        assert event.title == "Благотворительный забег"
        assert event.max_participants == 50
    
    def test_create_event_invalid_max_participants(self, admin_logged_in):
        """TC-03_негатив: Создание мероприятия с неверным max_participants"""
        success, msg, _ = admin_logged_in.create_event(
            "Плохое мероприятие",
            datetime(2026, 5, 10, 9, 0),
            "Где-то",
            "Описание",
            0
        )
        
        assert success is False
        assert "больше 0" in msg
    
    # ==================== TC-04: Запись волонтера на мероприятие ====================
    def test_register_volunteer_for_event(self, admin_logged_in):
        """TC-04: Успешная запись волонтера на мероприятие"""
        # Сначала создаем волонтера и мероприятие
        _, _, vid = admin_logged_in.register_volunteer(
            "Елена Петрова", "elena@example.com", "+79001234567", []
        )
        _, _, eid = admin_logged_in.create_event(
            "Мастер-класс", datetime(2026, 6, 1, 14, 0), "Коворкинг", "Обучение", 10
        )
        
        success, msg = admin_logged_in.register_volunteer_for_event(vid, eid)
        
        assert success is True
        assert "записан" in msg
        
        event = admin_logged_in.get_event(eid)
        assert vid in event.participants
    
    def test_register_volunteer_twice(self, admin_logged_in):
        """TC-04_негатив: Повторная запись на то же мероприятие"""
        _, _, vid = admin_logged_in.register_volunteer("Тест", "test@example.com", "+79001112233", [])
        _, _, eid = admin_logged_in.create_event("Тест", datetime(2026, 6, 1, 14, 0), "Место", "Описание", 10)
        
        admin_logged_in.register_volunteer_for_event(vid, eid)
        success, msg = admin_logged_in.register_volunteer_for_event(vid, eid)
        
        assert success is False
        assert "уже записан" in msg
    
    # ==================== TC-05: Фиксация отработанных часов ====================
    def test_record_hours_success(self, admin_logged_in):
        """TC-05: Успешная фиксация часов"""
        _, _, vid = admin_logged_in.register_volunteer("Павел Сидоров", "pavel@example.com", "+79111223344", [])
        _, _, eid = admin_logged_in.create_event("Событие", datetime(2026, 6, 5, 10, 0), "Место", "Описание", 10)
        
        admin_logged_in.register_volunteer_for_event(vid, eid)
        success, msg = admin_logged_in.record_hours(vid, eid, 5.5)
        
        assert success is True
        assert "5.5 часов" in msg
        
        volunteer = admin_logged_in.get_volunteer(vid)
        assert volunteer.total_hours == 5.5
    
    def test_record_hours_exceeds_limit(self, admin_logged_in):
        """TC-05_негатив: Фиксация часов более 24"""
        _, _, vid = admin_logged_in.register_volunteer("Тест", "test@example.com", "+79111223344", [])
        _, _, eid = admin_logged_in.create_event("Событие", datetime(2026, 6, 5, 10, 0), "Место", "Описание", 10)
        
        admin_logged_in.register_volunteer_for_event(vid, eid)
        success, msg = admin_logged_in.record_hours(vid, eid, 30)
        
        assert success is False
        assert "не может превышать 24" in msg
    
    # ==================== TC-06: Формирование отчета ====================
    def test_generate_report_for_volunteer(self, admin_logged_in):
        """TC-06: Формирование отчета по конкретному волонтеру"""
        _, _, vid = admin_logged_in.register_volunteer("Отчетный", "report@example.com", "+79991112233", [])
        _, _, eid = admin_logged_in.create_event("Событие для отчета", datetime(2026, 7, 1, 12, 0), "Место", "Описание", 5)
        
        admin_logged_in.register_volunteer_for_event(vid, eid)
        admin_logged_in.record_hours(vid, eid, 3.0)
        
        report = admin_logged_in.generate_report(vid)
        
        assert "volunteer" in report
        assert report["volunteer"]["full_name"] == "Отчетный"
        assert report["volunteer"]["total_hours"] == 3.0
        assert len(report["events"]) == 1
    
    def test_generate_full_report(self, admin_logged_in):
        """TC-06_доп: Формирование полного отчета по всем волонтерам"""
        admin_logged_in.register_volunteer("Волонтер1", "v1@example.com", "+79111111111", [])
        admin_logged_in.register_volunteer("Волонтер2", "v2@example.com", "+79222222222", [])
        
        report = admin_logged_in.generate_report()
        
        assert report["total_volunteers"] == 2
        assert len(report["volunteers_summary"]) == 2
    
    # ==================== TC-07: Уведомления ====================
    def test_send_notification_email(self, admin_logged_in):
        """TC-07: Отправка email-уведомления"""
        _, _, vid = admin_logged_in.register_volunteer("Уведомляемый", "notify@example.com", "+79000000000", [])
        
        success, msg = admin_logged_in.send_notification(vid, "Важное сообщение", "email")
        
        assert success is True
        assert "отправлено" in msg
    
    # ==================== TC-08: Авторизация ====================
    def test_login_success(self, system):
        """TC-08: Успешная авторизация"""
        success, msg = system.login("admin", "admin123")
        
        assert success is True
        assert "Добро пожаловать" in msg
    
    def test_login_wrong_password(self, system):
        """TC-08_негатив: Авторизация с неверным паролем"""
        success, msg = system.login("admin", "wrong_password")
        
        assert success is False
        assert "Неверный логин или пароль" in msg
    
    def test_login_nonexistent_user(self, system):
        """TC-08_негатив: Авторизация несуществующего пользователя"""
        success, msg = system.login("nonexistent", "password")
        
        assert success is False
        assert "Неверный логин или пароль" in msg
    
    # ==================== TC-09: Разграничение прав ====================
    def test_volunteer_cannot_register_volunteer(self, system):
        """TC-09: Волонтер не может регистрировать других волонтеров"""
        # Создаем волонтера-пользователя
        system.login("admin", "admin123")
        _, _, vid = system.register_volunteer("Волонтер-Юзер", "user@example.com", "+79111111111", [])
        system.create_user("volunteer_user", "pass123", UserRole.VOLUNTEER, vid)
        system.logout()
        
        # Вход как волонтер
        system.login("volunteer_user", "pass123")
        
        success, msg, _ = system.register_volunteer("Новый", "new@example.com", "+79222222222", [])
        
        assert success is False
        assert "Недостаточно прав" in msg
    
    def test_coordinator_can_create_event(self, system):
        """TC-09_доп: Координатор может создавать мероприятия"""
        system.login("admin", "admin123")
        system.create_user("coord", "coord123", UserRole.COORDINATOR)
        system.logout()
        
        system.login("coord", "coord123")
        success, msg, eid = system.create_event("Координаторское событие", datetime(2026, 8, 1, 10, 0), "Место", "Описание", 10)
        
        assert success is True
        assert eid is not None
    
    # ==================== TC-10: Нагрузочное тестирование ====================
    def test_concurrent_operations_simulation(self, admin_logged_in):
        """TC-10: Симуляция нагрузки (множество операций подряд)"""
        # Создаем 20 волонтеров и 5 мероприятий
        volunteer_ids = []
        for i in range(20):
            _, _, vid = admin_logged_in.register_volunteer(
                f"Нагрузочный{i}", f"load{i}@example.com", f"+790000000{i:02d}", []
            )
            volunteer_ids.append(vid)
        
        event_ids = []
        for i in range(5):
            _, _, eid = admin_logged_in.create_event(
                f"Нагрузочное событие{i}", datetime(2026, 9, i+1, 10, 0), "Место", "Описание", 30
            )
            event_ids.append(eid)
        
        # Записываем волонтеров на мероприятия
        for vid in volunteer_ids:
            for eid in event_ids[:2]:  # каждый на первые 2 мероприятия
                admin_logged_in.register_volunteer_for_event(vid, eid)
        
        # Фиксируем часы
        for vid in volunteer_ids[:10]:  # первые 10 получают часы
            for eid in event_ids[:2]:
                admin_logged_in.record_hours(vid, eid, 2.5)
        
        # Проверяем, что все операции выполнены без ошибок
        assert len(admin_logged_in.list_volunteers()) == 20
        assert len(admin_logged_in.list_events()) == 5


# Запуск тестов
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])