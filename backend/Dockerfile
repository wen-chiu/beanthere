FROM python:3.11-slim

WORKDIR /app

# Dependencies install 
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Python Dependencies Installation
RUN pip install --no-cache-dir -r requirements.txt

# source code duplicate
COPY . .

ENV PYTHONPATH=/app

EXPOSE 8000

# Initial command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
