import pandas as pd
import matplotlib.pyplot as plt

print("Chargement des données éCO2mix...")
# 1. Lecture des données
df_eco = pd.read_csv("eco2mix-national-cons-def.csv", sep=";")

# 2. Sélection des colonnes essentielles
cols_eco = ['Date et Heure', 'Consommation (MW)', 'Eolien (MW)', 'Solaire (MW)', 'Nucléaire (MW)']
df_eco = df_eco[cols_eco]

# 3. Conversion des dates et gestion du fuseau horaire
df_eco['Date et Heure'] = pd.to_datetime(df_eco['Date et Heure'], utc=True)
df_eco.set_index('Date et Heure', inplace=True)
df_eco.sort_index(inplace=True)

print("Calcul des moyennes journalières...")
# 4. ASTUCE : Passage en moyenne journalière ('1D') pour que le graphique soit lisible sur 4 ans
# Sinon, 35 000 heures = un gros bloc d'encre !
df_eco_daily = df_eco.resample('1D').mean().dropna()

print("Génération du graphique...")
# 5. Création du graphique sur l'ensemble de la période
plt.figure(figsize=(14, 7))

# Tracé des courbes avec des couleurs personnalisées
plt.plot(df_eco_daily.index, df_eco_daily['Consommation (MW)'], label='Consommation', color='black', linewidth=1.2)
plt.plot(df_eco_daily.index, df_eco_daily['Nucléaire (MW)'], label='Nucléaire', color='green', linewidth=1)
plt.plot(df_eco_daily.index, df_eco_daily['Eolien (MW)'], label='Eolien', color='blue', linewidth=0.8, alpha=0.8)
plt.plot(df_eco_daily.index, df_eco_daily['Solaire (MW)'], label='Solaire', color='orange', linewidth=0.8, alpha=0.8)

# Décorations pour un rendu professionnel (pour le poster)
plt.title("Production & Consommation Énergétique en France (Moyenne journalière 2021-2024)", fontsize=16)
plt.ylabel("Puissance (MW)", fontsize=12)
plt.xlabel("Date", fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(loc='upper right', fontsize=10)
plt.tight_layout()

# Affichage du graphique
plt.show()