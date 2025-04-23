from fastapi import APIRouter, HTTPException
from core.browser import launch_browser_with_url, extract_css_from_url
from core.axe import run_axe_scan
from core.css_checker import check_css_contrast
from core.html_parser import extract_structure_from_html
from core.validator import validate_structure
from core.aria_checker import check_aria_usage
from models import URLRequest
import traceback

router = APIRouter()

@router.post("/check")
def check_all(request: URLRequest):
    try:
        html = ""
        source = request.url or "HTML-Input"
        css_issues = []
        css_raw = ""

        # 1. HTML laden
        if request.url:
            result = launch_browser_with_url(request.url)
            html = result["html"]
        elif request.html:
            html = request.html
        else:
            raise HTTPException(status_code=400, detail="Bitte 'url' oder 'html' angeben.")

        # 2. CSS extrahieren oder verwenden
        if request.css:
            css_raw = request.css
            css_issues.extend(check_css_contrast(css_raw))
        elif request.url:
            try:
                css_raw = extract_css_from_url(request.url)
                css_issues.extend(check_css_contrast(css_raw))
            except Exception as e:
                css_issues.append({
                    "message": f"Fehler beim CSS-Extrahieren: {str(e)}",
                    "selector": "",
                    "snippet": ""
                })

        # 3. AXE prüfen
        try:
            axe_result = run_axe_scan(html=html, tags=request.filter or [])
        except RuntimeError as axe_error:
            error_msg = str(axe_error).lower()

            if "referenceerror" in error_msg:
                raise HTTPException(status_code=500, detail={
                    "type": "javascript-error",
                    "message": str(axe_error),
                    "note": "Ein eingebettetes Skript enthält Fehler."
                })
            elif "timeout" in error_msg:
                raise HTTPException(status_code=500, detail={
                    "type": "timeout",
                    "message": str(axe_error),
                    "note": "Das Laden oder Analysieren der Seite hat zu lange gedauert."
                })
            elif "securityerror" in error_msg or "cross-origin" in error_msg:
                raise HTTPException(status_code=500, detail={
                    "type": "cross-origin",
                    "message": str(axe_error),
                    "note": "Ein Frame konnte nicht geprüft werden (Cross-Origin)."
                })
            else:
                raise HTTPException(status_code=500, detail={
                    "type": "unknown",
                    "message": str(axe_error),
                    "note": "Unbekannter Fehler beim AXE-Scan."
                })

        # 4. Semantik & ARIA prüfen
        structure = extract_structure_from_html(html)
        structural_issues = validate_structure(structure)
        aria_issues = check_aria_usage(html)

        # 5. Rückgabe
        return {
            "source": source,
            "css_raw": css_raw,  # wird von fullcheck.py verwendet zum Hashen
            "summary": {
                "axe_errors": len(axe_result.get("violations", [])),
                "structural_issues": len(structural_issues),
                "css_issues": len(css_issues),
                "aria_issues": len(aria_issues),
                "total_errors": len(axe_result.get("violations", [])) + len(css_issues) + len(structural_issues) + len(aria_issues),
                "warnings": len(axe_result.get("incomplete", [])),
            },
            "axe_violations": [
                {
                    "id": v.get("id"),
                    "impact": v.get("impact"),
                    "description": v.get("description"),
                    "help": v.get("help"),
                    "help_url": v.get("helpUrl"),
                    "nodes": [
                        {
                            "target": node.get("target", []),
                            "html": node.get("html", "").strip(),
                            "failure_summary": node.get("failureSummary", "").strip()
                        }
                        for node in v.get("nodes", [])
                    ]
                }
                for v in axe_result.get("violations", [])
            ],
            "incomplete_warnings": [
                {
                    "id": w.get("id"),
                    "impact": w.get("impact"),
                    "description": w.get("description"),
                    "help": w.get("help"),
                    "help_url": w.get("helpUrl"),
                    "nodes": [
                        {
                            "target": node.get("target", []),
                            "html": node.get("html", "").strip(),
                            "failure_summary": node.get("failureSummary", "").strip()
                        }
                        for node in w.get("nodes", [])
                    ]
                }
                for w in axe_result.get("incomplete", [])
            ],
            "structural_issues": structural_issues,
            "css_issues": css_issues,
            "aria_issues": aria_issues,
        }

    except Exception as e:
        print("==== Fehler bei /check ====")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
