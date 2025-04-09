from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def setup_middleware(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Lass Anfragen von allen Ursprüngen zu (oder beschränke es auf deine Domains)
        allow_credentials=True,
        allow_methods=["*"],  # Erlaube alle HTTP-Methoden
        allow_headers=["*"],  # Erlaube alle Header
    )