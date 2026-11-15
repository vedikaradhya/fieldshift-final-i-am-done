# Production Deployment Guide

This guide covers deploying AgriSpace to a production environment.

## Prerequisites

### Infrastructure Requirements
- **Server**: Linux (Ubuntu 22.04+ recommended)
- **CPU**: 2+ cores
- **RAM**: 4GB+ (8GB recommended)
- **Storage**: 20GB+ SSD
- **Docker**: 20.10+
- **Docker Compose**: 2.0+

### External Services
- **PostgreSQL 15+** with PostGIS extension
- **Redis** (optional, for distributed rate limiting)
- **Email provider** (SendGrid, AWS SES, Mailgun, etc.)
- **Domain name** with DNS configured
- **SSL certificate** (Let's Encrypt recommended)

## Quick Start with Docker Compose

### 1. Prepare Environment Variables

Create a `.env` file in the project root:

```bash
# Application
APP_ENV=production
SECRET_KEY=<generate-secure-key-here>

# Database
DATABASE_URL=postgresql+psycopg://agrispace:<strong-password>@db:5432/agrispace

# CORS
CORS_ORIGINS=https://your-domain.com

# Security
SECURE_COOKIES=true
COOKIE_DOMAIN=.your-domain.com

# Features
DEMO_MODE=false
NASA_POWER_ENABLED=true
NASA_POWER_BASE_URL=https://power.larc.nasa.gov/api/temporal/daily/point

# Optional: Google Maps
GOOGLE_MAPS_API_KEY=<your-api-key>

# Token Expiration
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=14
```

### 2. Generate Secure SECRET_KEY

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Use the output as your SECRET_KEY.

### 3. Update docker-compose.yml for Production

```yaml
services:
  db:
    image: postgis/postgis:16-3.4
    environment:
      POSTGRES_DB: agrispace
      POSTGRES_USER: agrispace
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - agrispace-network

  api:
    build: ./backend
    environment:
      DATABASE_URL: postgresql+psycopg://agrispace:${DB_PASSWORD}@db:5432/agrispace
      CORS_ORIGINS: ${CORS_ORIGINS}
      SECRET_KEY: ${SECRET_KEY}
      SECURE_COOKIES: ${SECURE_COOKIES}
      COOKIE_DOMAIN: ${COOKIE_DOMAIN}
      DEMO_MODE: ${DEMO_MODE}
      NASA_POWER_ENABLED: ${NASA_POWER_ENABLED}
    depends_on:
      - db
    restart: unless-stopped
    networks:
      - agrispace-network

  web:
    build: ./frontend
    environment:
      VITE_API_URL: https://api.your-domain.com
    depends_on:
      - api
    restart: unless-stopped
    networks:
      - agrispace-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - web
      - api
    restart: unless-stopped
    networks:
      - agrispace-network

networks:
  agrispace-network:
    driver: bridge

volumes:
  postgres_data:
```

### 4. Configure Nginx Reverse Proxy

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream frontend {
        server web:5173;
    }

    upstream backend {
        server api:8000;
    }

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name your-domain.com www.your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name your-domain.com www.your-domain.com;

        ssl_certificate /etc/nginx/certs/fullchain.pem;
        ssl_certificate_key /etc/nginx/certs/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # Security headers
        add_header X-Frame-Options "DENY" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Backend API
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### 5. Obtain SSL Certificates

```bash
# Install certbot
sudo apt update
sudo apt install certbot

# Generate certificates
sudo certbot certonly --standalone -d your-domain.com -d www.your-domain.com

# Copy certificates to project
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ./certs/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ./certs/
sudo chmod 644 ./certs/*
```

### 6. Deploy

```bash
# Build and start services
docker-compose up -d

# Check logs
docker-compose logs -f

# Verify services
docker-compose ps
```

## Manual Deployment (Without Docker)

### Backend Deployment

#### 1. Install Dependencies

```bash
# Python 3.10+
sudo apt install python3.10 python3.10-venv

# PostgreSQL with PostGIS
sudo apt install postgresql-15 postgis

# System dependencies
sudo apt install libpq-dev build-essential
```

#### 2. Setup Database

```bash
# Create database and user
sudo -u postgres psql
CREATE DATABASE agrispace;
CREATE USER agrispace WITH ENCRYPTED PASSWORD 'strong-password';
GRANT ALL PRIVILEGES ON DATABASE agrispace TO agrispace;
\c agrispace
CREATE EXTENSION postgis;
\q
```

#### 3. Setup Backend

```bash
cd backend
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 4. Configure Environment

```bash
export APP_ENV=production
export SECRET_KEY=<your-secure-key>
export DATABASE_URL=postgresql+psycopg://agrispace:strong-password@localhost:5432/agrispace
export CORS_ORIGINS=https://your-domain.com
export SECURE_COOKIES=true
export COOKIE_DOMAIN=.your-domain.com
```

#### 5. Run with Gunicorn

```bash
pip install gunicorn uvicorn[standard]
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### Frontend Deployment

#### 1. Build for Production

```bash
cd frontend
npm install
npm run build
```

#### 2. Serve with Nginx

```bash
# Copy build to web server
sudo cp -r dist/* /var/www/agrispace/

# Configure Nginx (similar to docker-compose nginx.conf above)
sudo nano /etc/nginx/sites-available/agrispace
sudo ln -s /etc/nginx/sites-available/agrispace /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Post-Deployment Checklist

- [ ] Verify all services are running
- [ ] Test authentication flow
- [ ] Test farm creation and management
- [ ] Verify climate data display
- [ ] Check SSL certificate validity
- [ ] Configure log rotation
- [ ] Set up monitoring (Prometheus/Grafana, DataDog, etc.)
- [ ] Configure backup strategy (database backups)
- [ ] Set up error tracking (Sentry, Rollbar)
- [ ] Configure CDN for static assets (optional)
- [ ] Set up CI/CD pipeline

## Monitoring and Maintenance

### Health Checks

```bash
# Backend health
curl https://api.your-domain.com/health

# Frontend availability
curl https://your-domain.com
```

### Database Backups

```bash
# Daily backup script
#!/bin/bash
pg_dump -U agrispace agrispace > /backups/agrispace_$(date +%Y%m%d).sql
```

### Log Rotation

Configure `/etc/logrotate.d/agrispace`:

```
/var/log/agrispace/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
}
```

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection
psql -U agrispace -d agrispace -h localhost
```

