# core/iframe_scanner.py

from core.browser import launch_browser_with_url
from api.check import check_all
from models import URLRequest
import re
from urllib.parse import urljoin


def extract_iframe_sources(html: str) -> list[str]:
    """
    Findet alle iframe src-Links im HTML (ohne DOM-Abhängigkeit).
    """
    iframe_srcs = re.findall(r'<iframe[^>]+src=["\'](.*?)["\']', html)
    return iframe_srcs

def assess_iframe_relevance(iframe_url: str) -> str:
    """
    Bewertet generisch, ob ein Iframe voraussichtlich barrierefreiheitsrelevant ist.
    """
    irrelevant_domains = ["consent", "cookie", "google.com", "youtube.com", "doubleclick.net"]
    
    for keyword in irrelevant_domains:
        if keyword in iframe_url:
            return "low"

    return "high"


def scan_iframes_separately(parent_url: str) -> dict:
    """
    Lädt eine Seite, extrahiert iframe-srcs und führt für jeden iframe einen eigenen Test aus.
    Gibt ein verschachteltes Ergebnis zurück.
    """
    results = {
        "parent_url": parent_url,
        "iframes": []
    }

    try:
        # Hauptseite laden
        page_data = launch_browser_with_url(parent_url)
        html = page_data.get("html", "")
        iframe_links = extract_iframe_sources(html)

        for iframe_url in iframe_links:
            # relativen Pfad in absolute URL umwandeln
            if iframe_url.startswith("/"):
                iframe_url = urljoin(parent_url, iframe_url)

            relevance = assess_iframe_relevance(iframe_url)

            req = URLRequest(url=iframe_url)
            iframe_result_entry = {
                "url": iframe_url,
                "relevance": relevance
            }

            # Nur relevante Iframes wirklich scannen
            if relevance == "high":
                try:
                    iframe_result = check_all(req)
                    iframe_result_entry["result"] = iframe_result
                except Exception as e:
                    error_msg = str(e).lower()

                    if "timeout" in error_msg or "navigation timeout" in error_msg:
                        error_type = "timeout"
                        note = "Zeitüberschreitung beim Laden des Inhalts."
                    elif "securityerror" in error_msg or "cross-origin" in error_msg:
                        error_type = "cross-origin"
                        note = "Cross-Origin Zugriff nicht erlaubt."
                    elif "referenceerror" in error_msg:
                        error_type = "javascript-error"
                        note = "Ein eingebettetes Skript hat versucht, auf eine nicht definierte Variable zuzugreifen."
                    else:
                        error_type = "unknown"
                        note = "Unbekannter Fehler beim Iframe-Scan."

                    iframe_result_entry["error"] = {
                        "type": error_type,
                        "message": str(e),
                        "note": note
                    }
            else:
                iframe_result_entry["skipped"] = True
                iframe_result_entry["note"] = "Automatisch als wenig relevant eingestuft. Kein Test durchgeführt."

            results["iframes"].append(iframe_result_entry)

    except Exception as e:
        results["error"] = {
            "type": "main-page",
            "message": str(e)
        }

    return results