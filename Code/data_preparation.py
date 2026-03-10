import pandas as pd
import glob
import re

print("--- 1. PRIX DE L'ÉLECTRICITÉ (AVEC LECTURE INTELLIGENTE) ---")
fichiers_prix = glob.glob("Prix/Day-ahead Prices_*.csv")
dfs_prix = []

for f in fichiers_prix:
    # Lecture des premières lignes pour détecter le format
    with open(f, 'r', encoding='utf-8') as file:
        lignes_debut = [file.readline() for _ in range(5)]
        
    # Format Excel (2022-2023)
    if len(lignes_debut) > 0 and "Day-ahead Prices" in lignes_debut[0] and "12.1.D" in lignes_debut[1]:
        current_date = None
        data = []
        for line in lignes_debut:
            match = re.search(r'(\d{2}\.\d{2}\.\d{4}) \d{2}:\d{2} -', line)
            if match: current_date = match.group(1); break
                
        with open(f, 'r', encoding='utf-8') as file:
            for line in file:
                parts = line.strip().split(',')
                if not parts: continue
                col1 = parts[0].strip()
                if re.match(r'^\d{2}\.\d{2}\.\d{4}$', col1):
                    current_date = col1
                    continue
                if re.match(r'^\d{2}:\d{2} - \d{2}:\d{2}$', col1):
                    price_str = parts[1].strip() if len(parts) > 1 else ""
                    try: price = float(price_str) if price_str and price_str != '-' else None
                    except ValueError: price = None
                    start_hour = col1.split(' - ')[0]
                    data.append({'Datetime': f"{current_date} {start_hour}", 'Price_EUR_MWh': price})
                    
        df = pd.DataFrame(data)
        df['Datetime'] = pd.to_datetime(df['Datetime'], format='%d.%m.%Y %H:%M', errors='coerce', utc=True)
        df.dropna(subset=['Price_EUR_MWh'], inplace=True)
        df.set_index('Datetime', inplace=True)
        dfs_prix.append(df)
        
    # Format 2024
    elif len(lignes_debut) > 0 and 'MTU (UTC)' in lignes_debut[0]:
        df = pd.read_csv(f, engine="python", sep=',(?=")')
        df.columns = [c.replace('"', '').strip() for c in df.columns]
        df_clean = pd.DataFrame()
        df_clean['Datetime'] = df['MTU (UTC)'].str.replace('"', '').str.split(' - ').str[0]
        df_clean['Price_EUR_MWh'] = df['Day-ahead Price (EUR/MWh)'].str.replace('"', '').astype(float)
        df_clean['Datetime'] = pd.to_datetime(df_clean['Datetime'], format='mixed', dayfirst=True, utc=True)
        df_clean.set_index('Datetime', inplace=True)
        dfs_prix.append(df_clean)
        
    # Format Standard (2019-2021)
    else:
        df = pd.read_csv(f)
        df_clean = pd.DataFrame()
        col_mtu = [c for c in df.columns if 'MTU' in c][0]
        col_price = [c for c in df.columns if 'Price' in c][0]
        df_clean['Datetime'] = df[col_mtu].str.split(' - ').str[0]
        df_clean['Price_EUR_MWh'] = pd.to_numeric(df[col_price], errors='coerce')
        df_clean['Datetime'] = pd.to_datetime(df_clean['Datetime'], format='mixed', dayfirst=True, utc=True)
        df_clean.set_index('Datetime', inplace=True)
        dfs_prix.append(df_clean)

df_prix = pd.concat(dfs_prix)
df_prix = df_prix[~df_prix.index.duplicated(keep='first')] # Suppression des doublons
df_prix.sort_index(inplace=True)


print("--- 2. TEMPÉRATURE & RAYONNEMENT ---")
fichiers_meteo = glob.glob("temperature/donnees-de-temperature-et-de-pseudo-rayonnement_*.csv")
dfs_meteo = [pd.read_csv(f, sep=';') for f in fichiers_meteo]

df_meteo = pd.concat(dfs_meteo, ignore_index=True)
df_meteo['Horodate'] = pd.to_datetime(df_meteo['Horodate'], utc=True)
df_meteo.set_index('Horodate', inplace=True)
# Rééchantillonnage par heure
df_meteo_horaire = df_meteo[['Température réalisée lissée (°C)', 'Pseudo rayonnement (%)']].resample('1H').mean()


print("--- 3. PRODUCTION & CONSOMMATION (éCO2mix) ---")
# C'est cette partie qui manquait dans votre code !
df_eco = pd.read_csv("EnR & nucléaire/eco2mix-national-cons-def.csv", sep=";")
cols_eco = ['Date et Heure', 'Consommation (MW)', 'Eolien (MW)', 'Solaire (MW)', 'Nucléaire (MW)']
df_eco = df_eco[cols_eco]
df_eco['Date et Heure'] = pd.to_datetime(df_eco['Date et Heure'], utc=True)
df_eco.set_index('Date et Heure', inplace=True)
# Rééchantillonnage par heure
df_eco_horaire = df_eco.resample('1H').mean()


print("--- 4. FUSION GLOBALE DES 3 BASES (MERGE) ---")
# On fusionne Prix + Météo
df_final = pd.merge(df_prix, df_meteo_horaire, left_index=True, right_index=True, how='inner')
# On ajoute éCO2mix (Consommation, Nucléaire, EnR) !
df_final = pd.merge(df_final, df_eco_horaire, left_index=True, right_index=True, how='inner')

# Nettoyage des heures incomplètes
df_final.dropna(inplace=True)

# Création des variables temporelles (Feature Engineering)
df_final['Mois'] = df_final.index.month
df_final['Jour_Semaine'] = df_final.index.dayofweek
df_final['Heure'] = df_final.index.hour

print("\n=== DATASET FINAL COMPLET ===")
print(df_final.info())
print("\nExtrait :\n", df_final.head())

# Sauvegarde de la base d'apprentissage
df_final.to_csv('génération graph/Master_Dataset_Projet_ML.csv')
print("\n[SUCCÈS] Le fichier 'Master_Dataset_Projet_ML.csv' contient toutes les données !")