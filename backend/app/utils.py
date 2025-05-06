#Anwendung\backend\app\utils.py
import csv
import os
from datetime import datetime
from urllib.parse import urlparse
from fastapi.responses import FileResponse

# Externe Abhängigkeit für Website-Titel entfernen, weil wir echten Scan-Daten vertrauen
# import requests
# from bs4 import BeautifulSoup

# NEU: Global gespeicherte letzte Scan-Daten
latest_issues = []
latest_website = ""

REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

def sanitize_filename(value):
    """Hilfsfunktion um Dateinamen sicher zu machen"""
    return "".join(c for c in value if c.isalnum() or c in (' ', '_', '-')).rstrip()

def create_filename(website, extension):
    now = datetime.now()
    date_part = now.strftime("D%d%m%Y")
    time_part = now.strftime("T%H%M")
    website_clean = sanitize_filename(urlparse(website).netloc or "unknown")
    filename = f"{date_part}_{time_part}_{website_clean}.{extension}"
    return os.path.join(REPORTS_DIR, filename), filename

def save_latest_scan(issues, website):
    """Speichert die aktuellen Scan-Daten"""
    global latest_issues, latest_website
    latest_issues = issues
    latest_website = website

def generate_csv():
    """Erzeugt eine CSV-Datei aus den letzten Scan-Daten"""
    if not latest_issues:
        raise ValueError("Keine Scan-Daten verfügbar für CSV-Export.")
    
    filepath, filename = create_filename(latest_website, "csv")

    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Issue", "Description", "URL", "Code Snippet"])

        for idx, issue in enumerate(latest_issues, start=1):
            writer.writerow([
                idx,
                issue.get("type", "Unbekannt"),
                issue.get("description", "Keine Beschreibung"),
                issue.get("url", "Unbekannt"),
                issue.get("snippet", "-")
            ])

    return FileResponse(filepath, media_type='text/csv', filename=filename)

def generate_html():
    """Erzeugt eine HTML-Datei aus den letzten Scan-Daten"""
    if not latest_issues:
        raise ValueError("Keine Scan-Daten verfügbar für HTML-Export.")
    
    filepath, filename = create_filename(latest_website, "html")

    html_content = "<html><body><h1>Accessibility Issues</h1><table border='1'><tr><th>ID</th><th>Issue</th><th>Description</th><th>URL</th><th>Snippet</th></tr>"

    for idx, issue in enumerate(latest_issues, start=1):
        html_content += f"<tr><td>{idx}</td><td>{issue.get('type', 'Unbekannt')}</td><td>{issue.get('description', 'Keine Beschreibung')}</td><td>{issue.get('url', 'Unbekannt')}</td><td>{issue.get('snippet', '-')}</td></tr>"

    html_content += "</table></body></html>"

    with open(filepath, "w", encoding='utf-8') as f:
        f.write(html_content)

    return FileResponse(filepath, media_type='text/html', filename=filename)
