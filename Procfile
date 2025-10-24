web: python manage.py create_initial_users && gunicorn hbb_core.wsgi:application -c gunicorn.conf.py
worker: celery -A hbb_core worker --loglevel=info --concurrency=2
