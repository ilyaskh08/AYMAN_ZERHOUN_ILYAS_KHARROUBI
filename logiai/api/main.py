"""L'API LogiAI : python -m uvicorn logiai.api.main:app --reload"""
from contextlib import asynccontextmanager

from logiai.api import schemas
from fastapi import FastAPI, HTTPException

from logiai.config import MODEL_PATH
from logiai.predict import Predictor

state: dict = {}  # contient le "predictor" une fois le modèle chargé


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Exécuté UNE fois, au démarrage du serveur (pas à chaque requête)
    if MODEL_PATH.exists():
        state["predictor"] = Predictor(MODEL_PATH)
    yield
    state.clear()


app = FastAPI(
    title="LogiAI",
    version="1.0.0",
    description="Prédit le risque de retard d'une livraison à partir de ses caractéristiques.",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": "predictor" in state}


@app.post("/v1/predict", response_model=schemas.PredictionOut)
def predict(livraison: schemas.Livraison):
    # 1. Récupérer le prédicteur dans l'état de l'application
    predictor = state.get("predictor")

    # 2. Si le modèle n'est pas chargé, renvoyer une erreur 503
    if predictor is None:
        raise HTTPException(
            status_code=503,
            detail="Modèle non chargé. Veuillez entraîner le modèle avec python -m logiai.train"
        )

    # 3. Effectuer la prédiction et renvoyer le résultat typé
    result = predictor.predict(livraison.model_dump())
    return schemas.PredictionOut(**result)