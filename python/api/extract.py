# api/extract.py

from fastapi import APIRouter, HTTPException
from core.browser import launch_browser_with_url
from core.html_parser import extract_structure_from_html
from core.validator import validate_structure
from models import URLRequest

router = APIRouter()

@router.post("/extract-elements")
def extract_elements(request: URLRequest):
    try:
        html = ""

        # 1. HTML beschaffen
        if request.html:
            html = request.html
        elif request.url:
            # Startet echten Browser mit Zielseite
            result = launch_browser_with_url(request.url)
            html = result["html"]
        else:
            raise HTTPException(status_code=400, detail="Entweder 'url' oder 'html' muss angegeben sein.")

        # 2. Struktur extrahieren
        structure = extract_structure_from_html(html)

        # 3. Validierung durchführen
        validation_issues = validate_structure(structure)

        # 4. Alles als API-Response zurückgeben
        return {
            "status": "ok",
            "structure": structure,
            "issues": validation_issues
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
