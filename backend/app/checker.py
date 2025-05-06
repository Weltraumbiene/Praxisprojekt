#Anwendung\backend\app\checker.py
import requests
from bs4 import BeautifulSoup

def check_contrast(url):
    issues = []  # Beispielhaft leer
    return issues

def check_image_alt(url):
    issues = []
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        for img in soup.find_all('img'):
            if not img.get('alt'):
                issues.append({
                    "type": "image_alt_missing",
                    "url": url,
                    "snippet": str(img),
                    "description": "Image missing alt text"
                })
    except:
        pass
    return issues

def check_links(url):
    issues = []
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        for a in soup.find_all('a'):
            if not a.get('href') or not a.text.strip():
                issues.append({
                    "type": "link_incomplete",
                    "url": url,
                    "snippet": str(a),
                    "description": "Link missing href or text"
                })
    except:
        pass
    return issues
