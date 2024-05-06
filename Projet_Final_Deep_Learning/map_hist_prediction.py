import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from pathlib import Path

# Chargement et préparation des données
def load_and_prepare_data():
    data_folder = Path('data')  # Définition du dossier contenant les données
    crime_file = data_folder / 'crime.csv'  # Chemin vers le fichier des crimes
    offense_file = data_folder / 'offense_codes.csv'  # Chemin vers le fichier des codes d'infractions

    # Chargement des données avec gestion de l'encodage
    crime_data = pd.read_csv(crime_file, encoding='windows-1254')
    offense_codes = pd.read_csv(offense_file, encoding='windows-1254')

    # Nettoyage des données en supprimant les valeurs manquantes pour certains champs
    crime_data.dropna(subset=['OFFENSE_CODE', 'OCCURRED_ON_DATE', 'Lat', 'Long', 'DISTRICT'], inplace=True)
    # Fusion des données sur le code d'infraction
    merged_data = crime_data.merge(offense_codes, left_on='OFFENSE_CODE', right_on='CODE', how='left')
    # Conversion de la colonne de date en objet datetime et extraction des composants temporels
    merged_data['OCCURRED_ON_DATE'] = pd.to_datetime(merged_data['OCCURRED_ON_DATE'])
    merged_data['YEAR'] = merged_data['OCCURRED_ON_DATE'].dt.year
    merged_data['MONTH'] = merged_data['OCCURRED_ON_DATE'].dt.month
    merged_data['DAY'] = merged_data['OCCURRED_ON_DATE'].dt.day
    merged_data['HOUR'] = merged_data['OCCURRED_ON_DATE'].dt.hour
    merged_data['DAY_OF_WEEK'] = merged_data['OCCURRED_ON_DATE'].dt.day_name()

    # Regroupement des données par district et par heure, avec agrégation de la latitude, longitude 
    # et du nombre de crimes
    grouped_data = merged_data.groupby(['DISTRICT', 'YEAR', 'MONTH', 'DAY', 'HOUR']).agg({
        'Lat': 'mean',  # Prendre la moyenne des latitudes pour chaque groupe
        'Long': 'mean',  # Prendre la moyenne des longitudes pour chaque groupe
        'CODE': 'size'  # Compter les crimes par groupe
    }).rename(columns={'CODE': 'CRIME_COUNT'}).reset_index()
    return grouped_data

# Construction et entraînement du modèle de prédiction
def build_and_train_model(data):
    features = data[['YEAR', 'MONTH', 'DAY', 'HOUR']]  # Sélection des caractéristiques
    target = data['CRIME_COUNT']  # Cible de la prédiction
    scaler = StandardScaler()  # Initialisation du normalisateur
    features_scaled = scaler.fit_transform(features)  # Normalisation des caractéristiques
    # Construction du modèle de réseau de neurones
    model = Sequential([
        Dense(64, activation='relu', input_shape=(4,)),  # Couche dense avec activation ReLU
        Dropout(0.1),  # Couche de dropout pour réduire le surapprentissage
        Dense(64, activation='relu'),  # Autre couche dense avec activation ReLU
        Dropout(0.1),  # Autre couche de dropout
        Dense(1)  # Couche de sortie
    ])
    # Compilation du modèle avec l'optimiseur Adam et la perte MSE
    model.compile(optimizer='adam', loss='mse')  
    # Entraînement du modèle
    model.fit(features_scaled, target, epochs=10, batch_size=32, validation_split=0.2)
    return model, scaler

def main():
    st.title("Prédiction de la Densité des Crimes à Boston avec Carte et Histogramme")
    data = load_and_prepare_data()  # Chargement et préparation des données
    model, scaler = build_and_train_model(data)  # Construction et entraînement du modèle

    # Sélection de localisation avec latitude et longitude moyennes par l'utilisateur
    location_options = data[['Lat', 'Long']].drop_duplicates().reset_index(drop=True)
    location_list = list(location_options.itertuples(index=False, name=None))

    st.header("Effectuez une prédiction")  # En-tête pour la section de prédiction
    # Sélection de la localisation
    selected_location = st.selectbox("Sélectionnez la localisation", options=location_list) 
    lat, long = selected_location

    year = st.number_input('Année', min_value=2015, max_value=2024, value=2022) # Sélection de l'année
    month = st.number_input('Mois', min_value=1, max_value=12, value=1) # Sélection du mois
    day = st.number_input('Jour', min_value=1, max_value=31, value=1) # Sélection du jour
    hour_range = range(24)  # Prédictions pour chaque heure de la journée

    # Bouton pour déclencher la prédiction
    if st.button('Prédire la Densité des Crimes'):
        # Préparation des caractéristiques pour chaque heure
        features = [[year, month, day, hour] for hour in hour_range]
        features_scaled = scaler.transform(features) # Normalisation des caractéristiques
        predictions = model.predict(features_scaled) # Prédiction de la densité des crimes

        # Préparation des données pour la visualisation
        prediction_data = pd.DataFrame({
            'lat': [lat] * len(hour_range),
            'lon': [long] * len(hour_range),
            'Densité prédite': [pred[0] for pred in predictions]
        })
        # Création d'une carte avec les prédictions
        fig_map = px.scatter_mapbox(
            prediction_data,
            lat='lat', lon='lon', size='Densité prédite',
            color_continuous_scale=px.colors.cyclical.IceFire, size_max=15, zoom=10,
            mapbox_style="open-street-map"
        )
        st.plotly_chart(fig_map) # Affichage de la carte

        # Création d'un histogramme avec les prédictions par heure
        fig_histogram = px.bar(
            x=list(hour_range),
            y=[pred[0] for pred in predictions],
            labels={'x': 'Heure du Jour', 'y': 'Densité des Crimes'},
            title="Prédictions de la Densité des Crimes par Heure"
        )
        st.plotly_chart(fig_histogram) # Affichage de l'histogramme

# Point d'entrée principal
if __name__ == "__main__":
    main()
