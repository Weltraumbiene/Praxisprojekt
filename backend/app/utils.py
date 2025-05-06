#Anwendung\backend\app\utils.py
import csv
import os
from datetime import datetime
from urllib.parse import urlparse
from fastapi.responses import FileResponse
import requests
from bs4 import BeautifulSoup

REPORTS_DIR = "reports"

# Stellt sicher, dass der Ordner existiert
os.makedirs(REPORTS_DIR, exist_ok=True)

def sanitize_filename(value):
    """Hilfsfunktion um Dateinamen sicher zu machen"""
    return "".join(c for c in value if c.isalnum() or c in (' ', '_', '-')).rstrip()

def extract_title_from_url(url):
    """Ermittelt den <title> der Webseite"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.string if soup.title else "NoTitle"
            return sanitize_filename(title.strip())[:50]  # Max 50 Zeichen
    except Exception:
        pass
    return "NoTitle"

def create_filename_with_title(website, extension):
    now = datetime.now()
    date_part = now.strftime("D%d%m%Y")
    time_part = now.strftime("T%H%M")
    website_clean = sanitize_filename(urlparse(website).netloc or "unknown")
    title_part = extract_title_from_url(website)

    filename = f"{date_part}_{time_part}_{website_clean}_{title_part}.{extension}"
    return os.path.join(REPORTS_DIR, filename), filename

def generate_csv(website="unknown"):
    issues = [
        ["ID", "Issue", "Description", "URL", "Code Snippet"],
        [1, "Missing alt text", "Image missing alt text", "https://example.com", "<img src='image.png'>"],
        [2, "Missing contrast", "Low contrast text", "https://example.com", "<p>Text</p>"]
    ]

    filepath, filename = create_filename_with_title(website, "csv")

    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(issues)

    return FileResponse(filepath, media_type='text/csv', filename=filename)

def generate_html(website="unknown"):
    issues = [
        {"ID": 1, "Issue": "Missing alt text", "Description": "Image missing alt text", "URL": "https://example.com", "Snippet": "<img src='image.png'>"},
        {"ID": 2, "Issue": "Missing contrast", "Description": "Low contrast text", "URL": "https://example.com", "Snippet": "<p>Text</p>"}
    ]

    filepath, filename = create_filename_with_title(website, "html")

    html_content = "<html><body><h1>Accessibility Issues</h1><table border='1'><tr><th>ID</th><th>Issue</th><th>Description</th><th>URL</th><th>Snippet</th></tr>"
    for issue in issues:
        html_content += f"<tr><td>{issue['ID']}</td><td>{issue['Issue']}</td><td>{issue['Description']}</td><td>{issue['URL']}</td><td>{issue['Snippet']}</td></tr>"
    html_content += "</table></body></html>"

    with open(filepath, "w", encoding='utf-8') as f:
        f.write(html_content)

    return FileResponse(filepath, media_type='text/html', filename=filename)
