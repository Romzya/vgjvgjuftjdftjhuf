"""
Упрощенный запуск тестов
"""

from volunteer_system import VolunteerSystem, UserRole
from datetime import datetime

def test_registration():
    """Тест регистрации волонтера"""
    print("\n--- TC-01: Тест регистрации волонтера ---")
    system = VolunteerSystem()
    system.login("admin", "admin123")
    
    success, msg, vid = system.register_volunteer(
        "Тестовый Волонтер", 
        "test@example.com", 
        "+79123456789", 
        ["Python", "Тестирование"]
    )
    
    if success:
        print(f"✅ Регистрация успешна: {msg}")
        print(f"   ID волонтера: {vid}")
    else:
        print(f"❌ Ошибка: {msg}")
    
    return success

def test_create_event():
    """Тест создания мероприятия"""
    print("\n--- TC-03: Тест создания мероприятия ---")
    system = VolunteerSystem()
    system.login("admin", "admin123")
    
    success, msg, eid = system.create_event(
        "Тестовое мероприятие",
        datetime(2026, 5, 15, 10, 0),
        "Тестовое место",
        "Тестовое описание",
        10
    )
    
    if success:
        print(f"✅ Мероприятие создано: {msg}")
        print(f"   ID мероприятия: {eid}")
    else:
        print(f"❌ Ошибка: {msg}")
    
    return success

def test_login():
    """Тест авторизации"""
    print("\n--- TC-08: Тест авторизации ---")
    system = VolunteerSystem()
    
    # Правильный вход
    success, msg = system.login("admin", "admin123")
    if success:
        print(f"✅ Успешный вход: {msg}")
    else:
        print(f"❌ Ошибка входа: {msg}")
    
    # Неправильный пароль
    success2, msg2 = system.login("admin", "wrongpass")
    if not success2:
        print(f"✅ Неверный пароль отклонен: {msg2}")
    else:
        print(f"❌ Ошибка: неверный пароль пропущен")
    
    return success and not success2

def test_record_hours():
    """Тест фиксации часов"""
    print("\n--- TC-05: Тест фиксации часов ---")
    system = VolunteerSystem()
    system.login("admin", "admin123")
    
    # Создаем волонтера
    _, _, vid = system.register_volunteer(
        "Часовой Волонтер", 
        "hours@example.com", 
        "+79998887766", 
        ["Помощь"]
    )
    
    # Создаем мероприятие
    _, _, eid = system.create_event(
        "Часовое событие",
        datetime(2026, 6, 1, 9, 0),
        "Место",
        "Описание",
        5
    )
    
    # Записываем на мероприятие
    system.register_volunteer_for_event(vid, eid)
    
    # Фиксируем часы
    success, msg = system.record_hours(vid, eid, 4.5)
    
    if success:
        print(f"✅ Часы зафиксированы: {msg}")
        volunteer = system.get_volunteer(vid)
        print(f"   Общее количество часов: {volunteer.total_hours}")
    else:
        print(f"❌ Ошибка: {msg}")
    
    return success

def test_report():
    """Тест формирования отчета"""
    print("\n--- TC-06: Тест отчета ---")
    system = VolunteerSystem()
    system.login("admin", "admin123")
    
    # Создаем волонтера с активностью
    _, _, vid = system.register_volunteer(
        "Отчетный Волонтер", 
        "report@example.com", 
        "+79112223344", 
        ["Организация"]
    )
    
    _, _, eid = system.create_event(
        "Отчетное событие",
        datetime(2026, 7, 10, 14, 0),
        "Офис",
        "Важное событие",
        10
    )
    
    system.register_volunteer_for_event(vid, eid)
    system.record_hours(vid, eid, 3.0)
    
    report = system.generate_report(vid)
    
    if "volunteer" in report:
        print(f"✅ Отчет сформирован")
        print(f"   Волонтер: {report['volunteer']['full_name']}")
        print(f"   Часы: {report['volunteer']['total_hours']}")
        print(f"   Участий: {len(report['events'])}")
    else:
        print(f"❌ Ошибка формирования отчета")
    
    return "volunteer" in report

def test_security():
    """Тест разграничения прав"""
    print("\n--- TC-09: Тест разграничения прав ---")
    system = VolunteerSystem()
    system.login("admin", "admin123")
    
    # Создаем волонтера
    _, _, vid = system.register_volunteer(
        "Обычный Волонтер", 
        "volunteer@example.com", 
        "+79001112233", 
        []
    )
    
    # Создаем пользователя-волонтера
    success, msg = system.create_user(
        "test_volunteer", 
        "pass123", 
        UserRole.VOLUNTEER,
        vid
    )
    system.logout()
    
    # Вход как волонтер
    system.login("test_volunteer", "pass123")
    
    # Пытаемся создать мероприятие (должно быть отказано)
    success, msg, _ = system.create_event(
        "Попытка создания",
        datetime(2026, 8, 1, 10, 0),
        "Место",
        "Описание",
        5
    )
    
    if not success:
        print(f"✅ Права ограничены корректно: {msg}")
    else:
        print(f"❌ Ошибка безопасности: волонтер смог создать мероприятие")
    
    return not success

def main():
    print("=" * 60)
    print("ЗАПУСК ТЕСТОВ СИСТЕМЫ «ВОЛОНТЁРПЛЮС»")
    print("=" * 60)
    
    tests = [
        (test_registration, "TC-01/TC-02: Регистрация и просмотр"),
        (test_login, "TC-08: Авторизация"),
        (test_create_event, "TC-03: Создание мероприятия"),
        (test_record_hours, "TC-04/TC-05: Запись и часы"),
        (test_report, "TC-06: Формирование отчетов"),
        (test_security, "TC-09: Разграничение прав"),
    ]
    
    results = []
    for test_func, test_name in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Ошибка при выполнении {test_name}: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("ИТОГИ ТЕСТИРОВАНИЯ:")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    # Исправленный цикл вывода результатов
    for i in range(total):
        test_name = tests[i][1]
        result = results[i]
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print(f"\nПройдено: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    else:
        print(f"\n⚠️ НЕ ПРОЙДЕНО ТЕСТОВ: {total - passed}")
    
    input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    main()