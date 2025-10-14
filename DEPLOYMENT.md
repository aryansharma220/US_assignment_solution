# 🚀 Deployment Guide

Complete guide for deploying the AI-Powered E-commerce Product Recommender to production.

## 📋 Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Production Configuration](#production-configuration)
3. [Deployment Options](#deployment-options)
4. [Database Migration](#database-migration)
5. [Security Hardening](#security-hardening)
6. [Performance Optimization](#performance-optimization)
7. [Monitoring & Logging](#monitoring--logging)
8. [Backup Strategy](#backup-strategy)

---

## ✅ Pre-Deployment Checklist

### Code Quality
- [ ] All tests passing (`python scripts/test_integration.py`)
- [ ] No security vulnerabilities in dependencies
- [ ] Code reviewed and approved
- [ ] Documentation up to date
- [ ] API endpoints documented
- [ ] Error handling comprehensive

### Configuration
- [ ] Environment variables properly set
- [ ] Secret keys changed from defaults
- [ ] Gemini API key configured (if using)
- [ ] Database credentials secure
- [ ] Debug mode disabled
- [ ] CORS configured properly

### Infrastructure
- [ ] Server provisioned
- [ ] Domain name configured
- [ ] SSL certificate obtained
- [ ] Firewall rules set
- [ ] Backup system ready
- [ ] Monitoring tools installed

---

## ⚙️ Production Configuration

### 1. Environment Variables

Create production `.env` file:

```ini
# Application
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-generate-with-secrets.token_urlsafe

# Database (PostgreSQL recommended for production)
DATABASE_URI=postgresql://user:password@localhost:5432/recommender_prod

# Gemini AI
GEMINI_API_KEY=your_production_gemini_key

# Security
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax

# Performance
CACHE_TYPE=redis
CACHE_REDIS_URL=redis://localhost:6379/0

# Monitoring
SENTRY_DSN=your_sentry_dsn_here
LOG_LEVEL=INFO
```

### 2. Generate Secure Secret Key

```python
import secrets
print(secrets.token_urlsafe(32))
```

### 3. Database Configuration

**Switch to PostgreSQL**:

```python
# config.py
import os

class ProductionConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    TESTING = False
```

**Install PostgreSQL adapter**:
```bash
pip install psycopg2-binary
```

---

## 🌐 Deployment Options

### Option 1: Heroku (Easiest)

#### Step 1: Prepare Files

**Procfile**:
```
web: gunicorn app:app
```

**runtime.txt**:
```
python-3.11.0
```

**Add to requirements.txt**:
```
gunicorn==21.2.0
psycopg2-binary==2.9.9
```

#### Step 2: Deploy

```bash
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set SECRET_KEY=your_secret_key
heroku config:set GEMINI_API_KEY=your_gemini_key
heroku config:set FLASK_ENV=production

# Deploy
git push heroku master

# Run migrations
heroku run python scripts/populate_data.py

# Open app
heroku open
```

---

### Option 2: AWS (EC2 + RDS)

#### Step 1: Set Up RDS Database

1. Create PostgreSQL RDS instance
2. Note endpoint, username, password
3. Configure security groups (allow port 5432)

#### Step 2: Launch EC2 Instance

1. Choose Ubuntu 22.04 LTS
2. t2.medium or larger recommended
3. Configure security groups:
   - SSH (22)
   - HTTP (80)
   - HTTPS (443)

#### Step 3: Install Dependencies

```bash
# SSH into EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install Nginx
sudo apt install nginx -y

# Install PostgreSQL client
sudo apt install postgresql-client -y
```

#### Step 4: Deploy Application

```bash
# Clone repository
git clone your-repo-url
cd US

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Set up environment
cp .env.example .env
nano .env  # Edit with production values
```

#### Step 5: Configure Gunicorn

**gunicorn_config.py**:
```python
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
timeout = 120
keepalive = 5
errorlog = "/var/log/gunicorn/error.log"
accesslog = "/var/log/gunicorn/access.log"
loglevel = "info"
```

**Create systemd service** (`/etc/systemd/system/recommender.service`):
```ini
[Unit]
Description=Product Recommender
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/US
Environment="PATH=/home/ubuntu/US/venv/bin"
ExecStart=/home/ubuntu/US/venv/bin/gunicorn -c gunicorn_config.py app:app

[Install]
WantedBy=multi-user.target
```

**Start service**:
```bash
sudo systemctl daemon-reload
sudo systemctl start recommender
sudo systemctl enable recommender
```

#### Step 6: Configure Nginx

**/etc/nginx/sites-available/recommender**:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/ubuntu/US/app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

**Enable site**:
```bash
sudo ln -s /etc/nginx/sites-available/recommender /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### Step 7: SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

### Option 3: DigitalOcean App Platform

#### Step 1: Prepare Files

Same as Heroku (Procfile, runtime.txt)

#### Step 2: Deploy

1. Create new app on DigitalOcean
2. Connect GitHub repository
3. Add PostgreSQL database
4. Set environment variables
5. Deploy

---

### Option 4: Docker

#### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application
COPY . .

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run application
CMD ["gunicorn", "-c", "gunicorn_config.py", "app:app"]
```

#### docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URI=postgresql://user:pass@db:5432/recommender
      - SECRET_KEY=${SECRET_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    depends_on:
      - db
      - redis
    restart: always

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=recommender
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  redis:
    image: redis:7-alpine
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    restart: always

volumes:
  postgres_data:
```

#### Deploy

```bash
docker-compose up -d
```

---

## 💾 Database Migration

### From SQLite to PostgreSQL

#### Step 1: Export Data

```bash
sqlite3 recommender.db .dump > dump.sql
```

#### Step 2: Convert & Import

```bash
# Convert SQLite syntax to PostgreSQL
sed 's/AUTOINCREMENT/SERIAL/g' dump.sql > postgres_dump.sql

# Import to PostgreSQL
psql -h your-host -U your-user -d recommender_prod -f postgres_dump.sql
```

#### Step 3: Update Connection String

```python
# .env
DATABASE_URI=postgresql://user:password@host:5432/recommender_prod
```

---

## 🔒 Security Hardening

### 1. Application Security

**Update config.py**:

```python
class ProductionConfig:
    # Security headers
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600
    
    # Disable debug
    DEBUG = False
    TESTING = False
    
    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
```

**Add security headers** (in app.py):

```python
from flask import Flask
from flask_talisman import Talisman

app = Flask(__name__)
Talisman(app, 
    force_https=True,
    strict_transport_security=True,
    content_security_policy={
        'default-src': "'self'",
        'script-src': ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"],
        'style-src': ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
        'font-src': ["'self'", "https://fonts.gstatic.com"],
    }
)
```

### 2. Rate Limiting

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/recommend/<int:user_id>')
@limiter.limit("10 per minute")
def get_recommendations(user_id):
    # ... implementation
```

### 3. Input Validation

```python
from flask import request, abort

@app.route('/api/recommend/<int:user_id>')
def get_recommendations(user_id):
    # Validate user_id
    if user_id < 1 or user_id > 1000000:
        abort(400, "Invalid user ID")
    
    # Validate query params
    limit = request.args.get('limit', 5, type=int)
    if limit < 1 or limit > 20:
        abort(400, "Limit must be between 1 and 20")
```

### 4. Database Security

- Use parameterized queries (SQLAlchemy does this)
- Limit database user permissions
- Enable SSL for database connections
- Regular security audits

### 5. API Key Protection

```python
# Don't log API keys
import logging
logging.getLogger('google.generativeai').setLevel(logging.WARNING)

# Use environment variables only
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
```

---

## ⚡ Performance Optimization

### 1. Caching

**Install Redis**:
```bash
pip install flask-caching redis
```

**Configure caching** (in app.py):

```python
from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.environ.get('CACHE_REDIS_URL', 'redis://localhost:6379/0')
})

@app.route('/api/products')
@cache.cached(timeout=300, query_string=True)
def get_products():
    # ... implementation
```

### 2. Database Indexing

```python
# models.py
class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    category = db.Column(db.String(50), index=True)
    brand = db.Column(db.String(100), index=True)
    price = db.Column(db.Float, nullable=False, index=True)
```

### 3. Query Optimization

```python
# Use eager loading
user = User.query.options(
    db.joinedload(User.interactions)
).filter_by(id=user_id).first()

# Limit results
products = Product.query.limit(100).all()

# Use pagination
products = Product.query.paginate(page=1, per_page=20)
```

### 4. Static File Optimization

**Minify CSS/JS**:
```bash
pip install cssmin jsmin

# Create build script
python scripts/minify_assets.py
```

**Use CDN** for static assets:
- Host on AWS S3 + CloudFront
- Or use Cloudflare

### 5. Gunicorn Workers

```python
# gunicorn_config.py
import multiprocessing

workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gevent'  # For better concurrency
```

---

## 📊 Monitoring & Logging

### 1. Application Logging

**Configure logging** (in app.py):

```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    # File handler
    file_handler = RotatingFileHandler(
        'logs/recommender.log',
        maxBytes=10240000,
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    
    app.logger.setLevel(logging.INFO)
    app.logger.info('Recommender startup')
```

### 2. Error Tracking (Sentry)

```bash
pip install sentry-sdk[flask]
```

```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=[FlaskIntegration()],
    traces_sample_rate=0.1
)
```

### 3. Performance Monitoring

**Add timing middleware**:

```python
import time
from flask import g, request

@app.before_request
def before_request():
    g.start = time.time()

@app.after_request
def after_request(response):
    diff = time.time() - g.start
    if diff > 1.0:  # Log slow requests
        app.logger.warning(f'Slow request: {request.path} took {diff:.2f}s')
    return response
```

### 4. Health Checks

```python
@app.route('/health')
def health_check():
    try:
        # Check database
        db.session.execute('SELECT 1')
        
        # Check Redis (if using)
        cache.get('health_check')
        
        return jsonify({
            'status': 'healthy',
            'database': 'ok',
            'cache': 'ok'
        }), 200
    except Exception as e:
        app.logger.error(f'Health check failed: {str(e)}')
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503
```

---

## 💾 Backup Strategy

### 1. Database Backups

**Automated daily backups**:

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_NAME="recommender_prod"

# PostgreSQL backup
pg_dump -h localhost -U user $DB_NAME | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete
```

**Cron job**:
```cron
0 2 * * * /path/to/backup.sh
```

### 2. Code Backups

- Use Git for version control
- Push to GitHub/GitLab
- Tag releases
- Keep production branch separate

### 3. Recovery Plan

1. **Database Recovery**:
   ```bash
   gunzip < backup.sql.gz | psql -h localhost -U user recommender_prod
   ```

2. **Code Recovery**:
   ```bash
   git checkout production
   git pull origin production
   ```

3. **Test Recovery**:
   - Restore to staging environment first
   - Verify data integrity
   - Test critical paths
   - Then restore to production

---

## 🚀 Final Launch Checklist

### Before Launch
- [ ] All tests passing
- [ ] Security audit complete
- [ ] Performance testing done
- [ ] Load testing completed
- [ ] Backup system tested
- [ ] Monitoring configured
- [ ] SSL certificate installed
- [ ] Domain configured
- [ ] Error tracking setup
- [ ] Documentation updated

### Launch Day
- [ ] Deploy to production
- [ ] Run database migrations
- [ ] Verify all endpoints
- [ ] Test critical user flows
- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] Verify backup ran successfully

### Post-Launch
- [ ] Monitor for 24 hours
- [ ] Check error logs
- [ ] Review performance
- [ ] Gather user feedback
- [ ] Document issues
- [ ] Plan improvements

---

## 📞 Support

For deployment help:
- Check logs first
- Review error messages
- Consult documentation
- Open GitHub issue

---

**Good luck with your deployment! 🚀**
