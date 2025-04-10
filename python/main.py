# C:\Users\bfranneck\Desktop\Praxisprojekt\Anwendung\python\main.py

from fastapi import FastAPI
from api.check import router as check_router
from api.extract import router as extract_router
from api.deepcheck import router as deepcheck_router  # 👈 hinzugefügt
from middleware import setup_middleware

app = FastAPI()

# Setup Middleware
setup_middleware(app)

# Include the API Routers
app.include_router(check_router)
app.include_router(extract_router)
app.include_router(deepcheck_router)  # 👈 hinzugefügt

@app.get("/")
def read_root():
    return {"message": "Barrierefreiheits-Checker API läuft!"}
