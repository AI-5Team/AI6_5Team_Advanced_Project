@echo off
echo Starting API server on http://localhost:8000 ...
set PYTHONPATH=%~dp0
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --app-dir services\api
pause
