release: python manage.py migrate
web: gunicorn nutriscan.wsgi --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 60
