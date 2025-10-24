web: python manage.py add_user --username mdpetry1 --email matt.petry@searchai.io --first-name Matt --last-name Petry --password "Easton712022!!" && gunicorn hbb_core.wsgi:application -c gunicorn.conf.py
worker: celery -A hbb_core worker --loglevel=info --concurrency=2
