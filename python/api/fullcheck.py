# api/fullcheck.py

from fastapi import APIRouter, HTTPException
from models import URLRequest
from core.crawler import crawl_website as crawl_site
from api.check import check_all
from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback
import logging
from datetime import datetime
import os

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
                result = check_all(URLRequest(url=url, filter=request.filter))
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
