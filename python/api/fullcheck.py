from fastapi import APIRouter, HTTPException
from models import URLRequest
from core.crawler import crawl_website as crawl_site
from api.check import check_all
from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback
import logging
from datetime import datetime
import os
import hashlib

# Setup Logging
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "fullcheck.log")

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

router = APIRouter()

# Globaler CSS-Cache (für Wiederverwendung)
css_cache = {}

def hash_content(content: str) -> str:
    return hashlib.md5(content.encode("utf-8")).hexdigest()

@router.post("/full-check")
def full_accessibility_check(request: URLRequest):
    try:
        if not request.url:
            raise HTTPException(status_code=400, detail="'url' muss angegeben werden.")

        logging.info(f"🌐 Starte Crawl für {request.url}")
        all_links = crawl_site(request.url, max_pages=25, max_depth=2)
        logging.info(f"🔗 {len(all_links)} Seiten gefunden beim Crawl.")

        results = []

        def scan_page(url: str):
            try:
                logging.info(f"🔍 Scanne {url}")
                req_obj = URLRequest(url=url, filter=request.filter)
                result = check_all(req_obj)

                # Deduplizierung der CSS-Fehler über Seiten hinweg
                css_raw = result.get("css_raw")
                if css_raw:
                    css_hash = hash_content(css_raw)
                    if css_hash in css_cache:
                        result["css_issues"] = css_cache[css_hash]
                        logging.info(f"♻️ Wiederverwendete CSS-Analyse für {url}")
                    else:
                        css_cache[css_hash] = result.get("css_issues", [])
                        logging.info(f"💾 Neue CSS-Analyse gespeichert für {url}")

                logging.info(f"✅ Scan erfolgreich für {url}")
                return {"url": url, "result": result}

            except Exception as e:
                logging.warning(f"❌ Fehler beim Scan von {url}: {e}")
                return {"url": url, "error": str(e)}

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(scan_page, url) for url in all_links]
            for future in as_completed(futures):
                results.append(future.result())

        logging.info(f"📝 Scan abgeschlossen für {request.url} – {len(results)} Seiten verarbeitet")

        return {
            "start_url": request.url,
            "pages_tested": len(results),
            "results": results
        }

    except Exception as e:
        logging.error("💥 Unerwarteter Fehler im Fullcheck: " + traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
