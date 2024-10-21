# Use the official lightweight Python image
FROM python:3.11.5-slim

# Set environment variables
ENV DJANGO_SETTINGS_MODULE=core.settings

# Install necessary system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates curl gnupg build-essential && \
    rm -rf /var/lib/apt/lists/*

# Install Node.js and npm (v18) for building frontend assets
RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_18.x nodistro main" > /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Install and build frontend assets
RUN npm install && \
    npm run build && \
    npx tailwindcss -i ./static/assets/style.css -o ./static/dist/css/output.css

# Collect static files
RUN python manage.py collectstatic --no-input

# Ensure database migrations run only once
RUN python manage.py migrate --noinput

# Expose necessary port for Heroku
EXPOSE 8000

# Start the application with gunicorn

CMD gunicorn core.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --threads 4 --timeout 30 --preload

