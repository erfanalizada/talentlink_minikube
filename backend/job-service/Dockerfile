# ==============================
# Stage 1 — Base image
# ==============================
FROM python:3.11-slim

# Prevent Python from writing .pyc files & buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies (optional, helps for psycopg2, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (cache layer)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create uploads directory and set ownership so the non-root user can write to it
RUN mkdir -p /app/uploads/cvs \
    && useradd -m appuser \
    && chown -R appuser:appuser /app/uploads

# Switch to non-root user for running the app
USER appuser

# Expose Flask port
EXPOSE 5000

# Run Flask app
CMD ["python", "app.py"]
