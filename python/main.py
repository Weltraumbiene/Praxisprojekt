from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import json
import requests
import tinycss2
import re

app = FastAPI()


# ---------------------
# Datenmodell
# ---------------------
class URLRequest(BaseModel):
    url: str | None = None
    html: str | None = None
    css: str | None = None
    filter: list[str] | None = None


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


# ---------------------
# API-Endpunkte
# ---------------------

@app.get("/")
def read_root():
    return {"message": "Barrierefreiheits-Checker API läuft!"}


@app.post("/check")
def check_accessibility(request: URLRequest):
    try:
        css_errors = []

        if request.url:
            # CSS prüfen
            css_links = extract_css_from_url(request.url)
            for css_link in css_links:
                if css_link.startswith("http"):
                    css_response = requests.get(css_link)
                    css_errors.extend(check_css_contrast(css_response.text))
                else:
                    css_errors.extend(check_css_contrast(css_link))

            # HTML prüfen
            html_fetch_script = f"""
            const puppeteer = require('puppeteer');
            const axeCore = require('axe-core');

            (async () => {{
                const browser = await puppeteer.launch();
                const page = await browser.newPage();
                await page.goto('{request.url}');

                await page.addScriptTag({{ url: 'https://cdn.jsdelivr.net/npm/axe-core@4.3.0/axe.min.js' }});

                const results = await page.evaluate(async () => {{
                    const results = await axe.run();
                    return results;
                }});

                console.log(JSON.stringify(results));
                await browser.close();
            }})();
            """
            result = subprocess.run(["node", "-e", html_fetch_script], capture_output=True, text=True, encoding='utf-8')

            if result.returncode != 0:
                if "ERR" in result.stderr:
                    raise HTTPException(status_code=400, detail="Die HTML Datei ist fehlerhaft.")
                else:
                    raise HTTPException(status_code=500, detail="Fehler beim Laden der URL.")

            data = json.loads(result.stdout)

        elif request.html:
            html_content = request.html
            if request.css:
                html_content = f"<style>{request.css}</style>" + html_content
                css_errors.extend(check_css_contrast(request.css))

            data = run_axe_on_html(html_content)

        else:
            raise HTTPException(status_code=400, detail="Entweder 'url' oder 'html' muss angegeben sein.")

        return {
            "source": request.url or "local",
            "status": "checked",
            "errors": len(data.get("violations", [])) + len(css_errors),
            "warnings": len(data.get("incomplete", [])),
            "css_issues": css_errors,
            "suggestions": [issue["description"] for issue in data.get("violations", [])] + css_errors
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extract-elements")
def extract_elements(request: URLRequest):
    try:
        if not request.url and not request.html:
            raise HTTPException(status_code=400, detail="Entweder 'url' oder 'html' muss angegeben sein.")
        
        if request.html and "<html" not in request.html.lower():
            request.html = f"<!DOCTYPE html><html lang='de'><head><meta charset='utf-8'></head><body>{request.html}</body></html>"
        
        filter_elements = request.filter if request.filter else []
        filter_str = json.dumps(filter_elements)

        html_input = f"""
        const puppeteer = require('puppeteer');

        (async () => {{
            const browser = await puppeteer.launch();
            const page = await browser.newPage();
            {"await page.goto('" + request.url + "');" if request.url else f"await page.setContent(`{request.html.replace('`', '\\`')}`);"}

            const data = await page.evaluate((filter_elements) => {{
                const result = {{
                    title: document.title,
                    lang: document.documentElement.lang || null,
                    headings: [],
                    images: [],
                    aria: [],
                    labels: [],
                    links: [],
                    tables: [],
                    iframes: [],
                    html_structure: []
                }};
                
                if (!filter_elements || filter_elements.includes('headings')) {{
                    result.headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6')).map(h => {{
                        return {{ tag: h.tagName, text: h.innerText.trim() }};
                    }});
                }}
                
                if (!filter_elements || filter_elements.includes('images')) {{
                    result.images = Array.from(document.querySelectorAll('img')).map(img => img.getAttribute('alt'));
                }}

                if (!filter_elements || filter_elements.includes('aria')) {{
                    result.aria = Array.from(document.querySelectorAll('[aria-label], [aria-describedby], [aria-hidden]')).map(el => {{
                        return {{
                            tag: el.tagName,
                            attributes: {{
                                'aria-label': el.getAttribute('aria-label'),
                                'aria-describedby': el.getAttribute('aria-describedby'),
                                'aria-hidden': el.getAttribute('aria-hidden'),
                            }}
                        }};
                    }});
                }}

                if (!filter_elements || filter_elements.includes('labels')) {{
                    result.labels = Array.from(document.querySelectorAll('label')).map(l => l.innerText.trim());
                }}

                if (!filter_elements || filter_elements.includes('links')) {{
                    result.links = Array.from(document.querySelectorAll('a')).map(a => a.innerText.trim());
                }}

                if (!filter_elements || filter_elements.includes('tables')) {{
                    result.tables = Array.from(document.querySelectorAll('table')).map(table => {{
                        return {{
                            rows: table.rows.length,
                            cols: table.rows[0] ? table.rows[0].cells.length : 0
                        }};
                    }});
                }}

                if (!filter_elements || filter_elements.includes('iframes')) {{
                    result.iframes = Array.from(document.querySelectorAll('iframe')).map(f => {{
                        return {{
                            title: f.getAttribute('title'),
                            src: f.getAttribute('src')
                        }};
                    }});
                }}

                if (!filter_elements || filter_elements.includes('html_structure')) {{
                    result.html_structure = Array.from(document.body.children).map(el => el.tagName);
                }}

                return result;
            }}, {filter_str});

            console.log(JSON.stringify(data));
            await browser.close();
        }})();
        """

        result = subprocess.run(["node", "-e", html_input], capture_output=True, text=True, encoding='utf-8')
        if result.returncode != 0:
            print("Node Fehler:", result.stderr)  # Debug-Ausgabe
            raise HTTPException(status_code=500, detail="Fehler beim Extrahieren: " + result.stderr)
        return json.loads(result.stdout)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
