# Use the official Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables to make Python behave nicely in Docker
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set the working directory inside the container
WORKDIR /app

# Copy your dependency files first
COPY pyproject.toml uv.lock ./

# Install uv package manager
RUN pip install --no-cache-dir uv

# Install dependencies defined in pyproject.toml
RUN uv sync --frozen --no-dev


# Copy all project files
COPY . .

# Expose port 8000 (FastAPI default)
EXPOSE 8000

# Run the FastAPI app using Uvicorn
CMD [".venv/bin/uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
