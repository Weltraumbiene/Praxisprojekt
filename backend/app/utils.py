import csv
import os
from fastapi.responses import FileResponse, HTMLResponse

TEMP_CSV_PATH = "scan_results.csv"
TEMP_HTML_PATH = "scan_results.html"

def generate_csv():
    issues = [
        ["ID", "Issue", "Description", "URL", "Code Snippet"],
        [1, "Missing alt text", "Image missing alt text", "https://example.com", "<img src='image.png'>"],
        [2, "Missing contrast", "Low contrast text", "https://example.com", "<p>Text</p>"]
    ]
    with open(TEMP_CSV_PATH, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(issues)
    return FileResponse(TEMP_CSV_PATH, media_type='text/csv', filename="scan_results.csv")

def generate_html():
    issues = [
        {"ID": 1, "Issue": "Missing alt text", "Description": "Image missing alt text", "URL": "https://example.com", "Snippet": "<img src='image.png'>"},
        {"ID": 2, "Issue": "Missing contrast", "Description": "Low contrast text", "URL": "https://example.com", "Snippet": "<p>Text</p>"}
    ]
    html_content = "<html><body><h1>Accessibility Issues</h1><table border='1'><tr><th>ID</th><th>Issue</th><th>Description</th><th>URL</th><th>Snippet</th></tr>"
    for issue in issues:
        html_content += f"<tr><td>{issue['ID']}</td><td>{issue['Issue']}</td><td>{issue['Description']}</td><td>{issue['URL']}</td><td>{issue['Snippet']}</td></tr>"
    html_content += "</table></body></html>"

    with open(TEMP_HTML_PATH, "w", encoding='utf-8') as f:
        f.write(html_content)

    return FileResponse(TEMP_HTML_PATH, media_type='text/html', filename="scan_results.html")
