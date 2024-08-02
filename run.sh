#!/bin/bash

# Wait for db to be up
echo "Waiting for postgres..."
while ! nc -z db 5432; do
  sleep 1
done
echo "PostgreSQL started"

# Run migrations
python3 manage.py migrate

# Create super-user
echo "from django.contrib.auth.models import User; \
User.objects.filter(username='admin').exists() or \
User.objects.create_superuser('admin', 'LST@example.com', 'LST')" | python3 manage.py shell

# Start Django server
exec python3 manage.py runserver 0.0.0.0:8000