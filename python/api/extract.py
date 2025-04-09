import json
import subprocess
from fastapi import APIRouter, HTTPException
from functions.extractor import extract_elements_from_html
from models import URLRequest

router = APIRouter()

@router.post("/extract-elements")
def extract_elements(request: URLRequest):
    try:
        if not request.url and not request.html:
            raise HTTPException(status_code=400, detail="Entweder 'url' oder 'html' muss angegeben sein.")
        
        filter_elements = request.filter if request.filter else []

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
                
                // Extrahiere Überschriften
                result.headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6'))
                                         .map(h => h.innerText);
                
                // Extrahiere Bilder
                result.images = Array.from(document.querySelectorAll('img')).map(img => img.src);

                return result;
            }}, {json.dumps(filter_elements)});

            console.log(JSON.stringify(data));
            await browser.close();
        }})();
        """

        # Rufe Puppeteer über Node.js auf
        result = subprocess.run(["node", "-e", html_input], capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail="Fehler beim Extrahieren: " + result.stderr)
        
        # Ergebnisse von Puppeteer zurückgeben
        return json.loads(result.stdout)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
