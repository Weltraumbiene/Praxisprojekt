# api/fullcheck.py

from fastapi import APIRouter, HTTPException
from models import URLRequest
from core.crawler import crawl_website as crawl_site  # 🔧 Umbenennung hier
from api.check import check_all
import traceback

router = APIRouter()

@router.post("/full-check")
def full_accessibility_check(request: URLRequest):
    try:
        if not request.url:
            raise HTTPException(status_code=400, detail="'url' muss angegeben werden.")

        visited = set()
        queue = [request.url]
        results = []

        while queue and len(visited) < 25:  # Begrenzung für Performance
            current_url = queue.pop(0)
            if current_url in visited:
                continue

            print(f"🔎 Scanning {current_url}")
            visited.add(current_url)
            try:
                check_result = check_all(URLRequest(url=current_url, filter=request.filter))
                results.append({"url": current_url, "result": check_result})
            except Exception as e:
                results.append({"url": current_url, "error": str(e)})

            # Neue Links für weitere Prüfung sammeln
            try:
                new_links = crawl_site(current_url)
                for link in new_links:
                    if link not in visited and link not in queue:
                        queue.append(link)
            except Exception as crawl_error:
                print(f"⚠️ Fehler beim Crawlen von {current_url}: {crawl_error}")

        return {
            "start_url": request.url,
            "pages_tested": len(visited),
            "results": results
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
