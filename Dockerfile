FROM python:3.13

WORKDIR /app

ENV HOME=/app
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# --- System deps (BUILD-TIME ROOT) ---
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     tesseract-ocr \
#     tesseract-ocr-rus \
#     poppler-utils \
#     && rm -rf /var/lib/apt/lists/*

# --- Create non-root user ---
RUN groupadd -g 1000 agent \
 && useradd -u 1000 -g agent -m agent

# --- Prepare app dirs and ownership ---
RUN mkdir -p /app/venv /app/work /app/logs \
 && chown -R agent:agent /app

# --- Create venv ---
RUN python -m venv $VIRTUAL_ENV \
 && $VIRTUAL_ENV/bin/pip install --upgrade pip

# --- Python deps ---
COPY requirements.txt .
RUN pip install -r requirements.txt

# --- Runtime: non-root ---
USER agent

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

CMD ["uvicorn", "agent.server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
