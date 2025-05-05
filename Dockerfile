FROM python:3.12-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

RUN mkdir -p /app/data /app/database && chmod 777 /app/data /app/database

# Set user to non-root
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Temporarily set user to root for permissions
USER appuser

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]