from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import subprocess

app = FastAPI()

# Request Wahlmöglichkeiten
class URLRequest(BaseModel):
    url: str | None = None      # Für Online-Check
    html: str | None = None     # Für Offline-Check
    css: str | None = None      # Optionales CSS
    filter: list[str] | None = None  # Filter für bestimmte HTML-Elemente


# Funktionen in Axe-Check
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


# Funktion für HTML-Elemente Extraktion
def extract_html_elements(html: str) -> dict:
    escaped_html = html.replace("\\", "\\\\").replace("`", "\\`")

    script = f"""
    const puppeteer = require('puppeteer');

    (async () => {{
        const browser = await puppeteer.launch();
        const page = await browser.newPage();
        await page.setContent(`{escaped_html}`);

        const data = await page.evaluate(() => {{
            return {{
                title: document.title,
                lang: document.documentElement.lang || null,
                headings: Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6')).map(h => {{
                    return {{ tag: h.tagName, text: h.innerText.trim() }};
                }}),
                images: Array.from(document.querySelectorAll('img')).map(img => img.getAttribute('alt')),
                aria: Array.from(document.querySelectorAll('[aria-label], [aria-describedby], [aria-hidden]')).map(el => {{
                    return {{
                        tag: el.tagName,
                        attributes: {{
                            'aria-label': el.getAttribute('aria-label'),
                            'aria-describedby': el.getAttribute('aria-describedby'),
                            'aria-hidden': el.getAttribute('aria-hidden'),
                        }}
                    }};
                }}),
                labels: Array.from(document.querySelectorAll('label')).map(l => l.innerText.trim()),
                links: Array.from(document.querySelectorAll('a')).map(a => a.innerText.trim()),
                tables: Array.from(document.querySelectorAll('table')).map(table => {{
                    return {{
                        rows: table.rows.length,
                        cols: table.rows[0] ? table.rows[0].cells.length : 0
                    }};
                }}),
                iframes: Array.from(document.querySelectorAll('iframe')).map(f => {{
                    return {{
                        title: f.getAttribute('title'),
                        src: f.getAttribute('src')
                    }};
                }}),
                html_structure: Array.from(document.body.children).map(el => el.tagName)
            }};
        }});

        console.log(JSON.stringify(data));
        await browser.close();
    }})();
    """

    result = subprocess.run(["node", "-e", script], capture_output=True, text=True, encoding='utf-8')

    if result.returncode != 0:
        raise RuntimeError(result.stderr)

    return json.loads(result.stdout)


# Endpunkt

@app.get("/")
def read_root():
    return {"message": "Barrierefreiheits-Checker API läuft!"}


# Endpunkte Funktionen

@app.post("/check")
def check_accessibility(request: URLRequest):
    try:
        # URL CHECK
        if request.url:
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
            
            # Prüfe, ob der Fehlercode auf eine ungültige HTML-Datei hinweist
            if result.returncode != 0:
                if "ERR" in result.stderr:  # Überprüfen, ob der Fehler auf die HTML-Datei hinweist
                    raise HTTPException(status_code=400, detail="Die HTML Datei ist fehlerhaft. Bitte überprüfen Sie den Quellcode.")
                else:
                    raise HTTPException(status_code=500, detail="Fehler beim Laden der URL.")

            data = json.loads(result.stdout)

        # HTML/CSS CHECK
        elif request.html:
            html_content = request.html
            if request.css:
                html_content = f"<style>{request.css}</style>" + html_content

            data = run_axe_on_html(html_content)

        else:
            raise HTTPException(status_code=400, detail="Entweder 'url' oder 'html' muss angegeben sein.")

        # Ausgabe der Ergebnisse
        return {
            "source": request.url or "local",
            "status": "checked",
            "errors": len(data.get("violations", [])),
            "warnings": len(data.get("incomplete", [])),
            "suggestions": [issue["description"] for issue in data.get("violations", [])]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Neuer Endpunkt zur Extraktion von HTML-Daten
@app.post("/extract-elements")
def extract_elements(request: URLRequest):
    try:
        if not request.url and not request.html:
            raise HTTPException(status_code=400, detail="Entweder 'url' oder 'html' muss angegeben sein.")

        html_input = f"""
        const puppeteer = require('puppeteer');

        (async () => {{
            const browser = await puppeteer.launch();
            const page = await browser.newPage();
            {"await page.goto('" + request.url + "');" if request.url else f"await page.setContent(`{request.html.replace('`', '\\`')}`);"}

            const data = await page.evaluate(() => {{
                return {{
                    title: document.title,
                    lang: document.documentElement.lang || null,
                    headings: Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6')).map(h => {{
                        return {{ tag: h.tagName, text: h.innerText.trim() }};
                    }}),
                    images: Array.from(document.querySelectorAll('img')).map(img => img.getAttribute('alt')),
                    aria: Array.from(document.querySelectorAll('[aria-label], [aria-describedby], [aria-hidden]')).map(el => {{
                        return {{
                            tag: el.tagName,
                            attributes: {{
                                'aria-label': el.getAttribute('aria-label'),
                                'aria-describedby': el.getAttribute('aria-describedby'),
                                'aria-hidden': el.getAttribute('aria-hidden'),
                            }}
                        }};
                    }}),
                    labels: Array.from(document.querySelectorAll('label')).map(l => l.innerText.trim()),
                    links: Array.from(document.querySelectorAll('a')).map(a => a.innerText.trim()),
                    tables: Array.from(document.querySelectorAll('table')).map(table => {{
                        return {{
                            rows: table.rows.length,
                            cols: table.rows[0] ? table.rows[0].cells.length : 0
                        }};
                    }}),
                    iframes: Array.from(document.querySelectorAll('iframe')).map(f => {{
                        return {{
                            title: f.getAttribute('title'),
                            src: f.getAttribute('src')
                        }};
                    }}),
                    html_structure: Array.from(document.body.children).map(el => el.tagName)
                }};
            }});

            console.log(JSON.stringify(data));
            await browser.close();
        }})();
        """

        result = subprocess.run(["node", "-e", html_input], capture_output=True, text=True, encoding='utf-8')
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail="Fehler beim Extrahieren")

        return json.loads(result.stdout)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
