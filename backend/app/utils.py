# Anwendung\backend\app\main.py
import csv
import os
import html
from datetime import datetime
from urllib.parse import urlparse
from fastapi.responses import FileResponse

# Globale Daten
latest_issues = []
latest_website = ""

# Status-Log für laufenden Scan
scan_log = {
    "running": False,
    "current_page": None,
    "current_step": None,
    "errors": [],
    "last_success": None
}

def reset_scan_log():
    scan_log.update({
        "running": False,
        "current_page": None,
        "current_step": None,
        "errors": [],
        "last_success": None
    })

REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

def sanitize_filename(value):
    return "".join(c for c in value if c.isalnum() or c in (' ', '_', '-')).rstrip()

def create_filename(website, extension):
    now = datetime.now()
    date_part = now.strftime("D%d%m%Y")
    time_part = now.strftime("T%H%M")
    website_clean = sanitize_filename(urlparse(website).netloc or "unknown")
    filename = f"{date_part}_{time_part}_{website_clean}.{extension}"
    return os.path.join(REPORTS_DIR, filename), filename

def save_latest_scan(issues, website):
    global latest_issues, latest_website
    latest_issues = issues
    latest_website = website

def generate_csv():
    if not latest_issues:
        raise ValueError("Keine Scan-Daten verfügbar für CSV-Export.")

    # Sortieren nach Fehlertyp und danach URL
    sorted_issues = sorted(
        latest_issues,
        key=lambda x: (x.get("type", ""), x.get("url", ""))
    )

    filepath, filename = create_filename(latest_website, "csv")

    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Fehlertyp", "Beschreibung", "URL", "Codeauszug"])

        for idx, issue in enumerate(sorted_issues, start=1):
            writer.writerow([
                idx,
                issue.get("type", "Unbekannt"),
                issue.get("description", "Keine Beschreibung"),
                issue.get("url", "Unbekannt"),
                issue.get("snippet", "-")
            ])

    return FileResponse(filepath, media_type='text/csv', filename=filename)


def generate_html():
    if not latest_issues:
        raise ValueError("Keine Scan-Daten verfügbar für HTML-Export.")
    filepath, filename = create_filename(latest_website, "html")
    html_content = f"""
    <!DOCTYPE html>
    <html lang='de'>
    <head>
        <meta charset='UTF-8'>
        <title>Barrierefreiheitsreport – {latest_website}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 2rem; color: #222; }}
            h1 {{ font-size: 1.5rem; margin-bottom: 1rem; }}
            table {{ border-collapse: collapse; width: 100%; font-size: 0.95rem; }}
            th, td {{ border: 1px solid #ccc; padding: 0.5rem; text-align: left; vertical-align: top; }}
            th {{ background-color: #f2f2f2; }}
            a {{ color: #0057D9; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            pre {{ white-space: pre-wrap; word-break: break-word; margin: 0; }}
        </style>
    </head>
    <body>
        <h1>Barrierefreiheitsreport – {latest_website}</h1>
        <table>
            <tr><th>ID</th><th>Fehlertyp</th><th>Beschreibung</th><th>URL</th><th>Codeauszug</th></tr>
    """
    for idx, issue in enumerate(latest_issues, start=1):
        snippet = html.escape(issue.get('snippet', '-'))
        url = issue.get("url", "Unbekannt")
        html_content += (
            f"<tr>"
            f"<td>{idx}</td>"
            f"<td>{issue.get('type', 'Unbekannt')}</td>"
            f"<td>{issue.get('description', 'Keine Beschreibung')}</td>"
            f"<td><a href='{url}'>{url}</a></td>"
            f"<td><pre>{snippet}</pre></td>"
            f"</tr>"
        )
    html_content += "</table></body></html>"
    with open(filepath, "w", encoding='utf-8') as f:
        f.write(html_content)
    return FileResponse(filepath, media_type='text/html', filename=filename)
