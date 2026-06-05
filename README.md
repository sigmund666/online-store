# Интернет-магазин (витрина)

Интернет-магазин техники: компьютеры, газонокосилки, стиральные машины, аксессуары.

## Команда

| Роль | Имя |
|------|-----|
| Бэкенд (Django) | sigmund666 |
| Фронтенд (React/JS) | Ekaterina-Ogo |
| БД + интеграция | alinak-09 |

## Стек технологий

- Python 3.13+
- Django 6.0.5
- Django REST Framework
- SQLite
- Git / GitHub

## Установка и запуск (локально)

### 1. Клонировать репозиторий

```bash
git clone https://github.com/sigmund666/online-store.git
cd online-store
```

### 2. Создать и активировать виртуальное окружение

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```
### 3. Установить зависимости

```cmd
pip install django djangorestframework Pillow
```

### 4. Выполнить миграции

```cmd
python manage.py makemigrations
python manage.py migrate
```

### 5. Создать суперпользователя

```cmd
python manage.py createsuperuser
```

### 6. Запустить сервер

```cmd
python manage.py runserver
```

### 7. Открыть в браузере

Сайт: 

Админка: http://127.0.0.1:8000/admin

API товаров: http://127.0.0.1:8000/api/products/

## API Endpoints

## API Endpoints

| Метод | Адрес | Описание |
|-------|-------|----------|
| GET | /api/products/ | Список всех товаров |
| GET | /api/products/1/ | Карточка товара |
| GET | /api/categories/ | Список категорий |
| POST | /api/cart/ | Добавить товар в корзину |
| POST | /api/orders/ | Оформить заказ |
| POST | /api/register/ | Регистрация пользователя |
| POST | /api/login/ | Вход (получение токена) |

## Документация

- **DB_ADMIN.md** — документация по базе данных
- **TESTING.md** — тест-кейсы и результаты тестирования

## Структура
```
online-store/
├── core/
├── store/
├── venv/
├── db.sqlite3
├── manage.py
├── README.md
├── DB_ADMIN.md
└── TESTING.md
```
## Статус

В разработке. База данных настроена, API работает.

Дата: 2026-05-26