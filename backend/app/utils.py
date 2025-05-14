#anwendung/backend/app/utils.py
import csv
import os
import html
from datetime import datetime
from urllib.parse import urlparse
from fastapi.responses import FileResponse

latest_issues = []
latest_website = ""

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

    sorted_issues = sorted(latest_issues, key=lambda x: (x.get("type", ""), x.get("url", "")))
    filepath, filename = create_filename(latest_website, "csv")

    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Fehlertyp", "Beschreibung", "URL", "Codeauszug"])
        for idx, issue in enumerate(sorted_issues, start=1):
            snippet = issue.get("snippet", "-")
            snippet = snippet[:250] + "…" if len(snippet) > 250 else snippet
            writer.writerow([
                idx,
                issue.get("type", "Unbekannt"),
                issue.get("description", "Keine Beschreibung"),
                issue.get("url", "Unbekannt"),
                snippet
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
        <title>Barrierefreiheitsreport – {html.escape(latest_website)}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 2rem; color: #222; }}
            h1 {{ font-size: 1.5rem; margin-bottom: 1rem; }}
            table {{ border-collapse: collapse; width: 100%; font-size: 0.95rem; }}
            th, td {{ border: 1px solid #ccc; padding: 0.5rem; text-align: left; vertical-align: top; }}
            th {{ background-color: #f2f2f2; }}
            pre {{ white-space: pre-wrap; word-break: break-word; margin: 0; }}
            .preview-img {{ max-height: 80px; display: block; margin-top: 0.5rem; border: 1px solid #ccc; }}
        </style>
    </head>
    <body>
        <h1>Barrierefreiheitsreport – {html.escape(latest_website)}</h1>
        <table>
            <tr><th>ID</th><th>Fehlertyp</th><th>Beschreibung</th><th>URL</th><th>Codeauszug</th></tr>
    """

    for idx, issue in enumerate(latest_issues, start=1):
        try:
            raw_snippet = issue.get("snippet", "-") or "-"
            short_snippet = raw_snippet[:250] + "…" if len(raw_snippet) > 250 else raw_snippet
            snippet = html.escape(short_snippet)
            url = html.escape(issue.get("url", "Unbekannt"))
            desc = html.escape(issue.get("description", "Keine Beschreibung"))
            typ = html.escape(issue.get("type", "Unbekannt"))

            img_html = ""
            if issue.get("type") == "image_alt_missing":
                src = issue.get("image_src", "")
                if src and src.startswith("http") and "'" not in src:
                    img_html = f"<img src=\"{html.escape(src)}\" alt=\"Vorschaubild\" class=\"preview-img\" />"

            html_content += f"""
                <tr>
                    <td>{idx}</td>
                    <td>{typ}</td>
                    <td>{desc}</td>
                    <td><a href="{url}">{url}</a></td>
                    <td><pre>{snippet}</pre>{img_html}</td>
                </tr>
            """
        except Exception as e:
            continue

    html_content += "</table></body></html>"

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
    except Exception as write_err:
        raise RuntimeError(f"Fehler beim Schreiben der HTML-Datei: {write_err}")

    return FileResponse(filepath, media_type="text/html", filename=filename)
