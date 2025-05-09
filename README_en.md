# 📊 AbitAssistant

**AbitAssistant** is a Telegram bot for Ukrainian high school graduates that automates the process of tracking applicants' applications to universities. The bot implements the technique described in [this video](https://www.youtube.com/watch?v=m5YfI8_2ONo) and significantly saves time, showing competitors in a convenient format.

[![Donate](https://img.shields.io/badge/💸%20Підтримати%20проєкт-Monobank-orange)](https://send.monobank.ua/jar/23E3WYNesG)
[![Telegram Bot](https://img.shields.io/badge/🤖%20Telegram-Bot-blue?logo=telegram)](https://t.me/AbitAssistant_bot)
[![GitHub](https://img.shields.io/badge/GitHub-OlexiyOdarchuk-black?logo=github)](https://github.com/OlexiyOdarchuk)
[![License: GPLv3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.html)
[![Made in Ukraine](https://img.shields.io/badge/Made%20with%20❤️-in%20Ukraine-ffd700?style=flat&logo=flag&logoColor=blue)](https://t.me/NeShawyha)

---

### 🌐 Мова / Language

- [Українська](README.md)
- [English](README_en.md)

---

## 🛠️ Technologies

- [Python](https://www.python.org/)
- [Aiogram](https://github.com/aiogram/aiogram)
- [Selenium](https://pypi.org/project/selenium/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [SQLite](https://sqlite.org/index.html)

---

### 🚀 Quick Start

1. Clone the repository
   <code>git clone https://github.com/OlexiyOdarchuk/AbitAssistant_Bot.git</code>
   Then go to the directory
   <code>cd AbitAssistant_Bot</code>

3. Install [uv](https://docs.astral.sh/uv/getting-started/installation/):

5. Create a `config.py` file based on `config.example.py` and fill it with your data.

6. Run the bot with the command:

   <code>uv run bot.py</code>

---

### 🧠 Main Features

- 📥 Parsing competitive lists from [vstup.osvita.ua](https://vstup.osvita.ua)
- 📊 Automatic data processing and sorting
- 🧾 Generating a list of competitors for a selected specialty
- 🔗 Generating direct links to applicants in [abit.poisk](https://abit-poisk.org.ua/)
- 📂 Saving all data in a local database

---

### 📂 Project Structure

The project has a clear structure: main files are at the root, all logic is in the `app/` folder. Below is the full description with links:

📦 project_root/<br>
├── [bot.py](./bot.py) — main bot file<br>
├── config.py — configuration file (created from [config.example.py](./config.example.py))<br>
├── app/<br>
│   ├── database/ — database interaction (SQLite + SQLAlchemy)<br>
│   │   ├── db.sqlite3 — database (created during the /start command by the first user)<br>
│   │   ├── [models.py](./app/database/models.py) — models for the database<br>
│   │   ├── [requests.py](./app/database/requests.py) — database queries<br>
│   ├── handlers/ — handling commands and user messages<br>
│   │   ├── [\_\_init\_\_.py](./app/handlers/__init__.py) - package initialization<br>
│   │   ├── [admin.py](./app/handlers/admin.py) — admin commands<br>
│   │   ├── [common.py](./app/handlers/common.py) — common commands<br>
│   │   ├── [filtering.py](./app/handlers/filtering.py) — data filtering<br>
│   │   ├── [support.py](./app/handlers/support.py) — feedback<br>
│   │   ├── [viewing.py](./app/handlers/viewing.py) — viewing applicants<br>
│   ├── services/ — main bot logic (parsing, analysis, generation)<br>
│   │   ├── [applicants_len.py](./app/services/applicants_len.py) — counting applicants<br>
│   │   ├── [parse_in_db.py](./app/services/parse_in_db.py) — parsing, analysis, and adding data to the DB<br>
│   │   ├── [generate_link.py](./app/services/generate_link.py) — generating links<br>
│   │   ├── [mailing.py](./app/services/mailing.py) — mailings<br>
│   │   ├── [support.py](./app/services/support.py) — handling feedback<br>
│   ├── [keyboards.py](./app/keyboards.py) — buttons and keyboards<br>
│   ├── [states.py](./app/states.py) — FSM states<br>

---

### 🌐 Where the bot works?

Most likely, the bot is running in Telegram.

🔗 [Run the bot](https://t.me/AbitAssistant_bot)

If it is not working, it means the server is not yet connected or technical work is being carried out, please contact me via [Telegram](https://t.me/NeShawyha)

---

### 👤 Author

- GitHub: [OlexiyOdarchuk](https://github.com/OlexiyOdarchuk)
- Telegram: [@NeShawyha](https://t.me/NeShawyha)

---

### 📄 License

This project is licensed under [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html).<br>

Feel free to fork this repository, and maybe your contribution will become part of the next version of the project!
