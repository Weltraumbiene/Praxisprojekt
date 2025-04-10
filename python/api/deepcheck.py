# api/deepcheck.py

from fastapi import APIRouter, HTTPException
from core.iframe_scanner import scan_iframes_separately
from models import URLRequest

router = APIRouter()

@router.post("/deep-check")
def deep_check(request: URLRequest):
    if not request.url:
        raise HTTPException(status_code=400, detail="Bitte eine gültige 'url' angeben.")

    try:
        result = scan_iframes_separately(request.url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
