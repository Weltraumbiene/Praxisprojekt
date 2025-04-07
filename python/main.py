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


# Funktionen in Axe-Check
def run_axe_on_html(html: str) -> dict:
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
            if result.returncode != 0:
                raise HTTPException(status_code=500, detail="Fehler beim Laden der URL")

            data = json.loads(result.stdout)

        # HTML/CSS CHECK
        elif request.html:
            html_content = request.html
            if request.css:
                html_content = f"<style>{request.css}</style>" + html_content

            data = run_axe_on_html(html_content)

        else:
            raise HTTPException(status_code=400, detail="Entweder 'url' oder 'html' muss angegeben sein.")

        #Ausgabe der Ergebnisse
        return {
            "source": request.url or "local",
            "status": "checked",
            "errors": len(data.get("violations", [])),
            "warnings": len(data.get("incomplete", [])),
            "suggestions": [issue["description"] for issue in data.get("violations", [])]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
