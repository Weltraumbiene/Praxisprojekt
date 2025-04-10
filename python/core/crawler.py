# core/crawler.py

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re

def is_internal_link(link: str, base_domain: str) -> bool:
    parsed = urlparse(link)
    return parsed.netloc == "" or base_domain in parsed.netloc

def normalize_link(href: str, base_url: str) -> str:
    return urljoin(base_url, href.split("#")[0])

def crawl_website(start_url: str, max_pages: int = 20, max_depth: int = 2) -> list[str]:
    visited = set()
    to_visit = [(start_url, 0)]
    results = []

    base_domain = urlparse(start_url).netloc

    while to_visit and len(results) < max_pages:
        current_url, depth = to_visit.pop(0)
        if current_url in visited or depth > max_depth:
            continue

        try:
            response = requests.get(current_url, timeout=10)
            visited.add(current_url)
            results.append(current_url)

            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = normalize_link(href, current_url)

                if is_internal_link(full_url, base_domain) and full_url not in visited:
                    to_visit.append((full_url, depth + 1))

        except Exception as e:
            print(f"Fehler beim Laden von {current_url}: {e}")

    return results
