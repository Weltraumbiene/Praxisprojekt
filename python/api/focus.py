# api/focus.py

from fastapi import APIRouter, HTTPException
from models import URLRequest
from core.focus_tracker import track_focus_order

router = APIRouter()

@router.post("/focus-order")
def focus_order_endpoint(request: URLRequest):
    try:
        if not request.url:
            raise HTTPException(status_code=400, detail="'url' muss angegeben werden.")

        order = track_focus_order(request.url)

        return {
            "url": request.url,
            "focus_order": order,
            "count": len(order)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
