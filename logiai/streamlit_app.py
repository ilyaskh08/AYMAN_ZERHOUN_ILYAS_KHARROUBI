import streamlit as st
import requests

# Titre de l'application
st.set_page_config(page_title="LogiAl - Prédiction de Retard de Livraison", page_icon="🚚", layout="centered")

st.title("🚚 LogiAl - Prédiction de Retard de Livraison")
st.markdown("Interface interactive connectée à l'API FastAPI pour prédire les risques de retard de livraison.")

# Formulaire de saisie des caractéristiques de la livraison
st.subheader("Paramètres de la course")

col1, col2 = st.columns(2)

with col1:
    distance_km = st.number_input("Distance (km)", min_value=1.0, max_value=1000.0, value=25.0)
    poids_kg = st.number_input("Poids (kg)", min_value=1.0, max_value=3000.0, value=150.0)
    heure_depart = st.slider("Heure de départ", min_value=0, max_value=23, value=10)
    pluie_mm = st.number_input("Pluie (mm)", min_value=0.0, max_value=60.0, value=0.0)

with col2:
    trafic_index = st.slider("Indice de trafic (0 à 10)", min_value=0.0, max_value=10.0, value=4.0)
    nb_arrets = st.number_input("Nombre d'arrêts", min_value=0, max_value=10, value=2)
    type_vehicule = st.selectbox("Type de véhicule", ["moto", "fourgon", "camion"])

# Bouton de prédiction
if st.button("Lancer la prédiction", type="primary"):
    # Construction du dictionnaire de données
    payload = {
        "distance_km": distance_km,
        "poids_kg": poids_kg,
        "heure_depart": heure_depart,
        "pluie_mm": pluie_mm,
        "trafic_index": trafic_index,
        "nb_arrets": nb_arrets,
        "type_vehicule": type_vehicule
    }

    try:
        # Appel de l'API FastAPI lancée localement
        with st.spinner("Calcul de la prédiction en cours..."):
            response = requests.post(
                "http://127.0.0.1:8000/v1/predict",
                json=payload,
                timeout=15,
            )

        if response.status_code == 200:
            result = response.json()
            prob = result.get("probabilite_retard", 0.0)
            alerte = result.get("alerte", False)

            st.divider()
            st.subheader("Résultat de l'analyse")

            # Affichage visuel selon le résultat
            st.metric(label="Probabilité estimée de retard", value=f"{prob * 100:.1f} %")

            if alerte:
                st.error("⚠️ **Alerte : Risque élevé de retard !** Des mesures préventives sont conseillées.")
            else:
                st.success("✅ **Trajet sécurisé :** Livraison prévue à l'heure probable.")
        else:
            st.error(f"Erreur de l'API (Code {response.status_code}) : {response.text}")

    except requests.exceptions.Timeout:
        st.error("La prédiction prend trop de temps. Vérifiez que l'API répond sur http://127.0.0.1:8000/health.")
    except requests.exceptions.ConnectionError:
        st.error("Impossible de se connecter à l'API. Vérifiez que le serveur Uvicorn est bien démarré sur le port 8000.")
    except requests.exceptions.RequestException as error:
        st.error(f"Erreur lors de l'appel à l'API : {error}")