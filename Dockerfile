# Stage 1: Build Frontend
FROM node:20-alpine as frontend-build

WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .

# Set build-time environment variable for API URL
ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build

# Stage 2: Production - Backend + Frontend
FROM python:3.11-slim

# Create a non-root user
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

WORKDIR /app

# Install system dependencies including nginx and supervisor
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    nginx \
    supervisor \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies as root
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Copy frontend build from previous stage
COPY --from=frontend-build /frontend/dist /var/www/html

# Create nginx configuration for serving frontend and proxying API
RUN echo 'server {\n\
    listen 80;\n\
    server_name localhost;\n\
    \n\
    # Serve frontend\n\
    location / {\n\
        root /var/www/html;\n\
        try_files $uri $uri/ /index.html;\n\
    }\n\
    \n\
    # Proxy API requests to backend\n\
    location /api/ {\n\
        proxy_pass http://127.0.0.1:8000/;\n\
        proxy_set_header Host $host;\n\
        proxy_set_header X-Real-IP $remote_addr;\n\
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n\
        proxy_set_header X-Forwarded-Proto $scheme;\n\
    }\n\
}' > /etc/nginx/sites-available/default

# Create supervisor configuration to run both nginx and backend
RUN echo '[supervisord]\n\
nodaemon=true\n\
user=root\n\
\n\
[program:nginx]\n\
command=nginx -g "daemon off;"\n\
autostart=true\n\
autorestart=true\n\
stdout_logfile=/var/log/nginx/access.log\n\
stderr_logfile=/var/log/nginx/error.log\n\
\n\
[program:backend]\n\
command=uvicorn main:app --host 127.0.0.1 --port 8000\n\
directory=/app\n\
user=appuser\n\
autostart=true\n\
autorestart=true\n\
stdout_logfile=/var/log/backend.log\n\
stderr_logfile=/var/log/backend.log' > /etc/supervisor/conf.d/supervisord.conf

# Change ownership of app directory
RUN chown -R appuser:appuser /app

# Create log directories
RUN mkdir -p /var/log/nginx && touch /var/log/backend.log

# Expose port 80 (nginx will serve frontend and proxy API)
EXPOSE 80

# Start supervisor which will run both nginx and backend
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"] 