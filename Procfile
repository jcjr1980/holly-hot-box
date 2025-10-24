web: python manage.py add_user --username temp_user --email temp@example.com --first-name Temp --last-name User && gunicorn hbb_core.wsgi:application -c gunicorn.conf.py
worker: celery -A hbb_core worker --loglevel=info --concurrency=2
