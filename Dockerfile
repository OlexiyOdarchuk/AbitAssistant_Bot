FROM python:3.13.3-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    vim \
    fish \
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

# Створюємо ізольованого користувача (безпечніше)
RUN useradd -m botuser

WORKDIR /AbitAssistant_Bot

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

USER botuser

CMD ["python", "bot.py"]
