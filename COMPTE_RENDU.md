# Compte rendu : TP API LogiAI

**Nom :** ILYAS KHARROUBI
**Groupe :** EMSI 2026-2027

---

## 1. Environnement et premiers tests

**Sortie de `python -m pytest` au départ :**

```
collected 13 items
tests\test_api.py FF................FFF [100%]
================ 5 failed, 8 passed in 0.45s ================
```

**Pourquoi certains tests qui attendent un 422 passent-ils déjà, alors que rien n'est écrit ?**

Au départ, le schéma Pydantic initial était quasi vide et rejetait systématiquement tous les champs non reconnus. Les tests de validation négatifs recevaient donc un code 422 Unprocessable Entity par défaut, pour de « mauvaises raisons ». C'était un faux vert : les tests passaient non pas parce que la logique de validation était correcte, mais parce que le schéma incomplet bloquait l'ensemble des requêtes.

---

## 2. Mon schéma

| Champ | Min | Max | Justification physique |
|---|---|---|---|
| `distance_km` | 0.1 | 1000 | Trajet de livraison local ou inter-villes réaliste, supérieur à 0 km |
| `poids_kg` | 0 | 10000 | Poids de la marchandise, du colis léger au camion lourd |
| `heure_depart` | 0 | 23 | Les 24 heures d'une journée |
| `pluie_mm` | 0 | 100 | Précipitations en mm/h (0 = temps sec, 100 = tempête extrême) |
| `trafic_index` | 0 | 10 | Indice normalisé de densité de circulation (0 = fluide, 10 = totalement saturé) |
| `nb_arrets` | 0 | 50 | Nombre d'étapes de déchargement prévues au cours d'une tournée |
| `type_vehicule` | - | - | `Literal["moto", "fourgon", "camion"]` pour restreindre strictement aux types de la flotte |

---

## 3. Ma fonction `predict()`

```python
@app.post("/v1/predict", response_model=PredictionOut)
def predict(livraison: Livraison):
    predictor = state.get("predictor")
    if predictor is None:
        raise HTTPException(
            status_code=503,
            detail="Le modèle de prédiction est indisponible. Veuillez vérifier le fichier du modèle."
        )
    resultat = predictor.predict(livraison.model_dump())
    return PredictionOut(**resultat)
```

---

## 4. Quatre requêtes

| Requête | Code obtenu | Explication |
|---|---|---|
| Livraison normale | **200 OK** | Données conformes au schéma Pydantic, la prédiction est renvoyée par le modèle |
| `distance_km = -5` | **422 Unprocessable Entity** | Rejeté par la contrainte de validation Pydantic `gt=0` ou `ge=0.1` |
| `type_vehicule = "avion"` | **422 Unprocessable Entity** | Rejeté car « avion » n'appartient pas à `Literal["moto", "fourgon", "camion"]` |
| Modèle absent (dossier `models/` supprimé) | **503 Service Unavailable** | L'API est active mais `state.get("predictor")` renvoie `None`, ce qui lève une exception 503 |

---

## 5. Questions de compréhension

**Pourquoi charge-t-on le modèle au démarrage et pas à chaque requête ?**

Charger le modèle `.joblib` implique des entrées/sorties disque et une désérialisation coûteuses en temps. Le charger une fois au démarrage (événement `lifespan`) le conserve en mémoire RAM pour des réponses instantanées.

**Qui écrit le contrôle « pluie <= 100 », et où est-il écrit ?**

Ce contrôle est rédigé par le développeur dans le fichier `logiai/api/schemas.py`, sous forme de contrainte Pydantic au sein de la classe `Livraison`.

**Différence entre 422 et 503 ?**

Le 422 est une erreur client (données invalides ou hors bornes). Le 503 est une erreur serveur (service en ligne mais ressource interne, ici le modèle, indisponible).

**Pourquoi une route `/v1/predict` plutôt que `/predict` ?**

Le préfixe `/v1` instaure le versionnement de l'API, pour permettre des évolutions futures sans casser les applications clientes existantes.

**Que se passerait-il si la distance était déclarée `int` ?**

Une valeur décimale envoyée par un client (ex : 12.5 km) serait rejetée ou tronquée, ce qui réduirait la précision des données fournies au modèle.

---

## 6. Décision : modèle absent

**Choix retenu :** Option A (démarrer et répondre 503 aux demandes de prédiction)

**Justification :** L'option B (refuser de démarrer) fait crasher entièrement le conteneur, ce qui bloque même les diagnostics sur `/health`. L'option A maintient le serveur accessible pour superviser son état, tout en informant clairement les clients de l'indisponibilité du modèle via un code 503 explicite.

---

## 7. Lien de la pull request

- **Pull Request GitHub :** https://github.com/ilyaskh08/AYMAN_ZERHOUN_ILYAS_KHARROUBI/pull/1
- **Dépôt GitHub (branche `tp-api`) :** https://github.com/ilyaskh08/AYMAN_ZERHOUN_ILYAS_KHARROUBI
