from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import subprocess

app = FastAPI()

class URLRequest(BaseModel):
    url: str

@app.get("/")
def read_root():
    return {"message": "Barrierefreiheits-Checker API läuft!"}

@app.post("/check")
def check_accessibility(request: URLRequest):
    try:
        # Axe-Core mit Puppeteer starten (Headless Chrome)
        script = f"""
        const puppeteer = require('puppeteer');
        const axeCore = require('axe-core');

        (async () => {{
            const browser = await puppeteer.launch();
            const page = await browser.newPage();
            await page.goto('{request.url}');

            // Axe-Core ausführen im Browser-Kontext
            await page.addScriptTag({{ url: 'https://cdn.jsdelivr.net/npm/axe-core@4.3.0/axe.min.js' }});
            
            const results = await page.evaluate(async () => {{
                // Axe-Core im Browser-Kontext ausführen
                const results = await axe.run();
                return results;
            }});

            console.log(JSON.stringify(results));
            await browser.close();
        }})();
        """

        result = subprocess.run(["node", "-e", script], capture_output=True, text=True, encoding='utf-8')

        if result.returncode != 0:
            raise HTTPException(status_code=500, detail="Fehler bei der Barrierefreiheitsprüfung")

        data = json.loads(result.stdout)

        return {
            "url": request.url,
            "status": "checked",
            "errors": len(data.get("violations", [])),
            "warnings": len(data.get("incomplete", [])),
            "suggestions": [issue["description"] for issue in data.get("violations", [])]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
