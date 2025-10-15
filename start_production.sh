#!/bin/bash
# Production startup script for ShopSmart AI

echo "🚀 Starting ShopSmart AI Production Server..."

# Set production environment
export FLASK_ENV=production

# Initialize database if needed
if [ ! -f "instance/ecommerce.db" ]; then
    echo "📊 Initializing database..."
    python scripts/init_database.py
fi

# Start with Gunicorn
echo "🌐 Starting Gunicorn server..."
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 --keep-alive 5 app:app