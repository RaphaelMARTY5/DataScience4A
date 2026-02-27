import pandas as pd
import glob
import matplotlib.pyplot as plt

print("--- 1. CHARGEMENT ET NETTOYAGE DES PRIX SPOT ---")
fichiers_prix = glob.glob("Day-ahead Prices_*.csv")
dfs_prix = []

for f in fichiers_prix:
    if "2024-2025" in f:
        df = pd.read_csv(f, engine="python", sep=',(?=")')
        df.columns = [c.replace('"', '').strip() for c in df.columns]
        df_clean = pd.DataFrame()
        df_clean['Datetime'] = df['MTU (UTC)'].str.replace('"', '').str.split(' - ').str[0]
        df_clean['Price_EUR_MWh'] = df['Day-ahead Price (EUR/MWh)'].str.replace('"', '').astype(float)
        dfs_prix.append(df_clean)
    else:
        df = pd.read_csv(f)
        df_clean = pd.DataFrame()
        col_mtu = [c for c in df.columns if 'MTU' in c][0]
        col_price = [c for c in df.columns if 'Price' in c][0]
        df_clean['Datetime'] = df[col_mtu].str.split(' - ').str[0]
        df_clean['Price_EUR_MWh'] = pd.to_numeric(df[col_price], errors='coerce')
        dfs_prix.append(df_clean)

df_prix = pd.concat(dfs_prix, ignore_index=True)
# CONVERSION EN UTC OBLIGATOIRE POUR LE MERGE
df_prix['Datetime'] = pd.to_datetime(df_prix['Datetime'], format='mixed', dayfirst=True, utc=True)
df_prix.set_index('Datetime', inplace=True)
df_prix.sort_index(inplace=True)


print("--- 2. CHARGEMENT ET RÉÉCHANTILLONNAGE DE LA MÉTÉO ---")
fichiers_meteo = glob.glob("donnees-de-temperature-et-de-pseudo-rayonnement_*.csv")
dfs_meteo = []

for f in fichiers_meteo:
    df = pd.read_csv(f, sep=';')
    dfs_meteo.append(df)

df_meteo = pd.concat(dfs_meteo, ignore_index=True)
df_meteo['Horodate'] = pd.to_datetime(df_meteo['Horodate'], utc=True)
df_meteo.set_index('Horodate', inplace=True)
df_meteo.sort_index(inplace=True)

# Passage au pas horaire
colonnes_meteo = ['Température réalisée lissée (°C)', 'Pseudo rayonnement (%)']
df_meteo_horaire = df_meteo[colonnes_meteo].resample('1H').mean()


print("--- 3. FUSION DES DONNÉES (MERGE) ---")
# On fusionne sur l'index (la date) en gardant uniquement les dates communes (inner)
df_final = pd.merge(df_prix, df_meteo_horaire, left_index=True, right_index=True, how='inner')

# Nettoyage des éventuelles lignes avec des données manquantes (NaN)
df_final.dropna(inplace=True)


print("--- 4. CRÉATION DES VARIABLES TEMPORELLES (FEATURE ENGINEERING) ---")
# Ces variables aideront votre modèle à comprendre la saisonnalité et les heures de pointe
df_final['Mois'] = df_final.index.month
df_final['Jour_Semaine'] = df_final.index.dayofweek # 0 = Lundi, 6 = Dimanche
df_final['Heure'] = df_final.index.hour

print("\n=== APERÇU DU DATASET FINAL PRÊT POUR LE MACHINE LEARNING ===")
print(df_final.info())
print("\n", df_final.head())

# Sauvegarde pour l'étape de Machine Learning
df_final.to_csv('Dataset_Projet_ML_Pret.csv')
print("\n Fichier 'Dataset_Projet_ML_Pret.csv' sauvegardé avec succès !")