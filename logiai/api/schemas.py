from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Livraison(BaseModel):
    model_config = ConfigDict(extra="forbid")

    distance_km: float = Field(ge=1, le=1000, description="Distance du trajet (km)")
    poids_kg: float = Field(ge=1, le=3000, description="Poids transporté (kg)")
    heure_depart: int = Field(ge=0, le=23, description="Heure de départ, de 0 à 23")
    pluie_mm: float = Field(ge=0.0, le=60.0, description="Pluie prévue sur le trajet (mm)")
    trafic_index: float = Field(ge=0.0, le=10.0, description="Indice de trafic (0=fluide, 10=saturé)")
    nb_arrets: int = Field(ge=0, description="Nombre d'arrêts de livraison")
    type_vehicule: Literal["moto", "fourgon", "camion"] = Field(description="Type de véhicule")

class PredictionOut(BaseModel):
    probabilite_retard: float
    alerte: bool
    seuil: float
    model_version: str