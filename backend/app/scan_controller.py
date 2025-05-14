# /backend/app/scan_controller.py
import threading
import time
from typing import Optional

from .checker import (
    check_contrast, check_image_alt, check_links,
    check_buttons, check_labels, check_headings, check_aria_roles
)
from .crawler import crawl_website
from .logs import log_message
from .utils import save_latest_scan
import requests
from bs4 import BeautifulSoup

# Globalstatus
scan_running = False
scan_result = []


def run_scan_thread(url: str, exclude: list, full: bool, max_depth: int):
    global scan_running, scan_result
    scan_running = True
    scan_result = []

    try:
        log_message(f"\n[🚀 Scan gestartet] Ziel: {url}")
        log_message(f"[⚙️  Crawltiefe]: {max_depth}")

        if exclude:
            log_message(f"[⚙️  Ausschluss]: {', '.join(exclude)}")
        if not full:
            log_message("[⚙️  Modus: Nur eingegebene URL wird geprüft]")

        if not full:
            result = {"pages": [{"url": url, "soup": None}]}
        else:
            result = crawl_website(url, exclude_patterns=exclude, max_depth=max_depth)

        issues = []
        log_message(f"[🔍 Crawler] {len(result['pages'])} Seiten gesammelt.")

        for page in result['pages']:
            page_url = page['url']
            soup = page['soup']

            if not soup:
                try:
                    resp = requests.get(page_url, timeout=5)
                    soup = BeautifulSoup(resp.text, 'html.parser')
                except:
                    log_message(f"[❌ Fehler beim Laden: {page_url}]")
                    continue

            log_message(f"\n[📝 Prüfe] {page_url}")
            for check_func, label in [
                (check_contrast, "Kontraste"),
                (check_image_alt, "Bilder ALT"),
                (check_links, "Links"),
                (check_buttons, "Buttons"),
                (check_labels, "Formulare"),
                (check_headings, "Überschriften"),
                (check_aria_roles, "ARIA")
            ]:
                log_message(f"  → {label}...")
                time.sleep(0.1)  # etwas Delay für Log-Rhythmus
                new_issues = check_func(page_url, soup)
                log_message(f"     ↳ {len(new_issues)} gefunden")
                issues.extend(new_issues)

            log_message(f"[✅ Fertig mit {page_url}]")

        seen = set()
        unique_issues = []
        for issue in issues:
            key = (issue.get("type"), issue.get("snippet"))
            if key not in seen:
                seen.add(key)
                unique_issues.append(issue)

        log_message(f"\n[📊 Scan abgeschlossen] {len(unique_issues)} Probleme gefunden.")
        save_latest_scan(unique_issues, url)
        scan_result = unique_issues

    finally:
        scan_running = False


# API-Zugriffsfunktionen

def start_background_scan(url: str, exclude: list, full: bool, max_depth: int):
    if scan_running:
        raise RuntimeError("Ein Scan läuft bereits")
    thread = threading.Thread(target=run_scan_thread, args=(url, exclude, full, max_depth))
    thread.start()


def is_scan_running():
    return scan_running


def get_scan_result():
    return scan_result
