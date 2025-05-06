@echo off
cd /d "%~dp0"

start "Backend" cmd /k "cd backend && uvicorn app.main:app --reload"
start "Frontend" cmd /k "cd frontend && npm run dev"
