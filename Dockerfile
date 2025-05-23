FROM python:3.13.3-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libsqlite3-dev \
    wget \
    ca-certificates \
    fonts-liberation \
    libnss3 \
    libxss1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libx11-xcb1 \
    libxcb-dri3-0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdrm2 \
    libxinerama1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /AbitAssistant_Bot

# Копіювання файлів проєкту
COPY . .

# Встановлення Python-залежностей
RUN pip install --no-cache-dir -r requirements.txt

# Команда запуску бота
CMD ["python", "bot.py"]
