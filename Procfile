web: MPLBACKEND=Agg OPENCV_VIDEOIO_DEBUG=0 python manage.py migrate && gunicorn nutriscan.wsgi --bind 0.0.0.0:${PORT:-8000} --workers 1 --timeout 300 --keep-alive 75
