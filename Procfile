web: gunicorn SAF_backend.wsgi:application --bind 0.0.0.0:8000
release: python manage.py migrate
worker: python manage.py process_tasks
