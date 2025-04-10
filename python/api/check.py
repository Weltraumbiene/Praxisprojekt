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

        # 1. HTML beschaffen
        if request.url:
            result = launch_browser_with_url(request.url)
            html = result["html"]
        elif request.html:
            html = request.html
        else:
            raise HTTPException(status_code=400, detail="Bitte 'url' oder 'html' angeben.")

        # 2. CSS analysieren (optional)
        if request.css:
            css_issues.extend(check_css_contrast(request.css))
        elif request.url:
            try:
                css_combined = extract_css_from_url(request.url)

                # 🔪 Debug-Ausgabe
                print("💡 Extrahiertes CSS (erste 500 Zeichen):\n")
                print(css_combined[:500])
                print("\n--- ENDE DEBUG CSS ---\n")

                css_issues.extend(check_css_contrast(css_combined))
            except Exception as e:
                css_issues.append(f"Fehler beim CSS-Extrahieren: {str(e)}")

        # 3. AXE-Scan (technische Barrierefreiheit)
        try:
            axe_result = run_axe_scan(html=html, tags=request.filter or [])
        except RuntimeError as axe_error:
            error_msg = str(axe_error).lower()

            if "referenceerror" in error_msg:
                raise HTTPException(status_code=500, detail={
                    "type": "javascript-error",
                    "message": str(axe_error),
                    "note": "Ein eingebettetes Skript auf der Seite enthält fehlerhafte Variablen oder fehlerhaftes JS."
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
                    "note": "Ein Frame oder ein eingebetteter Bereich konnte nicht geprüft werden, da der Zugriff blockiert war (Cross-Origin)."
                })
            else:
                raise HTTPException(status_code=500, detail={
                    "type": "unknown",
                    "message": str(axe_error),
                    "note": "Unbekannter Fehler beim AXE-Scan."
                })

        # 4. Strukturprüfung (semantisch)
        structure = extract_structure_from_html(html)
        structural_issues = validate_structure(structure)

        # 4b. ARIA-Analyse
        aria_issues = check_aria_usage(html)

        # 5. Zusammenfassen
        return {
            "source": source,
            "summary": {
                "axe_errors": len(axe_result.get("violations", [])),
                "structural_issues": len(structural_issues),
                "css_issues": len(css_issues),
                "aria_issues": len(aria_issues),
                "total_errors": len(axe_result.get("violations", [])) + len(css_issues) + len(structural_issues) + len(aria_issues),
                "warnings": len(axe_result.get("incomplete", [])),
            },
            "axe_violations": axe_result.get("violations", []),
            "structural_issues": structural_issues,
            "css_issues": css_issues,
            "aria_issues": aria_issues,
            "incomplete_warnings": axe_result.get("incomplete", []),
        }

    except Exception as e:
        print("==== Fehler bei /check ====")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
