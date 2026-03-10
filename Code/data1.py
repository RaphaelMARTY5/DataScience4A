import pandas as pd
import glob
import matplotlib.pyplot as plt

# 1. Lister tous les fichiers CSV qui commencent par "Day-ahead Prices"
fichiers = glob.glob("Day-ahead Prices_*.csv")
print("Fichiers trouvés :", fichiers) # <-- AJOUTEZ CETTE LIGNE

if len(fichiers) == 0:
    print("ATTENTION : Aucun fichier CSV n'a été trouvé ! Vérifiez le dossier et le nom des fichiers.")
fichiers.sort()

dfs = []

# 2. Boucle de lecture et nettoyage selon le format de l'année
for f in fichiers:
    if "2024-2025" in f:
        # Le fichier 2024 a un formatage particulier avec beaucoup de guillemets
        df = pd.read_csv(f, engine="python", sep=',(?=")')
        df.columns = [c.replace('"', '').strip() for c in df.columns]
        
        df_clean = pd.DataFrame()
        # On extrait la colonne de temps et la colonne de prix
        df_clean['Datetime_Range'] = df['MTU (UTC)'].str.replace('"', '')
        df_clean['Price_EUR_MWh'] = df['Day-ahead Price (EUR/MWh)'].str.replace('"', '').astype(float)
        dfs.append(df_clean)
    else:
        # Les fichiers 2019 à 2023 ont un format classique
        df = pd.read_csv(f)
        df_clean = pd.DataFrame()
        
        # Identification dynamique des colonnes
        col_mtu = [c for c in df.columns if 'MTU' in c][0]
        col_price = [c for c in df.columns if 'Price' in c][0]
        
        df_clean['Datetime_Range'] = df[col_mtu]
        # Conversion des prix en numérique (remplace les erreurs éventuelles par NaN)
        df_clean['Price_EUR_MWh'] = pd.to_numeric(df[col_price], errors='coerce')
        dfs.append(df_clean)

# 3. Concaténation de l'ensemble des données
all_data = pd.concat(dfs, ignore_index=True)

# 4. Traitement des Dates : Extraire uniquement l'heure de début
all_data['Start_Time'] = all_data['Datetime_Range'].str.split(' - ').str[0]

# Convertir en format Datetime officiel de Pandas
all_data['Start_Time'] = pd.to_datetime(all_data['Start_Time'], format='mixed', dayfirst=True)

# Trier chronologiquement et définir la date comme index
all_data.sort_values('Start_Time', inplace=True)
all_data.set_index('Start_Time', inplace=True)

# Suppression de la colonne temporaire
all_data.drop(columns=['Datetime_Range'], inplace=True)

# Affichage des premières lignes et des infos
print(all_data.info())
print(all_data.head())

# 5. Visualisation rapide
plt.figure(figsize=(14, 6))
plt.plot(all_data.index, all_data['Price_EUR_MWh'], linewidth=0.5, color='blue')
plt.title("Prix Spot de l'Électricité (Day-Ahead) en France (2019-2025)")
plt.ylabel("Prix (€/MWh)")
plt.xlabel("Date")
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()

# (Optionnel) Sauvegarder le fichier propre
# all_data.to_csv('Prix_Spot_Nettoyes_2019_2025.csv')