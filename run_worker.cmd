@echo off
call venv\Scripts\activate
cd backend
set PYTHONPATH=.
celery -A app.celery_app.celery worker --loglevel=info --pool=solo