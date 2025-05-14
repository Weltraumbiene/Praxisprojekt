#anwendung/backend/app/crawler.py
# anwendung/backend/app/crawler.py
import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
import fnmatch
from urllib.parse import urlparse

def match_exclusion(url, patterns):
    """
    Prüft, ob die URL gegen eines der Ausschlussmuster passt.
    Achtet auch auf fehlenden abschließenden Slash.
    """
    path = urlparse(url).path.rstrip('/')
    for pattern in patterns:
        if fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(path + '/', pattern):
            return pattern
    return None

def crawl_website(base_url, exclude_patterns=None, max_depth=3):
    """
    Crawlt die Website und beachtet dabei die Ausschlussmuster und maximale Crawltiefe.
    """
    print(f"\n[Scan gestartet] Ziel-URL: {base_url}")
    print(f"[⚙️  Crawltiefe eingestellt]: {max_depth} Ebene(n)")

    start_time = time.time()

    if exclude_patterns is None:
        exclude_patterns = []

    visited = set()
    to_visit = [(base_url.rstrip("/"), 0)]  # Tupel aus (URL, Tiefe)
    pages = []

    while to_visit:
        url, depth = to_visit.pop(0)
        clean_url = url.split("#")[0].rstrip("/")

        if clean_url in visited:
            continue
        visited.add(clean_url)

        if depth > max_depth:
            print(f"[Crawler] ⛔ Maximale Tiefe erreicht bei: {clean_url}")
            continue

        matched = match_exclusion(clean_url, exclude_patterns)
        if matched:
            print(f"[Crawler] ⛔ Ausschluss wegen Muster '{matched}': {clean_url}")
            continue

        try:
            response = requests.get(clean_url, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                pages.append({
                    "url": clean_url,
                    "soup": soup
                })

                print(f"[Crawler] ✔ Gefunden: {clean_url} (Tiefe: {depth})")

                if depth < max_depth:
                    for link in soup.find_all('a', href=True):
                        link_url = urllib.parse.urljoin(clean_url, link['href']).split("#")[0].rstrip("/")
                        if link_url.startswith(base_url) and link_url not in visited:
                            to_visit.append((link_url, depth + 1))

        except Exception as e:
            print(f"[Crawler] ⚠ Fehler bei {clean_url}: {e}")
            continue

        time.sleep(0.25)  # Pause zur Schonung des Servers

    end_time = time.time()
    print(f"[Crawler] Abgeschlossen. {len(pages)} Seiten gefunden.")
    print(f"[Crawler] Dauer: {round(end_time - start_time, 2)} Sekunden.\n")

    return {"pages": pages}
