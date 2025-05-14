@echo off
cd /d "%~dp0"

start "Frontend" cmd /k "cd frontend && npm run dev"
start "Backend" cmd /k "cd backend && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 --workers 1"

