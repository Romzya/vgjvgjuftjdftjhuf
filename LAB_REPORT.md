# Отчет по лабораторной работе: Настройка и работа с Git

**Дата проведения:** [17.09.2025]
**Команда:** ИСП34

Участники команды:
| Тимлид | Петров Роман | ✅ |
| Разработчик 1 | Наговицын Ян | ✅ |
| Тестировщик | Чутов| ✅ |

 *Ссылка на репозиторий:*https://github.com/Romzya/vgjvgjuftjdftjhuf

 ### 2. Настройка окружения и первое коммит

Создал ветку develop от main и запушил её на сервер.
<br/> git checkout main    
git pull origin main   # Убедился, что локальная main актуальна
git checkout -b develop
git push -u origin develop

Участники команды переключились на ветку develop:
git fetch origin          # Получили информацию о новых ветках с сервера
git checkout develop

Пример работы в feature-ветке:
# Создание ветки от актуальной develop
git checkout develop
git pull origin develop
git checkout -b feature/my-new-feature


# Создание коммитов
git add .
git commit -m "Add user login method"

# продолжение работы
git add .
git commit -m "Fix validation bug in email field"

# Пуш ветки на сервер
git push -u origin feature/my-new-feature

Обновил локальную ветку develop:
git checkout develop
git pull origin develop


