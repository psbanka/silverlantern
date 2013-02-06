#web: python manage.py runserver 0.0.0.0:$PORT
#web: python bin/gunicorn_django --workers=4 --bind=0.0.0.0:$PORT main/settings.py
web: mkdir /app/main/static; python manage.py collectstatic --noinput; python bin/gunicorn_django --workers=4 --bind=0.0.0.0:$PORT main/settings.py
