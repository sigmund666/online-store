# Документация администратора баз данных (АБД)

**Проект:** Интернет-магазин (компьютеры, газонокосилки, стиральные машины)  
**Дата:** 2026-05-24  

---

## 1. Общие сведения

| Параметр | Значение |
|----------|----------|
| Тип БД | SQLite |
| Файл БД | `db.sqlite3` |
| Расположение | Корневая папка проекта `online-store` |

---

## 2. Структура БД

### Таблица `categories` (категории)
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER | Первичный ключ |
| name | TEXT | Название категории |
| parent_id | INTEGER | Ссылка на родительскую категорию |

### Таблица `products` (товары)
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER | Первичный ключ |
| name | TEXT | Название товара |
| description | TEXT | Описание |
| price | DECIMAL(10,2) | Цена в BYN |
| stock | INTEGER | Количество на складе |
| category_id | INTEGER | Внешний ключ → categories.id |
| image | TEXT | Путь к изображению |
| is_active | BOOLEAN | Активен (1) или нет (0) |

### Таблица `orders` (заказы)
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER | Номер заказа |
| user_id | INTEGER | Внешний ключ → auth_user.id |
| status | VARCHAR(20) | Статус (pending, confirmed, shipped, delivered, cancelled) |
| total | DECIMAL(10,2) | Общая сумма |
| address | TEXT | Адрес доставки |
| created_at | DATETIME | Дата создания |

### Таблица `order_items` (позиции заказа)
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER | Первичный ключ |
| order_id | INTEGER | Внешний ключ → orders.id |
| product_id | INTEGER | Внешний ключ → products.id |
| quantity | INTEGER | Количество |
| unit_price | DECIMAL(10,2) | Цена на момент заказа |

### Таблица `cart_items` (корзина)
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER | Первичный ключ |
| session_id | TEXT | Для неавторизованных |
| user_id | INTEGER | Для авторизованных (→ auth_user.id) |
| product_id | INTEGER | Внешний ключ → products.id |
| quantity | INTEGER | Количество |

---

## 3. Связи между таблицами
categories ──┐
│
products ────┼── order_items ─── orders
│ │
cart_items ──┘ │
└── users


| Связь | Тип | Поле |
|-------|-----|------|
| categories → products | один ко многим | `products.category_id` |
| products → order_items | один ко многим | `order_items.product_id` |
| orders → order_items | один ко многим | `order_items.order_id` |
| users → orders | один ко многим | `orders.user_id` |

---

## 4. Резервное копирование

### Создать копию (Windows)
```cmd
copy db.sqlite3 db_backup.sqlite3
```
---

## 5. Результаты тестирования БД

| N | Название теста | Результат |
|---|----------------|-----------|
| 1 | Проверка наличия таблиц | Пройден |
| 2 | Проверка наличия данных | Пройден (4 категории, 16 товаров) |
| 3 | Проверка внешних ключей | Пройден |