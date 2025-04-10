# C:\Users\bfranneck\Desktop\Praxisprojekt\Anwendung\python\main.py

from fastapi import FastAPI
from api.check import router as check_router
from api.extract import router as extract_router
from api.deepcheck import router as deepcheck_router
from middleware import setup_middleware
from api.fullcheck import router as fullcheck_router
from api.focus import router as focus_router

app = FastAPI()

# Setup Middleware
setup_middleware(app)

# Include the API Routers
app.include_router(check_router)
app.include_router(extract_router)
app.include_router(deepcheck_router)
app.include_router(fullcheck_router)
app.include_router(focus_router)

@app.get("/")
def read_root():
    return {"message": "Barrierefreiheits-Checker API läuft!"}
