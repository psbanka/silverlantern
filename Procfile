#web: python manage.py runserver 0.0.0.0:$PORT
worker: python worker.py
web: python bin/gunicorn_django --workers=4 --bind=0.0.0.0:$PORT main/settings.py
