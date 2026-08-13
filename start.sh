#!/usr/bin/env bash
set -e

echo "Starting deployment..."

# Find python
PYTHON=$(which python3 || which python)
echo "Using Python: $PYTHON"

# Ensure pip is up to date
$PYTHON -m pip install --upgrade pip --quiet

# Install dependencies
echo "Installing Python dependencies..."
$PYTHON -m pip install -r requirements.txt --quiet

# Run migrations
echo "Running database migrations..."
$PYTHON manage.py migrate || true

# Ensure the SuperAdmin panel account exists (staff+superuser). Idempotent -
# only sets a password the first time (if the account has none yet).
echo "Ensuring superadmin account..."
$PYTHON manage.py ensure_superadmin || true

# Seed data (only if first run - won't duplicate if already exists)
echo "Seeding data..."
$PYTHON manage.py seed_data || true

# Collect static files
echo "Collecting static files..."
$PYTHON manage.py collectstatic --noinput || true

# Start gunicorn
echo "Starting gunicorn on port ${PORT:-8000}..."
exec $PYTHON -m gunicorn ulsavam_backend.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 1
