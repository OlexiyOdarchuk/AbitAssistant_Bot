# AbitAssistant_Bot · v2.x (Python) — ⚠️ Архівовано

> **🚀 Проєкт переїхав на Go.**  
> Активна розробка триває тут: **[github.com/OlexiyOdarchuk/abit-assistant](https://github.com/OlexiyOdarchuk/abit-assistant)**

[![Status: Archived](https://img.shields.io/badge/status-archived-lightgrey.svg)](https://github.com/OlexiyOdarchuk/abit-assistant)
[![Successor: abit-assistant](https://img.shields.io/badge/⤳%20Successor-abit--assistant-00ADD8?logo=go)](https://github.com/OlexiyOdarchuk/abit-assistant)
[![Telegram Bot](https://img.shields.io/badge/🤖%20Telegram-Bot-blue?logo=telegram)](https://t.me/AbitAssistant_bot)
[![License: GPLv3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.html)
[![Made in Ukraine](https://img.shields.io/badge/Made%20with%20❤️-in%20Ukraine-ffd700)](https://t.me/NeShawyha)

---

## 📦 Куди тепер

| | v2.x (цей repo) | v3.0 (новий repo) |
|---|---|---|
| Мова | Python · Aiogram | **Go · telebot/v3** |
| БД | PostgreSQL + SQLAlchemy | **SQLite + sqlc** (pure-Go, без CGo) |
| Архітектура | моноліт `app/` | **Standard Go Layout** (`cmd / pkg / internal`) |
| Як бібліотека | — | **`go get github.com/OlexiyOdarchuk/abit-assistant/pkg/abit`** |
| FSM | aiogram, in-memory | Persistent у SQLite (переживає рестарт) |
| Тести | — | 70+ unit-тестів |
| Docker | `python:slim` ~400MB | `scratch` ~30MB |

Telegram-бот **той самий** — [@AbitAssistant_bot](https://t.me/AbitAssistant_bot). Перехід для користувачів безшовний.

---

## 🔁 Чому переїхали

Ідея проєкту росте, і моноліт на Python почав заважати:
- Потрібна **модульність** — щоб довільний розробник міг підключити ядро (`pkg/abit`, `pkg/parser`) до свого бота / десктоп-додатку / CLI через `go get`
- **Легший рантайм** — scratch-Docker ~30MB замість Python+SQLAlchemy+aiohttp ~400MB
- **Конкурентність на горутинах** — парсинг конкурсних списків на горутинах у рази швидший за asyncio
- **Type-safety end-to-end** — sqlc-генеровані запити, типізовані callback-args, доменна модель замість dict-of-anything

Повний план переходу — у [`AbitAssistant-3.0.md`](./AbitAssistant-3.0.md).

---

## ❓ Що з цим repo

- 🟥 **Архівований.** Нові фічі не приймаються, issues — на новому repo.
- 🟩 **Залишається доступним** для історії, навчальних цілей і fork'ів. Якщо тобі цікаво пограти з aiogram / parsing на BeautifulSoup — будь ласка.
- 🟨 Bot-сервер вже **переключено на v3.0** — старий код тут не запущено на проді.

Якщо ти прийшов сюди по код для свого pet-проекту:
- 🐍 Шукаєш Python → залишайся, форкай, веселись
- 🐹 Шукаєш Go → одразу [`abit-assistant`](https://github.com/OlexiyOdarchuk/abit-assistant)

---

## 🧾 Що це було

**AbitAssistant_Bot** — Telegram-бот для абітурієнтів України, який автоматизує відстеження заяв на вступ. Реалізує техніку з [цього відео](https://www.youtube.com/watch?v=m5YfI8_2ONo): «реальних» конкурентів видно одразу, без ручного парсингу `vstup.osvita.ua` в Excel.

### Що вмів
- 📥 Парсинг конкурсних списків із [vstup.osvita.ua](https://vstup.osvita.ua)
- 🔍 abit-poisk lookup для конкретного абітурієнта
- 📊 Розрахунок шансу + ваше місце в реальній черзі
- 📈 Гістограми (matplotlib)
- 👤 Профіль з НМТ балами, квотами, регіональним коеф.
- 💾 Збережені списки + share через deep-link
- 📣 Розсилка для адмінів

Усе перенесене (і покращене) в [v3.0](https://github.com/OlexiyOdarchuk/abit-assistant).

### Стек
- **Python 3** + **Aiogram** — логіка бота
- **aiohttp** + **BeautifulSoup4** — парсинг
- **Pandas** + **NumPy** — обробка
- **Matplotlib** — графіки
- **SQLAlchemy** + **PostgreSQL** — БД
- **Docker** — контейнеризація

---

## 🛠 Якщо хочеш запустити v2.x локально

> ⚠️ Тільки для архівних цілей — для роботи з v3.0 використовуй [новий repo](https://github.com/OlexiyOdarchuk/abit-assistant).

### Docker

```bash
git clone https://github.com/OlexiyOdarchuk/AbitAssistant_Bot.git
cd AbitAssistant_Bot
cp .env.example .env   # заповни TELEGRAM_TOKEN, POSTGRES_* тощо
docker-compose up --build -d
```

### Nix

```bash
git clone https://github.com/OlexiyOdarchuk/AbitAssistant_Bot.git
cd AbitAssistant_Bot
nix develop
make sync
cp .env.example .env
make docker-up
```

---

## 📂 Структура (для довідки)

📦 project_root/  
├── [bot.py](./bot.py) — entrypoint  
├── [config.py](config.py) — конфіг  
├── [docker-compose.yml](docker-compose.yml)  
├── app/  
│   ├── database/  
│   │   ├── [models.py](./app/database/models.py) — SQLAlchemy моделі  
│   │   └── [requests.py](./app/database/requests.py)  
│   ├── handlers/  
│   │   ├── [admin.py](./app/handlers/admin.py)  
│   │   ├── [common.py](./app/handlers/common.py)  
│   │   ├── [filtering.py](./app/handlers/filtering.py)  
│   │   ├── [profile.py](./app/handlers/profile.py)  
│   │   ├── [support.py](./app/handlers/support.py)  
│   │   └── [viewing.py](./app/handlers/viewing.py)  
│   ├── services/  
│   │   ├── [parser.py](./app/services/parser.py) · [decoder.py](./app/services/decoder.py) · [filter.py](./app/services/filter.py)  
│   │   ├── [parse_abit_poisk.py](./app/services/parse_abit_poisk.py) · [generate_link.py](./app/services/generate_link.py)  
│   │   ├── [visualization.py](./app/services/visualization.py) · [stats.py](./app/services/stats.py)  
│   │   ├── [results_cache.py](./app/services/results_cache.py)  
│   │   ├── [mailing.py](./app/services/mailing.py) · [support.py](./app/services/support.py) · [user_management.py](./app/services/user_management.py)  
│   │   └── [logger.py](./app/services/logger.py)  
│   ├── [keyboards.py](./app/keyboards.py) · [states.py](./app/states.py)

---

## 📄 Ліцензія

[GPLv3](https://www.gnu.org/licenses/gpl-3.0.html). Та сама залишається у v3.0.

## 👤 Автор

Олексій Одарчук — Telegram [@NeShawyha](https://t.me/NeShawyha) · [GitHub](https://github.com/OlexiyOdarchuk) · `shawyhaf@gmail.com`

## 💸 Підтримати

Сервери, кава, новий ноут — на одній [Monobank-банці](https://send.monobank.ua/jar/23E3WYNesG). Підтримуєш одразу обидва покоління.

---

### 👉 [github.com/OlexiyOdarchuk/abit-assistant](https://github.com/OlexiyOdarchuk/abit-assistant)
