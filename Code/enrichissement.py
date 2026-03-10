import pandas as pd
import numpy as np

print("--- 1. LECTURE DU DATASET EXISTANT ---")
# On recharge le fichier maître que vous aviez créé à l'étape précédente
df = pd.read_csv("génération graph/Master_Dataset_Projet_ML.csv", index_col=0, parse_dates=True)

print("--- 2. AJOUT DU VENT ET RAYONNEMENT (TRI-HORAIRE -> HORAIRE) ---")
# Lecture des données régionales
df_vent = pd.read_csv("enrichissement/rayonnement-solaire-vitesse-vent-tri-horaires-regionaux.csv", sep=";")
df_vent['Date'] = pd.to_datetime(df_vent['Date'], utc=True)
# Étape A : Calcul de la Moyenne Nationale (on fusionne les régions)
df_vent_nat = df_vent.groupby('Date')[['Vitesse du vent à 100m (m/s)', 'Rayonnement solaire global (W/m2)']].mean()
# Étape B : Transformation du pas tri-horaire (toutes les 3h) en pas Horaire
# La méthode "interpolate" permet de lisser les données mathématiquement pour combler les trous
df_vent_horaire = df_vent_nat.resample('1H').interpolate(method='linear')
# Jointure avec le dataset principal
df = df.join(df_vent_horaire, how='left')

print("--- 3. AJOUT DU BILAN ÉLECTRIQUE (DEMI-HEURE -> HORAIRE) ---")
df_bilan = pd.read_csv("enrichissement/bilan-electrique-demi-heure (3).csv", sep=";")
df_bilan['horodate'] = pd.to_datetime(df_bilan['horodate'], utc=True)
df_bilan.set_index('horodate', inplace=True)
# On ne garde que les colonnes qui apportent une information nouvelle (pas déjà dans eCO2mix)
cols_inedites = ['injection_rte', 'consommation_hta', 'production_totale']
df_bilan_horaire = df_bilan[cols_inedites].resample('1H').mean()
df = df.join(df_bilan_horaire, how='left')

print("--- 4. AJOUT DES FACTEURS DE CHARGE (MENSUEL -> HORAIRE) ---")
df_fc = pd.read_csv("enrichissement/fc-tc-nationaux-mensuels-eolien-solaire.csv", sep=";")
# La colonne "Mois" de ce fichier est au format "YYYY-MM" (ex: 2021-03)
df_fc.rename(columns={'Mois': 'YearMonth'}, inplace=True)
# On crée une clé similaire dans notre tableau maître pour faire la liaison
df['YearMonth'] = df.index.strftime('%Y-%m')
df = df.reset_index().merge(df_fc, on='YearMonth', how='left').set_index('index')
df.index.name = 'Datetime'
df.drop(columns=['YearMonth'], inplace=True)

print("--- 5. NETTOYAGE FINAL ---")
# Le bilan électrique (3) ne commence qu'en fin février 2021. 
# On supprime donc les premières semaines de 2021 qui seront vides pour garder un tableau 100% robuste.
df.dropna(inplace=True)

print("\n=== DATASET ENRICHI (V2) ===")
print(df.info())

# Sauvegarde de la Base V2 !
df.to_csv("génération graph/Master_Dataset_Projet_ML_V2.csv")
print("\nFichier 'Master_Dataset_Projet_ML_V2.csv' sauvegardé !")