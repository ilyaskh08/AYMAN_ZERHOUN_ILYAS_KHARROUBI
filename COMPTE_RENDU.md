# Compte rendu : TP API LogiAI

**Noms :** KHARROUBI  **Groupe :** ........

## 1. Environnement et premiers tests
- Sortie observée de `python -m pytest` : 13 tests exécutés, 11 réussis et 2 échoués.
  Les deux échecs concernaient les champs manquants dans `PredictionOut`
  (`seuil` et `model_version`) et l'acceptation d'un champ inconnu (`couleur`).
- Certains tests qui attendent un 422 passent déjà parce que FastAPI utilise le
  schéma Pydantic `Livraison` pour valider automatiquement les requêtes. Les
  bornes et les valeurs autorisées sont déclarées dans `schemas.py`.

## 2. Mon schéma
- Bornes actuelles et justification :

| Variable | Min | Max | Pourquoi |
|---|---|---|---|
| distance_km | 1 | 1000 | Distance positive, limitée à une plage réaliste pour le projet. |
| poids_kg | 1 | 3000 | Poids positif, limité à la capacité prévue. |
| heure_depart | 0 | 23 | Une heure de départ doit appartenir à une journée. |
| pluie_mm | 0 | 60 | La pluie ne peut pas être négative ; le schéma fixe une limite à 60 mm. |
| trafic_index | 0 | 10 | L'indice de trafic est défini sur une échelle de 0 à 10. |
| nb_arrets | 0 | non défini | Le nombre d'arrêts ne peut pas être négatif ; aucune borne supérieure n'est déclarée. |

Les valeurs autorisées pour `type_vehicule` sont `moto`, `fourgon` et `camion`.

## 3. Ma fonction predict()

```python
@app.post("/v1/predict", response_model=schemas.PredictionOut)
def predict(livraison: schemas.Livraison):
    predictor = state.get("predictor")

    if predictor is None:
        raise HTTPException(
            status_code=503,
            detail="Modèle non chargé. Veuillez entraîner le modèle avec python -m logiai.train"
        )

    result = predictor.predict(livraison.model_dump())
    return schemas.PredictionOut(**result)
```

## 4. Quatre requêtes
| Requête | Code obtenu | Pourquoi |
|---|---|---|
| livraison normale | 200 | Les données sont valides et le modèle est chargé. |
| distance_km = -5 | 422 | La distance est inférieure au minimum autorisé (1 km). |
| type_vehicule = "avion" | 422 | Cette valeur n'est pas parmi les types de véhicules autorisés. |
| modèle absent | 503 | Le serveur répond, mais ne peut pas prédire sans modèle chargé. |

## 5. Questions de compréhension
1. **Pourquoi charge-t-on le modèle au démarrage et pas à chaque requête ?**
   Pour éviter de relire le fichier du modèle à chaque prédiction, ce qui
   ajouterait du délai. Le modèle reste disponible en mémoire pendant que l'API
   fonctionne.
2. **Qui écrit le contrôle « pluie <= 100 », et où est-il écrit ?**
   Dans l'application actuelle, la limite n'est pas 100 mais **60 mm**. Elle
   est déclarée dans `logiai/api/schemas.py` avec
   `Field(ge=0.0, le=60.0, ...)`. FastAPI applique cette validation Pydantic
   automatiquement.
3. **Différence entre 422 et 503 ?**
   `422` indique que les données reçues ne respectent pas le schéma. `503`
   indique que le service ne peut pas réaliser la prédiction, ici parce que le
   modèle n'est pas chargé.
4. **Pourquoi une route `/v1/predict` plutôt que `/predict` ?**
   `v1` identifie la version de l'API. Une nouvelle version peut ensuite
   modifier le contrat sans imposer immédiatement ces changements aux clients
   de la première version.
5. **Que se passerait-il si la distance était déclarée `int` ?**
   Les distances décimales ne seraient pas représentées comme telles. Le type
   `float` permet par exemple de transmettre une distance de 12,5 km.

## 6. Décision : modèle absent
L'application choisit de démarrer même si le modèle manque, puis de répondre
`503` à une requête de prédiction. Cela permet de garder disponibles les autres
routes, comme `/health`, et d'expliquer que le modèle est indisponible. En
contrepartie, les prédictions ne fonctionnent pas tant que le modèle n'est pas
chargé. Refuser de démarrer empêcherait toute utilisation ou vérification de
l'API, mais rendrait l'absence du modèle visible immédiatement au démarrage.

## 7. Lien de la pull request
À compléter avec le lien de la pull request si elle existe ; sinon, indiquer
« Aucune pull request créée ».
