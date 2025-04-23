@echo off
echo Starte Backend...
cd /d "C:\Users\bfranneck\Desktop\Praxisprojekt\Anwendung\python"
start cmd /k "python -m uvicorn main:app --reload"

echo Starte Frontend...
cd /d "C:\Users\bfranneck\Desktop\Praxisprojekt\Anwendung\frontend"
start cmd /k "npm run dev"

echo Starte Testskript...
cd /d "C:\Users\bfranneck\Desktop\Praxisprojekt\Anwendung\python"
start cmd /k "python run_test.py"

echo Alle Dienste wurden gestartet.
