import subprocess
import json
import requests
import tinycss2
import re
from bs4 import BeautifulSoup

# ---------------------
# HTML Extraktor
# ---------------------
def extract_elements_from_html(html: str) -> dict:
    """
    Extrahiert bestimmte Elemente (z. B. alle Links und Bilder) aus einem HTML-Dokument.
    
    :param html: HTML-String
    :return: Ein Dictionary mit den extrahierten Elementen
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extrahiert alle Links (Anker-Tags)
    links = [a['href'] for a in soup.find_all('a', href=True)]
    
    # Extrahiert alle Bild-URLs (img-Tags)
    images = [img['src'] for img in soup.find_all('img', src=True)]
    
    # Hier könnten auch andere Elemente extrahiert werden
    # Zum Beispiel: Tabellen, Formulare, Überschriften, etc.
    
    return {
        "links": links,
        "images": images
    }

# ---------------------
# Kontrastberechnung
# ---------------------
def hex_to_rgb(hex_color):
    hex_color = hex_color.strip().lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join([c*2 for c in hex_color])
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def parse_color(value: str):
    value = value.strip().lower()
    if value.startswith("#"):
        return hex_to_rgb(value)

    rgb_match = re.match(r"rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*[\d.]+)?\)", value)
    if rgb_match:
        return tuple(int(rgb_match.group(i)) for i in range(1, 4))

    raise ValueError(f"Unbekanntes Farbformat: {value}")


def relative_luminance(rgb):
    def to_linear(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = rgb
    return 0.2126 * to_linear(r) + 0.7152 * to_linear(g) + 0.0722 * to_linear(b)


def contrast_ratio(rgb1, rgb2):
    lum1 = relative_luminance(rgb1)
    lum2 = relative_luminance(rgb2)
    L1, L2 = max(lum1, lum2), min(lum1, lum2)
    return (L1 + 0.05) / (L2 + 0.05)


def check_css_contrast(css: str) -> list[str]:
    errors = []

    rules = tinycss2.parse_stylesheet(css, skip_whitespace=True)
    for rule in rules:
        if rule.type != 'qualified-rule':
            continue

        declarations = tinycss2.parse_declaration_list(rule.content)
        color = None
        background_color = None

        for decl in declarations:
            if decl.type != 'declaration':
                continue
            name = decl.name.lower()
            value = "".join([token.serialize() for token in decl.value]).strip()

            if name == "color":
                color = value
            elif name == "background-color":
                background_color = value

        if color and background_color:
            try:
                rgb_text = parse_color(color)
                rgb_bg = parse_color(background_color)
                ratio = contrast_ratio(rgb_text, rgb_bg)

                if ratio < 4.5:
                    errors.append(
                        f"Niedriger Kontrast ({ratio:.2f}:1) zwischen Textfarbe {color} und Hintergrundfarbe {background_color}"
                    )
            except Exception as e:
                errors.append(f"Fehler bei Farben {color} / {background_color}: {str(e)}")

    return errors


# ---------------------
# Puppeteer-Aktionen
# ---------------------
def run_axe_on_html(html: str) -> dict:
    if "<html" not in html.lower():
        html = f"""
        <!DOCTYPE html>
        <html lang="de">
        <head><meta charset="UTF-8"><title>Fragment Test</title></head>
        <body>
        {html}
        </body>
        </html>
        """

    escaped_html = html.replace("\\", "\\\\").replace("`", "\\`")

    script = f"""
    const puppeteer = require('puppeteer');
    const axeCore = require('axe-core');

    (async () => {{
        const browser = await puppeteer.launch();
        const page = await browser.newPage();
        await page.setContent(`{escaped_html}`);

        await page.addScriptTag({{ url: 'https://cdn.jsdelivr.net/npm/axe-core@4.3.0/axe.min.js' }});

        const results = await page.evaluate(async () => {{
            const results = await axe.run();
            return results;
        }});

        console.log(JSON.stringify(results));
        await browser.close();
    }})();
    """

    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, encoding='utf-8')

    if result.returncode != 0:
        raise RuntimeError(result.stderr)

    return json.loads(result.stdout)


def extract_css_from_url(url: str) -> list:
    script = f"""
    const puppeteer = require('puppeteer');

    (async () => {{
        const browser = await puppeteer.launch();
        const page = await browser.newPage();
        await page.goto('{url}');

        const cssLinks = await page.evaluate(() => {{
            return Array.from(document.querySelectorAll('link[rel="stylesheet"], style')).map(link => {{
                return link.href || link.innerHTML;
            }});
        }});

        console.log(JSON.stringify(cssLinks));
        await browser.close();
    }})();
    """

    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, encoding='utf-8')

    if result.returncode != 0:
        raise RuntimeError(f"Fehler beim Extrahieren der CSS-Dateien: {result.stderr}")

    return json.loads(result.stdout)
