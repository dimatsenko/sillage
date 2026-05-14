web: sh -c "python manage.py migrate && python create_superuser.py && python manage.py collectstatic --noinput && gunicorn core.wsgi:application --log-file -"
