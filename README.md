# 📊 AbitAssistant

**AbitAssistant** — це Telegram-бот для випускників 11 класів України, який автоматизує процес відстеження заяв абітурієнтів на вступ до ВНЗ. Бот реалізує техніку, описану у [цьому відео](https://www.youtube.com/watch?v=m5YfI8_2ONo), і значно економить час, показуючи конкурентів у зручному вигляді.

[![Donate](https://img.shields.io/badge/💸%20Підтримати%20проєкт-Monobank-orange)](https://send.monobank.ua/jar/23E3WYNesG)
[![Telegram Bot](https://img.shields.io/badge/🤖%20Telegram-Bot-blue?logo=telegram)](https://t.me/AbitAssistant_bot)
[![GitHub](https://img.shields.io/badge/GitHub-OlexiyOdarchuk-black?logo=github)](https://github.com/OlexiyOdarchuk)
[![License: GPLv3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.html)
[![Made in Ukraine](https://img.shields.io/badge/Made%20with%20❤️-in%20Ukraine-ffd700?style=flat&logo=flag&logoColor=blue)](https://t.me/NeShawyha)

---

### 🌐 Мова / Language

- [Українська](README.md)
- [English](README_en.md).

---
## 🛠️ Технології

- [Python](https://www.python.org/)
- [Aiogram](https://github.com/aiogram/aiogram)
- [Selenium](https://pypi.org/project/selenium/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [SQLite](https://sqlite.org/index.html)

---

## 🚀 Швидкий старт

1. Клонуйте репозиторій
   <code>git clone https://github.com/OlexiyOdarchuk/AbitAssistant_Bot.git</code>
   Та зайдіть в його директорію
   <code>cd AbitAssistant_Bot</code>

3. Встановіть [uv](https://docs.astral.sh/uv/getting-started/installation/):

5. Створіть файл `config.py` на основі `config.example.py` та заповніть його своїми даними.

6. Запустіть бота командою:

   <code>uv run bot.py</code>

---

## 🧠 Основний функціонал

- 📥 Парсинг конкурсних списків із [vstup.osvita.ua](https://vstup.osvita.ua)
- 📊 Автоматична обробка та сортування даних
- 🧾 Формування списку конкурентів за обраною спеціальністю
- 🔗 Генерація прямих посилань на абітурієнтів у [abit.poisk](https://abit-poisk.org.ua/)
- 📂 Запис усіх даних у локальну базу даних

---

## 📂 Структура проєкту

У проєкті дотримано чіткої структури: головні файли — в корені, уся логіка — в папці `app/`. Нижче — повний опис з посиланнями:

📦 project_root/<br>
├── [bot.py](./bot.py) — головний файл для запуску бота<br>
├── config.py — конфігураційний файл (створюється на основі [config.example.py](./config.example.py))<br>
├── app/<br>
│   ├── database/ — взаємодія з базою даних (SQLite + SQLAlchemy)<br>
│   │   ├── db.sqlite3 — база данних (створюється під час натискання /start першим користувачем)<br>
│   │   ├── [models.py](./app/database/models.py) — моделі для бази<br>
│   │   ├── [requests.py](./app/database/requests.py) — запити до бази<br>
│   ├── handlers/ — обробка команд та повідомлень користувача<br>
│   │   ├── [\_\_init\_\_.py](./app/handlers/__init__.py) - ініціалізація пакету<br>
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
│   ├── [keyboards.py](./app/keyboards.py) — кнопки та клавіатури<br>
│   ├── [states.py](./app/states.py) — стани FSM<br>

---


## 🌐 Де працює бот?

Скоріше всього, зараз бот працює в робочому режимі в телеграм.

🔗 [Запустити бота](https://t.me/AbitAssistant_bot)

Але якщо він не працює, значить сервер ще не підключений, або технічні роботи, пишіть мені в [телеграм](https://t.me/NeShawyha)


---

## 👤 Автор

- GitHub: [OlexiyOdarchuk](https://github.com/OlexiyOdarchuk)
- Telegram: [@NeShawyha](https://t.me/NeShawyha)

---

## 📄 Ліцензія

Цей проєкт розповсюджується під ліцензією [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html).<br>

Тому робіть свої fork'и цього репозиторію і можливо саме ваша доробка потрапить до нової версії проєкту!
