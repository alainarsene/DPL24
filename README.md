# DPL24
 DeepLearning
 
## Description du Projet

Ce projet vise à fournir une visualisation interactive et facile à utiliser des données de criminalité dans la ville de Boston. Utilisant Streamlit et Plotly pour le frontend, il permet aux utilisateurs de visualiser les tendances de la criminalité au fil du temps, de découvrir la densité des crimes par district et d'examiner les différents types de crimes répertoriés dans la base de données.

Les données sont chargées et nettoyées à l'aide de pandas, offrant un aperçu précis des incidents enregistrés. Les utilisateurs peuvent filtrer les résultats selon l'année, observer la répartition mensuelle des crimes, et localiser géographiquement les événements sur une carte.

## Installation
```bash
# Cloner le dépôt
git clone https://github.com/alainarsene/DPL24.git

# Positionnez vous dans le répertoire racine
cd Projet_Final_Deep_Learning

# Créer et activer un environnement virtuel 
python -m venv deep_venv ou python3 -m venv deep_venv
source deep_venv/bin/activate  # Sur Unix ou MacOS
deep_venv\Scripts\activate     # Sur Windows

# Installer les dépendances nécessaires
pip install -r requirements.txt

# Exécuter le projet
streamlit run map_hist_prediction.py
Renseignez votre mail (si elle vous est demandée) et l'adresse du dashboard vous sera fournie (copiez l'adresse dans un navigateur de votre choix) ou la page s'ouvrira automatiquement dans votre navigateur par défaut
