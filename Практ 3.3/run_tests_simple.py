"""
Простой запуск тестов без pytest
"""

import sys
import traceback

def run_test(test_func, test_name):
    """Запуск одного теста с обработкой ошибок"""
    try:
        test_func()
        print(f"✅ {test_name} - ПРОЙДЕН")
        return True
    except AssertionError as e:
        print(f"❌ {test_name} - НЕ ПРОЙДЕН: {e}")
        return False
    except Exception as e:
        print(f"❌ {test_name} - ОШИБКА: {e}")
        traceback.print_exc()
        return False

# Импортируем тесты
from test_volunteer_system import TestVolunteerSystem
from volunteer_system import VolunteerSystem

def main():
    print("=" * 60)
    print("ЗАПУСК ТЕСТОВ СИСТЕМЫ «ВОЛОНТЁРПЛЮС»")
    print("=" * 60)
    
    test_instance = TestVolunteerSystem()
    results = []
    
    # Список тестов для запуска
    tests = [
        (test_instance.test_register_volunteer_success, "TC-01: Регистрация волонтера"),
        (test_instance.test_register_volunteer_invalid_email, "TC-01_негатив: Неверный email"),
        (test_instance.test_register_volunteer_invalid_phone, "TC-01_негатив: Неверный телефон"),
        (test_instance.test_get_volunteer_profile, "TC-02: Просмотр профиля"),
        (test_instance.test_get_nonexistent_volunteer, "TC-02_негатив: Несуществующий волонтер"),
        (test_instance.test_create_event_success, "TC-03: Создание мероприятия"),
        (test_instance.test_create_event_invalid_max_participants, "TC-03_негатив: Неверное кол-во участников"),
        (test_instance.test_register_volunteer_for_event, "TC-04: Запись на мероприятие"),
        (test_instance.test_register_volunteer_twice, "TC-04_негатив: Повторная запись"),
        (test_instance.test_record_hours_success, "TC-05: Фиксация часов"),
        (test_instance.test_record_hours_exceeds_limit, "TC-05_негатив: Часы > 24"),
        (test_instance.test_generate_report_for_volunteer, "TC-06: Отчет по волонтеру"),
        (test_instance.test_generate_full_report, "TC-06_доп: Полный отчет"),
        (test_instance.test_send_notification_email, "TC-07: Уведомление"),
        (test_instance.test_login_success, "TC-08: Успешный вход"),
        (test_instance.test_login_wrong_password, "TC-08_негатив: Неверный пароль"),
        (test_instance.test_login_nonexistent_user, "TC-08_негатив: Несуществующий пользователь"),
        (test_instance.test_volunteer_cannot_register_volunteer, "TC-09: Разграничение прав"),
        (test_instance.test_coordinator_can_create_event, "TC-09_доп: Права координатора"),
    ]
    
    # Запуск тестов с созданием свежей системы для каждого
    for test_func, test_name in tests:
        # Создаем новый экземпляр класса и систему для каждого теста
        fresh_instance = TestVolunteerSystem()
        
        # Создаем свежую систему
        fresh_instance.system = VolunteerSystem()
        fresh_instance.admin_logged_in = fresh_instance.system
        fresh_instance.system.login("admin", "admin123")
        
        # Получаем метод для текущего теста
        method_name = test_func.__name__
        bound_func = getattr(fresh_instance, method_name)
        
        result = run_test(bound_func, test_name)
        results.append(result)
    
    print("\n" + "=" * 60)
    print("ИТОГИ ТЕСТИРОВАНИЯ:")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Пройдено: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    else:
        print(f"\n⚠️ НЕ ПРОЙДЕНО ТЕСТОВ: {total - passed}")
    
    input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    main()