from fastapi import APIRouter, HTTPException
from functions.extractor import extract_css_from_url, run_axe_on_html, check_css_contrast
from models import URLRequest
import requests
import json
import subprocess

router = APIRouter()

@router.post("/check")
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