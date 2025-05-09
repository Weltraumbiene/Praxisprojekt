# Anwendung\backend\app\crawler.py
import requests
from bs4 import BeautifulSoup
import urllib.parse
import time

def crawl_website(base_url):
    print(f"\n[Scan gestartet] Ziel-URL: {base_url}")
    start_time = time.time()

    visited = set()
    to_visit = [base_url]
    pages = []

    while to_visit:
        url = to_visit.pop(0)
        if url in visited:
            continue
        visited.add(url)

        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                pages.append({
                    "url": url,
                    "soup": soup
                })

                print(f"[Crawler] ✔ Gefunden: {url}")

                for link in soup.find_all('a', href=True):
                    link_url = urllib.parse.urljoin(url, link['href'])
                    if link_url.startswith(base_url) and link_url not in visited:
                        to_visit.append(link_url)
        except Exception as e:
            print(f"[Crawler] ⚠ Fehler bei {url}: {e}")
            continue

    end_time = time.time()
    print(f"[Crawler] Abgeschlossen. {len(pages)} Seiten gefunden.")
    print(f"[Crawler] Dauer: {round(end_time - start_time, 2)} Sekunden.\n")

    return {"pages": pages}
