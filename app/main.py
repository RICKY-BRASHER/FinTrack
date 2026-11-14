from fastapi import FastAPI
app = FastAPI(
    title="FinTrack API",
    description="API de gestion de budget personnel et détection d'anomalies",
    version="0.1.0"
)
@app.get("/")
def lire_racine() -> dict[str, str]:
    return {
        "statut": "en ligne",
        "message": "Bienvenue sur FinTrack API"
    }
