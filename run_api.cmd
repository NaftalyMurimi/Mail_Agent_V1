@echo off
call venv\Scripts\activate
cd backend
set PYTHONPATH=.
uvicorn app.main:app --reload