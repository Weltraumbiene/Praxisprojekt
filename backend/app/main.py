#\backend\app\main.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import traceback

from .utils import generate_csv, generate_html, save_latest_scan
from .logs import log_message, get_log_buffer
from .scan_controller import start_background_scan, is_scan_running, get_scan_result

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScanRequest(BaseModel):
    url: str
    exclude: Optional[List[str]] = []
    full: Optional[bool] = False
    max_depth: Optional[int] = 3

@app.post("/scan/start")
async def scan_start(scan_request: ScanRequest):
    if is_scan_running():
        raise HTTPException(status_code=409, detail="Ein Scan ist bereits aktiv.")
    try:
        start_background_scan(scan_request.url, scan_request.exclude, scan_request.full, scan_request.max_depth)
        return {"status": "Scan gestartet"}
    except Exception:
        log_message("[❌ Fehler beim Start des Hintergrund-Scans]")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Scan konnte nicht gestartet werden.")

@app.get("/scan/status")
async def scan_status():
    return {"running": is_scan_running()}

@app.get("/scan/result")
async def scan_result():
    result = get_scan_result()
    if result is None:
        raise HTTPException(status_code=404, detail="Noch kein Scan abgeschlossen.")
    return {"issues": result}

@app.get("/download-csv")
async def download_csv():
    try:
        log_message("[💾 CSV-Export] Generiere Datei...")
        return generate_csv()
    except Exception:
        log_message("[❌ CSV-Fehler]")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="CSV-Export fehlgeschlagen.")

@app.get("/download-html")
async def download_html():
    try:
        log_message("[💾 HTML-Export] Generiere Datei...")
        return generate_html()
    except Exception:
        log_message("[❌ HTML-Fehler]")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="HTML-Export fehlgeschlagen.")

@app.get("/log-buffer")
async def get_logs():
    return JSONResponse(content={"logs": get_log_buffer()})
