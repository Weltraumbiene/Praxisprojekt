from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Erlaube CORS für dein Frontend
origins = [
    "http://localhost:5173",  # dein Vite/Frontend Dev-Server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # oder ["*"] für alle – aber das ist unsicher in Prod
    allow_credentials=True,
    allow_methods=["*"],     # GET, POST, usw.
    allow_headers=["*"],
)
