# AbitAssistant_Bot

[![Donate](https://img.shields.io/badge/💸%20Підтримати%20проєкт-Monobank-orange)](https://send.monobank.ua/jar/23E3WYNesG)
[![Telegram Bot](https://img.shields.io/badge/🤖%20Telegram-Bot-blue?logo=telegram)](https://t.me/AbitAssistant_bot)
[![GitHub](https://img.shields.io/badge/GitHub-OlexiyOdarchuk-black?logo=github)](https://github.com/OlexiyOdarchuk)
[![License: GPLv3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.html)
[![Made in Ukraine](https://img.shields.io/badge/Made%20with%20❤️-in%20Ukraine-ffd700?style=flat&logo=flag&logoColor=blue)](https://t.me/NeShawyha)

## 🧾 Опис

**AbitAssistant_Bot** — це Telegram-бот для випускників 11 класів України, який автоматизує процес відстеження заяв абітурієнтів на вступ до ВНЗ. Бот реалізує техніку, описану у [цьому відео](https://www.youtube.com/watch?v=m5YfI8_2ONo), і значно економить час, показуючи конкурентів у зручному вигляді.

---

## 📚 Зміст

- [AbitAssistant\_Bot](#abitassistant_bot)
  - [🧾 Опис](#-опис)
  - [📚 Зміст](#-зміст)
  - [🧠 Функціонал](#-функціонал)
  - [🛠 Інсталяція](#-інсталяція)
    - [Кроки](#кроки)
  - [🚀 Використання](#-використання)
  - [📦 Залежності](#-залежності)
  - [⚙️ Конфігурація](#️-конфігурація)
  - [👤 Автор](#-автор)
  - [Gmail: Написати лист](#gmail-написати-лист)
  - [📄 Ліцензія](#-ліцензія)
  - [🧡 Підтримати проєкт](#-підтримати-проєкт)
  - [📂 Структура проєкту](#-структура-проєкту)
  - [📡 Де шукати?](#-де-шукати)
    - [P.S. Він буде зараз ще трохи на доробках, тоді вже релізнеться і буде працювати 24/7, бо зараз він актуальний тільки 1 місяць в рік](#ps-він-буде-зараз-ще-трохи-на-доробках-тоді-вже-релізнеться-і-буде-працювати-247-бо-зараз-він-актуальний-тільки-1-місяць-в-рік)
  - [🛠 Звернення до розробників](#-звернення-до-розробників)

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
>
> - Docker + Docker Compose
> - Telegram Bot Token

### Кроки

1. **Встановити Docker:**
   - [Офіційна інструкція](https://docs.docker.com/get-docker/)

2. **Клонувати репозиторій:**

   ```bash
   git clone https://github.com/OlexiyOdarchuk/AbitAssistant_Bot.git
   cd AbitAssistant_Bot
   ```

3. **Налаштувати конфігурацію:**
   - Створіть `.env` на основі `.env.example`

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
- **aiohttp** – парсинг даних з вебсайтів
- **SQLAlchemy** – ORM для роботи з базою даних
- **PostgreSQL** – основна СУБД
- **Docker** – контейнеризація

---

## ⚙️ Конфігурація

Перед запуском обов’язково скопіюйте і налаштуйте файл `.env` відповідно до [.env.example](.env.example)

---

## 👤 Автор

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

📦 project_root/  
├── [bot.py](./bot.py) — головний файл для запуску бота  
├── [.env](.env) — файл зі змінними оточення. (стоворюється на основі [.env.example](.env.example))  
├── config.py — конфігураційний файл  
├── docker-compose.yml — конфігурація Docker-сервісів  
├── app/  
│   ├── database/ — взаємодія з базою даних PostgreSQL + SQLAlchemy  
│   │   ├── [models.py](./app/database/models.py) — моделі для бази  
│   │   ├── [requests.py](./app/database/requests.py) — запити до бази  
│   ├── handlers/ — обробка команд та повідомлень користувача  
│   │   ├── [\_\_init\_\_.py](./app/handlers/__init__.py) — ініціалізація пакету  
│   │   ├── [admin.py](./app/handlers/admin.py) — адмін-команди  
│   │   ├── [common.py](./app/handlers/common.py) — загальні команди  
│   │   ├── [filtering.py](./app/handlers/filtering.py) — фільтрація даних  
│   │   ├── [support.py](./app/handlers/support.py) — зворотній зв'язок  
│   │   ├── [viewing.py](./app/handlers/viewing.py) — перегляд абітурієнтів  
│   ├── services/ — основна логіка бота (парсинг, аналіз, генерація)  
│   │   ├── [applicants_len.py](./app/services/applicants_len.py) — підрахунок абітурієнтів  
│   │   ├── [parse_in_db.py](./app/services/parse_in_db_OLD.py) — парсинг, аналіз і додавання даних до БД  
│   │   ├── [generate_link.py](./app/services/generate_link.py) — генерування посилань  
│   │   ├── [mailing.py](./app/services/mailing.py) — розсилки  
│   │   ├── [support.py](./app/services/support.py) — обробка відгуків  
│   │   ├── [user_management.py](./app/services/user_management.py) — управління користувачами  
│   │   ├── [logger.py](./app/services/logger.py) — система логування  
│   │   ├── [stats.py](./app/services/stats.py) — статистика  
│   ├── [keyboards.py](./app/keyboards.py) — кнопки та клавіатури  
│   ├── [states.py](./app/states.py) — стани FSM  

---

## 📡 Де шукати?

~~Бот вже працює і доступний у Telegram~~:

👉 [@AbitAssistant_bot](https://t.me/AbitAssistant_bot)

### P.S. Він буде зараз ще трохи на доробках, тоді вже релізнеться і буде працювати 24/7, бо зараз він актуальний тільки 1 місяць в рік

---

## 🛠 Звернення до розробників

Проєкт відкритий до розвитку і вдосконалення. Якщо ви хочете допомогти — **fork'айте репозиторій**, вносьте зміни і створюйте pull request'и.

> 💡 Можливо саме ваша доробка потрапить до нової версії проєкту!
