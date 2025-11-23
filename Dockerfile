FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# 1. System-Pakete für Playwright + Docker CLI Voraussetzungen
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgtk-3-0 libasound2 source-highlight libgbm1 \
    ca-certificates curl gnupg lsb-release \
    && rm -rf /var/lib/apt/lists/*

# 2. Nur Docker CLI installieren (Kein Daemon!)
RUN mkdir -m 0755 -p /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
    $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && apt-get install -y --no-install-recommends \
    docker-ce-cli docker-buildx-plugin docker-compose-plugin \
    && rm -rf /var/lib/apt/lists/*

# 3. Python & Playwright Setup
COPY pyproject.toml .
RUN pip install . --no-cache-dir && \
    playwright install chromium --with-deps

COPY ./browser_autmatisation/get_youre_guide .

# Kein Entrypoint-Hack mehr nötig. Python ist der Boss.
CMD ["python", "main.py"] 
# (Oder was auch immer dein Startbefehl ist)