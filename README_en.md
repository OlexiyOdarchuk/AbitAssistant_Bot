# AbitAssistant_Bot

[![Donate](https://img.shields.io/badge/💸%20Support%20Project-Monobank-orange)](https://send.monobank.ua/jar/23E3WYNesG)
[![Telegram Bot](https://img.shields.io/badge/🤖%20Telegram-Bot-blue?logo=telegram)](https://t.me/AbitAssistant_bot)
[![GitHub](https://img.shields.io/badge/GitHub-OlexiyOdarchuk-black?logo=github)](https://github.com/OlexiyOdarchuk)
[![License: GPLv3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.html)
[![Made in Ukraine](https://img.shields.io/badge/Made%20with%20❤️-in%20Ukraine-ffd700?style=flat&logo=flag&logoColor=blue)](https://t.me/NeShawyha)

### 🌐 Language

- [Українська](README.md)
- [English](README_en.md)

## 🧾 Description

**AbitAssistant_Bot** is a Telegram bot for Ukrainian high school graduates that automates tracking of university application status. It implements the method described in [this video](https://www.youtube.com/watch?v=m5YfI8_2ONo) and saves a lot of time by displaying competitor data in a clear and convenient way.

---

## 📚 Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Dependencies](#dependencies)
- [Configuration](#configuration)
- [Author](#author)
- [License](#license)

---

## 🧠 Features

- 📥 Parses admission lists from [vstup.osvita.ua](https://vstup.osvita.ua)
- 📊 Automatically processes and sorts data
- 🧾 Generates a list of competitors by selected specialty
- 🔗 Generates direct links to applicants on [abit.poisk](https://abit-poisk.org.ua/)
- 📂 Stores all data in a local database
- 👥 Administrative panel for user management
- 📋 System logging for administrator actions
- 📣 Mass messaging to users

---

## 🛠 Installation

> **Requirements:**
> - Python 3.10+
> - Docker + Docker Compose
> - Telegram Bot Token

### Steps:

1. **Install Docker:**
   - [Official instructions](https://docs.docker.com/get-docker/)

2. **Clone the repository:**
   ```bash
   git clone https://github.com/OlexiyOdarchuk/AbitAssistant_Bot.git
   cd AbitAssistant_Bot
   ```

3. **Configure settings:**
   - Create `config.py` based on `config.example.py`
   - Create `docker-compose.yml` based on `docker-compose.example.yml`

4. **Start the project:**
   ```bash
   docker-compose up --build
   ```

---

## 🚀 Usage

Once started, the bot runs automatically in Telegram.

### 👥 Administrative Features

The bot includes a comprehensive administrative panel for management:

- **👥 Users** — view user list with `tg://user?id=ID` links
- **📣 Mailing** — mass messaging to users
- **📊 Statistics** — general bot statistics
- **📋 Logs** — view system logs and download them

All administrator actions are automatically logged for activity tracking.

---

## 📦 Dependencies

- **Python** + **Aiogram** – bot logic
- **Selenium** – web scraping
- **SQLAlchemy** – ORM for database access
- **PostgreSQL** – primary database
- **Docker** – containerization

---

## ⚙️ Configuration

Before running, copy and configure the following files:

- `config.py` (based on `config.example.py`) — tokens, credentials, and settings.
- `docker-compose.yml` (based on `docker-compose.example.yml`) — environment configuration.

---

## 👤 Author

**Oleksii**
Telegram: [@NeShawyha](https://t.me/NeShawyha)
Gmail: [Email me](mailto:shawyhaf@gmail.com)

---

## 📄 License

This project is licensed under the [GPLv3 License](https://www.gnu.org/licenses/gpl-3.0.html).

---

## 🧡 Support the Project

If this bot helps you, consider supporting the author:

[💸 Support via Monobank](https://send.monobank.ua/jar/23E3WYNesG)

---

## 📂 Project Structure

The project follows a clear structure: key files are in the root, and all logic is within the `app/` folder. Full structure:

📦 project_root/<br>
├── [bot.py](./bot.py) — main bot launcher<br>
├── config.py — main config file (created from [config.example.py](./config.example.py))<br>
├── docker-compose.yml — Docker service config (based on [docker-compose.example.yml](./docker-compose.example.yml))<br>
├── app/<br>
│   ├── database/ — PostgreSQL + SQLAlchemy DB interaction<br>
│   │   ├── [models.py](./app/database/models.py) — DB models<br>
│   │   ├── [requests.py](./app/database/requests.py) — DB queries<br>
│   ├── handlers/ — user command and message handling<br>
│   │   ├── [__init__.py](./app/handlers/__init__.py) — package initializer<br>
│   │   ├── [admin.py](./app/handlers/admin.py) — admin commands<br>
│   │   ├── [common.py](./app/handlers/common.py) — general commands<br>
│   │   ├── [filtering.py](./app/handlers/filtering.py) — data filtering<br>
│   │   ├── [support.py](./app/handlers/support.py) — user feedback<br>
│   │   ├── [viewing.py](./app/handlers/viewing.py) — view applicants<br>
│   ├── services/ — core bot logic (parsing, analysis, generation)<br>
│   │   ├── [applicants_len.py](./app/services/applicants_len.py) — applicant counter<br>
│   │   ├── [parse_in_db.py](./app/services/parse_in_db.py) — parse, analyze, and store<br>
│   │   ├── [generate_link.py](./app/services/generate_link.py) — link generation<br>
│   │   ├── [mailing.py](./app/services/mailing.py) — mailings<br>
│   │   ├── [support.py](./app/services/support.py) — feedback handling<br>
│   │   ├── [user_management.py](./app/services/user_management.py) — user management<br>
│   │   ├── [logger.py](./app/services/logger.py) — logging system<br>
│   │   ├── [stats.py](./app/services/stats.py) — statistics<br>
│   ├── [keyboards.py](./app/keyboards.py) — inline and reply keyboards<br>
│   ├── [states.py](./app/states.py) — FSM states<br>
│   ├── middleware/ — middleware components<br>
│   │   ├── [__init__.py](./app/middleware/__init__.py) — package initializer<br>
│   │   ├── [logging_middleware.py](./app/middleware/logging_middleware.py) — request logging<br>

---

## 📡 Where find?

The bot is currently live and accessible on Telegram:

👉 [@AbitAssistant_bot](https://t.me/AbitAssistant_bot)

---

## 🛠 A Note to Developers

This is an open-source project that welcomes contributions. If you want to improve it — **fork the repo**, make your changes, and create a pull request.

> 💡 Your contribution might be included in the next official release!
