# Use official Python 3.11 slim base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libffi-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY chatbot_backend/requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy entire chatbot_backend code into container
COPY chatbot_backend/ .

# Ensure app is treated as a Python package
RUN touch app/__init__.py

# Expose FastAPI port
EXPOSE 8000

# Start FastAPI app with uvicorn (using correct app object)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
