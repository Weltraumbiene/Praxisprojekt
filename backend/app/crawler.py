#Anwendung\backend\app\crawler.py
import requests
from bs4 import BeautifulSoup
import urllib.parse

def crawl_website(base_url):
    visited = set()
    to_visit = [base_url]
    pages = []

    while to_visit:
        url = to_visit.pop(0)
        if url in visited:
            continue
        visited.add(url)

        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                pages.append(url)
                for link in soup.find_all('a', href=True):
                    link_url = urllib.parse.urljoin(url, link['href'])
                    if link_url.startswith(base_url) and link_url not in visited:
                        to_visit.append(link_url)
        except:
            continue

    return {'pages': pages}
