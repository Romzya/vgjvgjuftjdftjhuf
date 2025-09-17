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
<br/> git pull origin main   # Убедился, что локальная main актуальна
<br/> git checkout -b develop
<br/> git push -u origin develop

Участники команды переключились на ветку develop:
<br/> git fetch origin          # Получили информацию о новых ветках с сервера
<br/> git checkout develop

Пример работы в feature-ветке:
# Создание ветки от актуальной develop
<br/> git checkout develop
<br/> git pull origin develop
<br/> git checkout -b feature/my-new-feature


# Создание коммитов
<br/> git add .
<br/> git commit -m "Add user login method"

# продолжение работы
<br/> git add .
<br/> git commit -m "Fix validation bug in email field"

# Пуш ветки на сервер
<br/> git push -u origin feature/my-new-feature

Обновил локальную ветку develop:
<br/> git checkout develop
<br/> git pull origin develop


