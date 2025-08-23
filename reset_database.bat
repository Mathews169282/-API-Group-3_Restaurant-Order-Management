@echo off
echo Resetting database...

REM Remove existing database if it exists
if exist db.sqlite3 (
    echo Removing existing database...
    del db.sqlite3
)

echo Creating new database and applying migrations...
python manage.py migrate

echo Creating superuser...
python manage.py createsuperuser --username=admin --email=admin@example.com --noinput

echo Loading sample data...
python manage.py create_sample_menu

echo Database reset complete!
pause
