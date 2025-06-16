# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy only requirements first (for better caching)
COPY requirements_strict.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements_strict.txt

# Copy app code
COPY . .

EXPOSE 34001

# Run the app
CMD ["python", "server.py"]
