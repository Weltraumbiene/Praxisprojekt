from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re

# --- Hilfsfunktionen für Farbkontrast ---
def relative_luminance(r, g, b):
    def adjust(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    R, G, B = adjust(r), adjust(g), adjust(b)
    return 0.2126 * R + 0.7152 * G + 0.0722 * B

def contrast_ratio(hex1, hex2):
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    rgb1 = hex_to_rgb(hex1)
    rgb2 = hex_to_rgb(hex2)

    lum1 = relative_luminance(*rgb1)
    lum2 = relative_luminance(*rgb2)
    L1, L2 = max(lum1, lum2), min(lum1, lum2)
    return round((L1 + 0.05) / (L2 + 0.05), 2)

def extract_inline_color(style):
    fg = re.search(r'color\s*:\s*#?([\da-fA-F]{6})', style or '')
    bg = re.search(r'background-color\s*:\s*#?([\da-fA-F]{6})', style or '')
    return (fg.group(1) if fg else None), (bg.group(1) if bg else 'ffffff')

# --- Prüf-Funktionen ---
def check_contrast(url, soup):
    issues = []
    for tag in soup.find_all(style=True):
        fg_hex, bg_hex = extract_inline_color(tag.get('style'))
        if fg_hex and bg_hex:
            ratio = contrast_ratio(fg_hex, bg_hex)
            if ratio < 4.5:
                issues.append({
                    "type": "contrast_insufficient",
                    "url": url,
                    "snippet": str(tag),
                    "description": f"Kontrast zu gering ({ratio}:1). Erforderlich ≥ 4.5:1",
                    "element": "CONTRAST"
                })
    return issues

def check_image_alt(url, soup):
    issues = []
    title = soup.title.string.strip() if soup.title else "Ohne Titel"
    for img in soup.find_all('img'):
        alt = img.get('alt')
        if alt is None or alt.strip() == "":
            # Mögliche Bildquellen prüfen
            src_candidates = [
                img.get('data-src'),
                img.get('data-orig-src'),
                img.get('data-src-fg'),
                img.get('data-srcset', '').split(' ')[0],
                img.get('src'),
            ]
            # Nur gültige HTTP-URLs, kein base64 oder leeres src
            src = next((s for s in src_candidates if s and not s.strip().startswith("data:")), None)
            abs_src = urljoin(url, src) if src else None

            issues.append({
                "type": "image_alt_missing",
                "url": url,
                "title": title,
                "snippet": str(img),
                "description": "Fehlende Alt-Beschreibung bei Bild",
                "element": "IMG-TAG",
                "image_src": abs_src
            })
    return issues

def check_links(url, soup):
    issues = []
    title = soup.title.string.strip() if soup.title else "Ohne Titel"
    for a in soup.find_all('a'):
        if not a.get('href') or not a.text.strip():
            issues.append({
                "type": "link_incomplete",
                "url": url,
                "title": title,
                "snippet": str(a),
                "description": "Link ohne href oder ohne Linktext",
                "element": "LINK-TAG"
            })
    return issues

def check_buttons(url, soup):
    issues = []
    title = soup.title.string.strip() if soup.title else "Ohne Titel"
    for tag in soup.find_all(['div', 'span']):
        role = tag.get('role', '').lower()
        onclick = tag.get('onclick')
        if onclick or role == 'button':
            issues.append({
                "type": "nonsemantic_button",
                "url": url,
                "title": title,
                "snippet": str(tag),
                "description": "Interaktives Element verwendet kein <button>, sondern <div>/<span>",
                "element": "BUTTON-TAG"
            })
    return issues

def check_labels(url, soup):
    issues = []
    title = soup.title.string.strip() if soup.title else "Ohne Titel"
    inputs = soup.find_all(['input', 'select', 'textarea'])
    label_ids = {label.get('for') for label in soup.find_all('label') if label.get('for')}
    for input in inputs:
        input_id = input.get('id')
        if not input_id or input_id not in label_ids:
            issues.append({
                "type": "form_label_missing",
                "url": url,
                "title": title,
                "snippet": str(input),
                "description": "Formularfeld hat kein zugeordnetes <label>",
                "element": "FORM-TAG"
            })
    return issues

def check_headings(url, soup):
    issues = []
    title = soup.title.string.strip() if soup.title else "Ohne Titel"
    headings = soup.find_all(re.compile('^h[1-6]$'))
    level_sequence = [int(tag.name[1]) for tag in headings]
    for i in range(1, len(level_sequence)):
        if level_sequence[i] > level_sequence[i - 1] + 1:
            issues.append({
                "type": "heading_hierarchy_error",
                "url": url,
                "title": title,
                "snippet": str(headings[i]),
                "description": "Überschriftenstruktur ist nicht hierarchisch korrekt (z. B. H2 direkt nach H4)",
                "element": "HEADING"
            })
    return issues

def check_aria_roles(url, soup):
    issues = []
    title = soup.title.string.strip() if soup.title else "Ohne Titel"
    for tag in soup.find_all(attrs={"aria-label": True}):
        if not tag.get_text(strip=True):
            issues.append({
                "type": "aria_label_without_text",
                "url": url,
                "title": title,
                "snippet": str(tag),
                "description": "ARIA-Label vorhanden, aber Element hat keinen sichtbaren Text",
                "element": "ARIA"
            })
    return issues
