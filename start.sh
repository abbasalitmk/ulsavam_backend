#!/usr/bin/env bash
set -e

echo "Starting deployment..."

# Ensure pip is up to date
python -m pip install --upgrade pip

# Install dependencies
echo "Installing Python dependencies..."
python -m pip install -r requirements.txt

# Run migrations
echo "Running database migrations..."
python manage.py migrate || true

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput || true

# Start gunicorn
echo "Starting gunicorn..."
exec gunicorn ulsavam_backend.wsgi:application --bind 0.0.0.0:${PORT:-8000}
