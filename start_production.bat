@echo off
REM Production startup script for ShopSmart AI (Windows)

echo 🚀 Starting ShopSmart AI Production Server...

REM Set production environment
set FLASK_ENV=production

REM Initialize database if needed
if not exist "instance\ecommerce.db" (
    echo 📊 Initializing database...
    python scripts\init_database.py
)

REM Start with Gunicorn
echo 🌐 Starting Gunicorn server...
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 --keep-alive 5 app:app