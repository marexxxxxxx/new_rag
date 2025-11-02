# === STAGE 1: Der "Builder" ===
FROM python:3.12 AS builder

WORKDIR /app

# Installiere Build-Tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Erstelle ein virtuelles Environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Installiere Python-Abhängigkeiten
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# === STAGE 2: Das finale "Slim" Image ===
FROM python:3.12-slim

WORKDIR /app

# Kopiere das venv aus dem Builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Installiere Playwright System-Abhängigkeiten
RUN apt-get update && \
    python -m playwright install-deps && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Installiere Playwright Browser-Binaries
RUN python -m playwright install

# Kopiere den App-Code
COPY . .

# --- FastAPI Start-Konfiguration ---

# 1. Deklariere den Port, den der Container bereitstellt
EXPOSE 8000

# 2. Starte den Uvicorn-Server
#    HINWEIS: Dies setzt voraus, dass Ihre Datei 'fastapi.py'
#    eine Variable namens 'app' enthält (z.B. app = FastAPI())
CMD ["uvicorn", "fastapi:app", "--host", "0.0.0.0", "--port", "8000"]