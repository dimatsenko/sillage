release: python manage.py migrate && python create_superuser.py
web: python manage.py collectstatic --noinput && gunicorn core.wsgi:application --log-file -
