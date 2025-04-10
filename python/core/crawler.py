# core/crawler.py

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

def is_internal_link(link: str, base_domain: str) -> bool:
    parsed = urlparse(link)
    return (
        parsed.scheme in ["http", "https"] and (
            parsed.netloc == "" or base_domain in parsed.netloc
        )
    )

def normalize_link(href: str, base_url: str) -> str:
    return urljoin(base_url, href.split("#")[0].strip())

def is_valid_href(href: str) -> bool:
    # Ignoriere Mail, Tel, JavaScript, leere Links
    return href and not any(href.lower().startswith(p) for p in ["mailto:", "tel:", "javascript:", "#", "data:"])

def fetch_and_parse(url: str) -> tuple[str, list[str]]:
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        found_links = []

        for link in soup.find_all('a', href=True):
            href = link['href'].strip()
            if is_valid_href(href):
                full_url = normalize_link(href, url)
                found_links.append(full_url)

        return url, found_links
    except Exception as e:
        print(f"⚠️ Fehler beim Laden von {url}: {e}")
        return url, []

def crawl_website(start_url: str, max_pages: int = 20, max_depth: int = 2) -> list[str]:
    visited = set()
    to_visit = [(start_url, 0)]
    results = []

    base_domain = urlparse(start_url).netloc.replace("www.", "")

    with ThreadPoolExecutor(max_workers=5) as executor:
        while to_visit and len(results) < max_pages:
            futures = {}
            batch = []

            # Fülle nächsten Batch bis zur maximalen Seitenzahl
            while to_visit and len(batch) < 5:
                current_url, depth = to_visit.pop(0)
                if current_url in visited or depth > max_depth:
                    continue
                futures[executor.submit(fetch_and_parse, current_url)] = (current_url, depth)
                batch.append(current_url)

            for future in as_completed(futures):
                current_url, depth = futures[future]
                visited.add(current_url)
                results.append(current_url)

                if len(results) >= max_pages:
                    break

                _, found_links = future.result()
                for link in found_links:
                    if is_internal_link(link, base_domain) and link not in visited:
                        to_visit.append((link, depth + 1))

    return results
