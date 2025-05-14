# /backend/app/scan_controller.py
import threading
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup

from .checker import (
    check_contrast, check_image_alt, check_links,
    check_buttons, check_labels, check_headings, check_aria_roles
)
from .crawler import crawl_website
from .logs import log_message
from .utils import save_latest_scan

scan_running = False
scan_result = []

def run_scan_thread(url: str, exclude: list, full: bool, max_depth: int):
    global scan_running, scan_result

    if scan_running:
        log_message("[⚠️ Thread doppelt gestartet – wird abgebrochen]")
        return

    scan_running = True
    scan_result = []

    try:
        log_message(f"\n[🚀 Scan gestartet] Ziel: {url}")
        log_message(f"[⚙️  Crawltiefe eingestellt]: {max_depth}")
        if exclude:
            log_message(f"[⚙️  Ausschlüsse aktiviert]: {', '.join(exclude)}")
        log_message(f"[⚙️  Modus]: {'Vollscan' if full else 'Nur aktuelle URL'}")

        if not full:
            pages = [{"url": url, "soup": None}]
        else:
            result = crawl_website(url, exclude_patterns=exclude, max_depth=max_depth)
            pages = result.get("pages", [])

        log_message(f"[🔍 Gesammelte Seiten]: {len(pages)}")

        issues = []
        for page in pages:
            page_url = page["url"]
            soup = page["soup"]

            if not soup:
                try:
                    resp = requests.get(page_url, timeout=5)
                    soup = BeautifulSoup(resp.text, 'html.parser')
                except Exception as e:
                    log_message(f"[❌ Fehler beim Nachladen {page_url}]: {e}")
                    continue

            log_message(f"\n[📝 Prüfung gestartet für]: {page_url}")
            for check_func, label in [
                (check_contrast, "Kontraste"),
                (check_image_alt, "Bild ALT-Texte"),
                (check_links, "Links"),
                (check_buttons, "Buttons"),
                (check_labels, "Formulare"),
                (check_headings, "Überschriften"),
                (check_aria_roles, "ARIA-Rollen")
            ]:
                log_message(f"  → {label}...")
                time.sleep(0.1)
                new_issues = check_func(page_url, soup)
                log_message(f"     ↳ {len(new_issues)} gefunden")
                issues.extend(new_issues)

            log_message(f"[✅ Fertig: {page_url}]")

        seen = set()
        unique_issues = []
        for issue in issues:
            key = (issue.get("type"), issue.get("snippet"))
            if key not in seen:
                seen.add(key)
                unique_issues.append(issue)

        log_message(f"\n[📊 Scan abgeschlossen] {len(unique_issues)} eindeutige Probleme gefunden.")
        save_latest_scan(unique_issues, url)
        scan_result = unique_issues

    finally:
        scan_running = False

def start_background_scan(url: str, exclude: list, full: bool, max_depth: int):
    global scan_running
    if scan_running:
        raise RuntimeError("Ein Scan läuft bereits")
    thread = threading.Thread(target=run_scan_thread, args=(url, exclude, full, max_depth))
    thread.start()

def is_scan_running():
    return scan_running

def get_scan_result():
    return scan_result
