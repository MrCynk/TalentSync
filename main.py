from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import cv, cover_letter, opportunities, apply, status

app = FastAPI(
    title="DevAfricaArena — AI Microservice",
    description="Microservice IA : génération CV, lettre de motivation, matching et candidature automatique.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restreindre à l'URL Laravel en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cv.router,            prefix="/generate-cv",           tags=["CV"])
app.include_router(cover_letter.router,  prefix="/generate-cover-letter", tags=["Lettre de motivation"])
app.include_router(opportunities.router, prefix="/match-opportunities",   tags=["Matching"])
app.include_router(apply.router,         prefix="/auto-apply",            tags=["Candidature auto"])
app.include_router(status.router,        prefix="/application-status",    tags=["Statut"])

@app.get("/health")
def health():
    return {"status": "ok", "service": "DevAfrica Arena AI"}