### SSL Certificate Renewal

```bash
# Renew certificates
sudo certbot renew

# Reload nginx
sudo systemctl reload nginx
```

### Performance Issues

- Increase Gunicorn workers (typically 2-4 per CPU core)
- Enable Redis for distributed rate limiting
- Configure database connection pooling
- Enable CDN for static assets
- Consider horizontal scaling with load balancer

## Security Best Practices

1. **Never commit `.env` files** to version control
2. **Use strong, unique passwords** for database
3. **Keep dependencies updated** regularly
4. **Enable firewall** (ufw) to restrict access
5. **Use fail2ban** to prevent brute force attacks
6. **Regular security audits** of dependencies
7. **Enable audit logging** for sensitive operations
8. **Use separate database users** for read/write operations
9. **Implement IP whitelisting** for admin access
10. **Regular backups** stored off-site

## Scaling Considerations

### Horizontal Scaling

- Use load balancer (nginx, HAProxy, AWS ALB)
- Deploy multiple API instances behind load balancer
- Use shared PostgreSQL database
- Use Redis for session storage and rate limiting

### Vertical Scaling

- Increase server CPU/RAM
- Optimize database queries
- Enable database caching
- Use connection pooling

## Cost Optimization

- Use spot instances for non-critical workloads
- Enable auto-scaling based on traffic
- Optimize database storage and queries
- Use CDN for static assets
- Compress and cache responses

## Support

For issues or questions:
- Check logs: `docker-compose logs -f [service]`
- Review documentation in `SECURITY_AND_DEPLOYMENT.md`
- Check GitHub issues for known problems
