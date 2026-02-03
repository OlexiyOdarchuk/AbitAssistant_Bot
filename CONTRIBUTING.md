# Внесок у проєкт

Дякуємо за інтерес до **AbitAssistant_Bot**! 🎉

Цей документ містить інформацію про те, як ви можете допомогти покращити проєкт.

---

## 📋 Зміст

- [Код поведінки](#-код-поведінки)
- [Як я можу допомогти?](#-як-я-можу-допомогти)
- [Процес внесення змін](#-процес-внесення-змін)
- [Стандарти коду](#-стандарти-коду)
- [Налаштування середовища розробки](#-налаштування-середовища-розробки)
- [Тестування](#-тестування)
- [Питання та підтримка](#-питання-та-підтримка)

---

## 📜 Код поведінки

Цей проєкт дотримується [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). Будь ласка, прочитайте його перед початком роботи.

---

## 🤝 Як я можу допомогти?

Є багато способів внести свій внесок:

### 🐛 Повідомлення про помилки

Якщо ви знайшли помилку:

1. Перевірте, чи не створено вже issue з цією проблемою
2. Якщо ні, створіть нове issue, використовуючи [шаблон звіту про помилку](.github/ISSUE_TEMPLATE/bug_report.md)
3. Надайте максимально детальну інформацію:
   - Опис проблеми
   - Кроки для відтворення
   - Очікувана та фактична поведінка
   - Версія Python, залежності
   - Скріншоти (якщо застосовно)

### 💡 Пропозиції нових функцій

Маєте ідею для покращення?

1. Перевірте [Roadmap на Trello](https://trello.com/b/RYCBf2Ve) — можливо, ваша ідея вже там
2. Створіть issue з описом вашої пропозиції
3. Поясніть, чому ця функція буде корисною

### 📝 Покращення документації

Документація завжди потребує покращень:

- Виправлення помилок у README
- Додавання прикладів використання
- Покращення коментарів у коді
- Переклад документації

### 💻 Написання коду

Найбільш цінний внесок — це код! Дивіться розділ [Процес внесення змін](#-процес-внесення-змін).

---

## 🔄 Процес внесення змін

### 1. Fork репозиторію

Натисніть кнопку "Fork" у верхній частині сторінки репозиторію.

### 2. Клонуйте ваш fork

```bash
git clone https://github.com/ВАШЕ_ІМ'Я/AbitAssistant_Bot.git
cd AbitAssistant_Bot
```

### 3. Створіть гілку для ваших змін

```bash
git checkout -b feature/назва-вашої-фічі
# або
git checkout -b fix/опис-виправлення
```

**Приклади назв гілок:**
- `feature/add-new-filter`
- `fix/message-handling-error`
- `docs/update-readme`

### 4. Внесіть зміни

- Дотримуйтесь [стандартів коду](#-стандарти-коду)
- Додавайте коментарі там, де це необхідно
- Переконайтеся, що код працює локально

### 5. Зробіть commit

```bash
git add .
git commit -m "Короткий опис змін"
```

### 6. Відправте зміни

```bash
git push origin feature/назва-вашої-фічі
```

### 7. Створіть Pull Request

1. Перейдіть на сторінку вашого fork на GitHub
2. Натисніть "New Pull Request"
3. Заповніть опис:
   - Що змінено та чому
   - Як це протестовано
   - Посилання на пов'язані issues (якщо є)
4. Натисніть "Create Pull Request"

### 8. Очікуйте на рев'ю

- Можуть бути зауваження або пропозиції
- Будьте готові до обговорення та внесення змін
- Після схвалення ваш PR буде об'єднано з основною гілкою

---

## 📐 Стандарти коду

### Загальні принципи

1. **Читабельність** — код повинен бути зрозумілим для інших розробників
2. **Консистентність** — дотримуйтесь стилю, який вже використовується в проєкті
3. **Коментарі** — додавайте коментарі для складних частин коду
4. **DRY** — не повторюйте код (Don't Repeat Yourself)

### Стиль кодування

- **Мова коментарів та документації**: українська
- **Назви змінних та функцій**: англійська (snake_case)
- **Довжина рядка**: до 100 символів (якщо можливо)

### Структура файлів

```python
# Copyright (c) 2025 iShawyha. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Імпорти стандартної бібліотеки
import os
import asyncio

# Імпорти сторонніх бібліотек
from aiogram import Router
from aiogram.types import Message

# Імпорти з проєкту
from app.services.logger import log_user_action
from config import ADMIN_ID

# Код...
```

### Обробка помилок

Завжди обробляйте помилки та логуйте їх:

```python
try:
    # Ваш код
    pass
except Exception as e:
    log_error(e, f"Опис помилки для контексту")
    # Обробка помилки
```

### Асинхронний код

Проєкт використовує `async/await`. Переконайтеся, що ваш код асинхронний:

```python
async def my_function():
    result = await some_async_operation()
    return result
```

### Логування

Використовуйте функції з `app.services.logger`:

- `log_user_action()` — для дій користувачів
- `log_admin_action()` — для дій адміністраторів
- `log_error()` — для помилок
- `log_system_event()` — для системних подій

---

## 🛠 Налаштування середовища розробки

### Вимоги

- Python 3.13.3 або новіший
- Docker та Docker Compose
- Git

### Кроки

1. **Клонуйте репозиторій** (або ваш fork)

```bash
git clone https://github.com/OlexiyOdarchuk/AbitAssistant_Bot.git
cd AbitAssistant_Bot
```

2. **Створіть файл `.env`**

```bash
cp .env.example .env
```

Заповніть необхідні змінні в `.env`:
- `TELEGRAM_TOKEN` — токен вашого тестового бота
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`, `POSTGRES_PORT`
- `ADMIN_IDS` — ваш Telegram ID (через кому, якщо кілька)

3. **Запустіть через Docker**

```bash
docker-compose up --build
```

Або для локальної розробки (без Docker):

```bash
# Створіть віртуальне середовище
python -m venv venv
source venv/bin/activate  # Linux/macOS
# або
venv\Scripts\activate  # Windows

# Встановіть залежності
pip install -r requirements.txt

# Запустіть PostgreSQL окремо або через Docker
docker-compose up -d

# Запустіть бота
python bot.py
```

### Структура проєкту

```
AbitAssistant_Bot/
├── app/
│   ├── database/        # Моделі та запити до БД
│   ├── handlers/        # Обробники команд та повідомлень
│   ├── services/        # Бізнес-логіка (парсинг, генерація, логування)
│   ├── middleware/      # Middleware для бота
│   ├── keyboards.py     # Клавіатури для Telegram
│   └── states.py        # FSM стани
├── bot.py               # Точка входу
├── config.py            # Конфігурація
└── requirements.txt     # Залежності
```

---

## 🧪 Тестування

Перед відправкою PR переконайтеся, що:

1. **Код працює локально**
   - Бот запускається без помилок
   - Основна функціональність працює

2. **Немає синтаксичних помилок**

3. **Код відповідає стилю проєкту**
   - Перевірте відступи
   - Перевірте назви змінних
   - Перевірте коментарі

4. **Логування працює коректно**
   - Помилки логуються
   - Дії користувачів відстежуються

---

## ❓ Питання та підтримка

Якщо у вас виникли питання:

1. **Перевірте документацію**
   - [README.md](README.md)
   - [LOGGINT_FEATURES.md](LOGGINT_FEATURES.md)

2. **Створіть issue**
   - Використовуйте [шаблон для питань](.github/ISSUE_TEMPLATE/question_or_discussion.md)

3. **Зв'яжіться з автором**
   - Telegram: [@NeShawyha](https://t.me/NeShawyha)
   - Email: [shawyhaf@gmail.com](mailto:shawyhaf@gmail.com)

4. **Напишіть в боті**
   - [@AbitAssistant_bot](https://t.me/AbitAssistant_bot) — розділ підтримки

---

## 📝 Додаткові поради

### Перед початком роботи над великою зміною

1. Створіть issue з описом вашої ідеї
2. Дочекайтеся фідбеку від мейнтейнерів
3. Обговоріть підхід до реалізації

### Якщо ваш PR не прийнято

- Не засмучуйтеся! Це нормальна частина процесу
- Уважно прочитайте коментарі
- Задавайте питання, якщо щось незрозуміло
- Внесіть необхідні зміни

### Дрібні покращення

Навіть дрібні зміни мають значення:
- Виправлення друкарських помилок
- Покращення читабельності коду
- Додавання коментарів
- Оновлення документації

---

## 🎉 Дякуємо!

Ваш внесок допомагає покращити проєкт для всіх користувачів. Дякуємо за ваш час та зусилля! 🙏

---

**Питання?** Створіть issue або зв'яжіться з нами!

