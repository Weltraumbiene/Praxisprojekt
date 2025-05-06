from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .crawler import crawl_website
from .checker import check_contrast, check_image_alt, check_links
from .utils import generate_csv, generate_html

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # oder ["*"] für alle Domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScanRequest(BaseModel):
    url: str

@app.post("/scan")
async def scan_website(scan_request: ScanRequest):
    try:
        results = crawl_website(scan_request.url)
        issues = []
        
        for page_url in results['pages']:
            issues.extend(check_contrast(page_url))
            issues.extend(check_image_alt(page_url))
            issues.extend(check_links(page_url))
        
        return {"issues": issues}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download-csv")
async def download_csv():
    try:
        return generate_csv()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download-html")
async def download_html():
    try:
        return generate_html()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
