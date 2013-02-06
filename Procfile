#web: python manage.py runserver 0.0.0.0:$PORT
web: python bin/gunicorn_django --workers=4 --bind=0.0.0.0:$PORT main/settings.py
