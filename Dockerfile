FROM python:3.11-slim

WORKDIR /app

# Install Chrome and ChromeDriver dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for scraped data
RUN mkdir -p scraped_data

# Expose port (Railway will set PORT env var)
EXPOSE 8000

# Set environment variables
ENV HEADLESS_MODE=True
ENV CHROME_DRIVER_PATH=auto

# Run the application (use PORT env var from Railway, default to 8000)
CMD uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}
