# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install system dependencies
RUN apt update && apt install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Set the .env file (for runtime use)
ENV ENV_FILE .env

# Add model if .gguf file is present
RUN file=$(find . -name "*.gguf" -print -quit) && [ -n "$file" ] && llm llama-cpp add-model "$file" || echo "No .gguf file found, skipping command"

# Command to run the application with .env file
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--env-file", ".env"]
