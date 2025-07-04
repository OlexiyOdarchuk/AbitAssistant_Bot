# AbitAssistant_Bot

[![Donate](https://img.shields.io/badge/💸%20Підтримати%20проєкт-Monobank-orange)](https://send.monobank.ua/jar/23E3WYNesG)
[![Telegram Bot](https://img.shields.io/badge/🤖%20Telegram-Bot-blue?logo=telegram)](https://t.me/AbitAssistant_bot)
[![GitHub](https://img.shields.io/badge/GitHub-OlexiyOdarchuk-black?logo=github)](https://github.com/OlexiyOdarchuk)
[![License: GPLv3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.html)
[![Made in Ukraine](https://img.shields.io/badge/Made%20with%20❤️-in%20Ukraine-ffd700?style=flat&logo=flag&logoColor=blue)](https://t.me/NeShawyha)

### 🌐 Мова / Language

- [Українська](README.md)
- [English](README_en.md)

## 🧾 Опис

**AbitAssistant_Bot** — це Telegram-бот для випускників 11 класів України, який автоматизує процес відстеження заяв абітурієнтів на вступ до ВНЗ. Бот реалізує техніку, описану у [цьому відео](https://www.youtube.com/watch?v=m5YfI8_2ONo), і значно економить час, показуючи конкурентів у зручному вигляді.

---

## 📚 Зміст

- [Функціонал](#функціонал)
- [Інсталяція](#інсталяція)
- [Використання](#використання)
- [Залежності](#залежності)
- [Конфігурація](#конфігурація)
- [Автор](#автор)
- [Ліцензія](#ліцензія)

---

## 🧠 Функціонал

- 📥 Парсинг конкурсних списків із [vstup.osvita.ua](https://vstup.osvita.ua)
- 📊 Автоматична обробка та сортування даних
- 🧾 Формування списку конкурентів за обраною спеціальністю
- 🔗 Генерація прямих посилань на абітурієнтів у [abit.poisk](https://abit-poisk.org.ua/)
- 📂 Запис усіх даних у локальну базу даних
- 👥 Адміністративна панель з списком користувачів
- 📋 Система логування дій
- 📣 Розсилка повідомлень користувачам

---

## 🛠 Інсталяція

> **Вимоги:**
> - Python 3.10+
> - Docker + Docker Compose
> - Telegram Bot Token

### Кроки:

1. **Встановити Docker:**
   - [Офіційна інструкція](https://docs.docker.com/get-docker/)

2. **Клонувати репозиторій:**
   ```bash
   git clone https://github.com/OlexiyOdarchuk/AbitAssistant_Bot.git
   cd AbitAssistant_Bot
   ```

3. **Налаштувати конфігурацію:**
   - Створіть `config.py` на основі `config.example.py`
   - Створіть `docker-compose.yml` на основі `docker-compose.example.yml`

4. **Запустити проєкт:**
   ```bash
   docker-compose up --build
   ```

---

## 🚀 Використання

Після запуску бот автоматично почне працювати у Telegram.

---

## 📦 Залежності

- **Python** + **Aiogram** – логіка бота
- **Selenium** – парсинг даних з вебсайтів
- **SQLAlchemy** – ORM для роботи з базою даних
- **PostgreSQL** – основна СУБД
- **Docker** – контейнеризація

---

## ⚙️ Конфігурація

Перед запуском обов’язково скопіюйте і налаштуйте такі файли:

- `config.py` (на основі `config.example.py`) — токени, логіни, посилання.
- `docker-compose.yml` (на основі `docker-compose.example.yml`) — налаштування середовища.

---

## 👤 Автор

**Олексій**
Telegram: [@NeShawyha](https://t.me/NeShawyha)
Gmail: [Написати лист](mailto:shawyhaf@gmail.com)
---

## 📄 Ліцензія

Цей проєкт розповсюджується за умовами ліцензії [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html).

---

## 🧡 Підтримати проєкт

Якщо проєкт вам корисний, розгляньте можливість підтримки:

[💸 Підтримати через Monobank](https://send.monobank.ua/jar/23E3WYNesG)


---

## 📂 Структура проєкту

У проєкті дотримано чіткої структури: головні файли — в корені, уся логіка — в папці `app/`. Нижче — повний опис з посиланнями:

📦 project_root/<br>
├── [bot.py](./bot.py) — головний файл для запуску бота<br>
├── config.py — конфігураційний файл (створюється на основі [config.example.py](./config.example.py))<br>
├── docker-compose.yml — конфігурація Docker-сервісів (створюється на основі [docker-compose.example.yml](./docker-compose.example.yml))<br>
├── app/<br>
│   ├── database/ — взаємодія з базою даних PostgreSQL + SQLAlchemy<br>
│   │   ├── [models.py](./app/database/models.py) — моделі для бази<br>
│   │   ├── [requests.py](./app/database/requests.py) — запити до бази<br>
│   ├── handlers/ — обробка команд та повідомлень користувача<br>
│   │   ├── [__init__.py](./app/handlers/__init__.py) — ініціалізація пакету<br>
│   │   ├── [admin.py](./app/handlers/admin.py) — адмін-команди<br>
│   │   ├── [common.py](./app/handlers/common.py) — загальні команди<br>
│   │   ├── [filtering.py](./app/handlers/filtering.py) — фільтрація даних<br>
│   │   ├── [support.py](./app/handlers/support.py) — зворотній зв'язок<br>
│   │   ├── [viewing.py](./app/handlers/viewing.py) — перегляд абітурієнтів<br>
│   ├── services/ — основна логіка бота (парсинг, аналіз, генерація)<br>
│   │   ├── [applicants_len.py](./app/services/applicants_len.py) — підрахунок абітурієнтів<br>
│   │   ├── [parse_in_db.py](./app/services/parse_in_db.py) — парсинг, аналіз і додавання даних до БД<br>
│   │   ├── [generate_link.py](./app/services/generate_link.py) — генерування посилань<br>
│   │   ├── [mailing.py](./app/services/mailing.py) — розсилки<br>
│   │   ├── [support.py](./app/services/support.py) — обробка відгуків<br>
│   │   ├── [user_management.py](./app/services/user_management.py) — управління користувачами<br>
│   │   ├── [logger.py](./app/services/logger.py) — система логування<br>
│   │   ├── [stats.py](./app/services/stats.py) — статистика<br>
│   ├── [keyboards.py](./app/keyboards.py) — кнопки та клавіатури<br>
│   ├── [states.py](./app/states.py) — стани FSM<br>

---

## 📡 Де шукати?

Бот вже працює і доступний у Telegram:

👉 [@AbitAssistant_bot](https://t.me/AbitAssistant_bot)

---

## 🛠 Звернення до розробників

Проєкт відкритий до розвитку і вдосконалення. Якщо ви хочете допомогти — **fork'айте репозиторій**, вносьте зміни і створюйте pull request'и.

> 💡 Можливо саме ваша доробка потрапить до нової версії проєкту!
