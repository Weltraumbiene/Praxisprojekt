import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
import fnmatch
from urllib.parse import urlparse

from .logs import log_message

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

def normalize_url(url):
    """
    Normalisiert die URL, indem Fragment (#...) entfernt und Trailing Slash bereinigt wird.
    """
    return url.split("#")[0].rstrip("/")

def crawl_website(base_url, exclude_patterns=None, max_depth=3):
    """
    Crawlt die Website und beachtet dabei die Ausschlussmuster und maximale Crawltiefe.
    """
    msg_start = f"\n[Scan gestartet] Ziel-URL: {base_url}"
    print(msg_start)
    log_message(msg_start)

    msg_depth = f"[⚙️  Crawltiefe eingestellt]: {max_depth} Ebene(n)"
    print(msg_depth)
    log_message(msg_depth)

    start_time = time.time()

    if exclude_patterns is None:
        exclude_patterns = []

    visited = set()
    queued = set()
    to_visit = [(normalize_url(base_url), 0)]
    queued.add(normalize_url(base_url))
    pages = []

    while to_visit:
        url, depth = to_visit.pop(0)
        queued.discard(url)

        if url in visited:
            continue
        visited.add(url)

        if depth > max_depth:
            msg_max = f"[Crawler] ⛔ Maximale Tiefe erreicht bei: {url}"
            print(msg_max)
            log_message(msg_max)
            continue

        matched = match_exclusion(url, exclude_patterns)
        if matched:
            msg_excl = f"[Crawler] ⛔ Ausschluss wegen Muster '{matched}': {url}"
            print(msg_excl)
            log_message(msg_excl)
            continue

        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                pages.append({
                    "url": url,
                    "soup": soup
                })

                msg_found = f"[Crawler] ✔ Gefunden: {url} (Tiefe: {depth})"
                print(msg_found)
                log_message(msg_found)

                if depth < max_depth:
                    for link in soup.find_all('a', href=True):
                        link_url = urllib.parse.urljoin(url, link['href'])
                        normalized = normalize_url(link_url)
                        if normalized.startswith(base_url) and normalized not in visited and normalized not in queued:
                            to_visit.append((normalized, depth + 1))
                            queued.add(normalized)

        except Exception as e:
            msg_error = f"[Crawler] ⚠ Fehler bei {url}: {e}"
            print(msg_error)
            log_message(msg_error)
            continue

        time.sleep(0.25)

    end_time = time.time()

    msg_done = f"[Crawler] Abgeschlossen. {len(pages)} Seiten gefunden."
    print(msg_done)
    log_message(msg_done)

    msg_time = f"[Crawler] Dauer: {round(end_time - start_time, 2)} Sekunden.\n"
    print(msg_time)
    log_message(msg_time)

    return {"pages": pages}
