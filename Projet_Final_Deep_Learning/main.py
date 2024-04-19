import pandas as pd
import streamlit as st
import plotly.express as px
from pathlib import Path

# Chargement des données
def load_data():
    data_folder = Path('data')
    crime_file = data_folder / 'crime.csv'
    offense_file = data_folder / 'offense_codes.csv'

    if not crime_file.exists() or not offense_file.exists():
        st.error(f"Les fichiers de données n'ont pas été trouvés dans le répertoire {data_folder}.")
        return None, None
    
    crime_data = pd.read_csv(crime_file, encoding='windows-1254')
    offense_codes = pd.read_csv(offense_file, encoding='windows-1254')
    return crime_data, offense_codes

# Nettoyage des données
def clean_data(crime_data, offense_codes):
    if crime_data is None or offense_codes is None:
        return None
    # Suppression des données manquantes
    crime_data.dropna(subset=['OFFENSE_CODE', 'OCCURRED_ON_DATE', 'Lat', 'Long'], inplace=True)
    offense_codes.dropna(subset=['CODE'], inplace=True)

    # Fusion des jeux de données sur les codes des infractions
    merged_data = crime_data.merge(offense_codes, left_on='OFFENSE_CODE', right_on='CODE', how='left')

    # Suppression des lignes où la valeur de la latitude est -1
    merged_data = merged_data[merged_data['Lat'] != -1]
    return merged_data

# Traitement des données
def process_data(merged_data):
    if merged_data is None:
        return None
    # Conversion des dates au format datetime
    merged_data['OCCURRED_ON_DATE'] = pd.to_datetime(merged_data['OCCURRED_ON_DATE'])
    # Extraction de l'année, du mois et d'autres composants de la date
    merged_data['YEAR'] = merged_data['OCCURRED_ON_DATE'].dt.year
    merged_data['MONTH'] = merged_data['OCCURRED_ON_DATE'].dt.month
    merged_data['DAY'] = merged_data['OCCURRED_ON_DATE'].dt.day
    merged_data['HOUR'] = merged_data['OCCURRED_ON_DATE'].dt.hour
    merged_data['DAY_OF_WEEK'] = merged_data['OCCURRED_ON_DATE'].dt.day_name()
    # Création des groupes d'heures pour définir les plages horaires
    bins = [0, 6, 12, 18, 24]
    labels = ['Night', 'Morning', 'Afternoon', 'Evening']
    merged_data['TIME_OF_DAY'] = pd.cut(merged_data['HOUR'], bins=bins, labels=labels, right=False)
    # Calcul de la densité des crimes par district
    crime_counts = merged_data['DISTRICT'].value_counts()
    merged_data['CRIME_DENSITY'] = merged_data['DISTRICT'].map(crime_counts)
    # Remplacement des valeurs NaN dans CRIME_DENSITY par la moyenne
    merged_data['CRIME_DENSITY'].fillna(merged_data['CRIME_DENSITY'].mean(), inplace=True)
    return merged_data

# Initialisation de l'app Streamlit
def main():
    st.title("Dashboard des Crimes à Boston")

    # Chargement et préparation des données
    crime_data, offense_codes = load_data()
    if crime_data is not None and offense_codes is not None:
        merged_data = clean_data(crime_data, offense_codes)
        processed_data = process_data(merged_data)
        
        # Continuer uniquement si les données ont été chargées correctement
        if processed_data is not None:
            # Widget de sélection pour choisir l'année
            years = processed_data['YEAR'].unique()
            selected_year = st.selectbox('Choisissez une année', options=sorted(years, reverse=True))

            # Filtrer les données par l'année sélectionnée
            data_filtered = processed_data[processed_data['YEAR'] == selected_year]

            # Histogramme des crimes par mois
            st.header("Histogramme des Crimes par Mois")
            fig_monthly_crimes = px.histogram(data_filtered, x='MONTH', nbins=12, title="Répartition mensuelle des crimes")
            st.plotly_chart(fig_monthly_crimes)

            # Carte des crimes
            st.header("Carte des Crimes à Boston")
            fig_map = px.scatter_mapbox(data_filtered, lat='Lat', lon='Long', color='TIME_OF_DAY', size='CRIME_DENSITY',
                                        color_continuous_scale=px.colors.cyclical.IceFire, size_max=15, zoom=10,
                                        mapbox_style="open-street-map", title="Localisation des Crimes")
            st.plotly_chart(fig_map)

            # Autres analyses et visualisations
            st.header('Densité des Crimes par District')
            fig_density = px.bar(data_filtered, x='DISTRICT', y='CRIME_DENSITY', title='Densité des Crimes par District')
            st.plotly_chart(fig_density)

# Point d'entrée du script Streamlit
if __name__ == "__main__":
    main()
