# Prüfe ob Python installiert ist
$python = Get-Command python -ErrorAction SilentlyContinue

if (-not $python) {
    Write-Host "Python nicht gefunden. Lade Installer..."
    Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe" -OutFile "python-installer.exe"
    Start-Process "python-installer.exe" -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait
    Remove-Item "python-installer.exe"
    Write-Host "Python wurde installiert."
}

# Virtuelle Umgebung und Requirements installieren
python -m venv venv
.\venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
Write-Host "Backend eingerichtet. Starte es mit:"
Write-Host "uvicorn app.main:app --reload"
