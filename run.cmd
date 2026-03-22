@REM @echo off
@REM cd backend
@REM set PYTHONPATH=.
@REM uvicorn app.main:app --reload

@echo off
echo Starting Email Manager Agent...
echo.
echo Open THREE CMD windows and run:
echo.
echo   Window 1 (API):    run_api.cmd
echo   Window 2 (Worker): run_worker.cmd
echo   Window 3 (Beat):   run_beat.cmd
echo.
pause