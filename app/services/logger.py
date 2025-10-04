# Copyright (c) 2025 iShawyha. All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging
import logging.handlers
import os
from datetime import datetime
from typing import Optional

# Створюємо папку для логів якщо її немає
if not os.path.exists("logs"):
    os.makedirs("logs")

# Глобальні змінні для відстеження ініціалізованих логерів
_initialized_loggers = set()
_handlers_created = False
_handlers = {}


def create_handlers():
    """Створює хендлери для логування (викликається один раз)"""
    global _handlers_created, _handlers
    if _handlers_created:
        return

    # Форматтер для логів
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Хендлер для всіх логів (general.log)
    general_handler = logging.handlers.RotatingFileHandler(
        "logs/general.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    general_handler.setLevel(logging.INFO)
    general_handler.setFormatter(formatter)
    general_handler.set_name("general_handler")

    # Хендлер для помилок (errors.log)
    error_handler = logging.handlers.RotatingFileHandler(
        "logs/errors.log",
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    error_handler.set_name("error_handler")

    # Хендлер для адміністративних дій (admin.log)
    admin_handler = logging.handlers.RotatingFileHandler(
        "logs/admin.log",
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
        encoding="utf-8",
    )
    admin_handler.setLevel(logging.INFO)
    admin_handler.setFormatter(formatter)
    admin_handler.set_name("admin_handler")

    # Хендлер для дій користувачів (users.log)
    user_handler = logging.handlers.RotatingFileHandler(
        "logs/users.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    user_handler.setLevel(logging.INFO)
    user_handler.setFormatter(formatter)
    user_handler.set_name("user_handler")

    # Хендлер для парсингу (parsing.log)
    parsing_handler = logging.handlers.RotatingFileHandler(
        "logs/parsing.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    parsing_handler.setLevel(logging.INFO)
    parsing_handler.setFormatter(formatter)
    parsing_handler.set_name("parsing_handler")

    # Консольний хендлер (тільки для розробки)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    console_handler.set_name("console_handler")

    # Зберігаємо хендлери глобально
    _handlers = {
        "general": general_handler,
        "error": error_handler,
        "admin": admin_handler,
        "user": user_handler,
        "parsing": parsing_handler,
        "console": console_handler,
    }

    _handlers_created = True


def setup_logger(name: str = "AbitAssistant") -> logging.Logger:
    """Налаштовує логер з правильним розділенням по типах"""

    # Створюємо хендлери один раз
    create_handlers()

    # Перевіряємо чи логер вже ініціалізований
    if name in _initialized_loggers:
        return logging.getLogger(name)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Очищаємо існуючі хендлери
    logger.handlers.clear()

    # Додаємо відповідні хендлери залежно від типу логера
    if name == "AbitAssistant.users":
        logger.addHandler(_handlers["user"])
        logger.addHandler(_handlers["general"])
    elif name == "AbitAssistant.admin":
        logger.addHandler(_handlers["admin"])
        logger.addHandler(_handlers["general"])
    elif name == "AbitAssistant.errors":
        logger.addHandler(_handlers["error"])
        logger.addHandler(_handlers["general"])
    elif name == "AbitAssistant.parsing":
        logger.addHandler(_handlers["parsing"])
        logger.addHandler(_handlers["general"])
    else:
        # Основний логер - додаємо всі хендлери
        logger.addHandler(_handlers["general"])
        logger.addHandler(_handlers["console"])

    _initialized_loggers.add(name)
    return logger


# Основний логер
def log_user_action(
    user_id: int, username: Optional[str], action: str, details: Optional[str] = None
):
    """Логує дії користувачів"""
    user_logger = setup_logger("AbitAssistant.users")
    message = f"USER {user_id} (@{username or 'unknown'}) - {action}"
    if details:
        message += f" - {details}"
    user_logger.info(message)


def log_admin_action(admin_id: int, action: str, details: Optional[str] = None):
    """Логує адміністративні дії"""
    admin_logger = setup_logger("AbitAssistant.admin")
    message = f"ADMIN {admin_id} - {action}"
    if details:
        message += f" - {details}"
    admin_logger.info(message)


def log_parsing_action(
    user_id: int, action: str, details: Optional[str] = None, url: Optional[str] = None
):
    """Логує дії парсингу"""
    parsing_logger = setup_logger("AbitAssistant.parsing")
    message = f"PARSING {user_id} - {action}"
    if details:
        message += f" - {details}"
    if url:
        message += f" - URL: {url}"
    parsing_logger.info(message)


def log_parsing_step(
    user_id: int, step: str, details: Optional[str] = None, count: Optional[int] = None
):
    """Логує окремі кроки парсингу"""
    parsing_logger = setup_logger("AbitAssistant.parsing")
    message = f"PARSING_STEP {user_id} - {step}"
    if details:
        message += f" - {details}"
    if count is not None:
        message += f" - Count: {count}"
    parsing_logger.info(message)


def log_error(error: Exception, context: Optional[str] = None):
    """Логує помилки"""
    error_logger = setup_logger("AbitAssistant.errors")
    message = f"ERROR: {type(error).__name__}: {str(error)}"
    if context:
        message += f" - Context: {context}"
    error_logger.error(message, exc_info=True)


def log_system_event(event: str, details: Optional[str] = None):
    """Логує системні події"""
    logger = setup_logger("AbitAssistant")
    message = f"SYSTEM: {event}"
    if details:
        message += f" - {details}"
    logger.info(message)


def get_log_files() -> dict:
    """Повертає список доступних лог файлів"""
    log_files = {}
    log_dir = "logs"

    if os.path.exists(log_dir):
        for filename in os.listdir(log_dir):
            if filename.endswith(".log"):
                file_path = os.path.join(log_dir, filename)
                file_size = os.path.getsize(file_path)
                modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))

                log_files[filename] = {
                    "path": file_path,
                    "size": file_size,
                    "modified": modified_time,
                    "size_mb": round(file_size / (1024 * 1024), 2),
                }

    return log_files


def get_log_content(filename: str, lines: int = 100) -> Optional[str]:
    """Отримує останні N рядків з лог файлу"""
    file_path = os.path.join("logs", filename)

    if not os.path.exists(file_path):
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            all_lines = f.readlines()
            return "".join(all_lines[-lines:])
    except Exception as e:
        log_error(e, f"Error reading log file {filename}")
        return None
