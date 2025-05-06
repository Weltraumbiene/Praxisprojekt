@echo off
cd /d "%~dp0"
echo [INFO] Starte Backend-Server...
uvicorn app.main:app --reload
