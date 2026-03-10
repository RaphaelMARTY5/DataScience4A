import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

print("--- 1. CHARGEMENT DU DATASET ---")
df = pd.read_csv('génération graph/Master_Dataset_Projet_ML_V2.csv', index_col=0, parse_dates=True)
df_clean = df.copy()

# Dictionnaire pour tracer nos corrections (Livrable : Tableau de Qualité)
journal_qualite = {}

print("--- 2. APPLICATION DES RÈGLES MÉTIER (Critère A & B2) ---")
# Vérification Consommation et Nucléaire (Pas de valeurs négatives)
for col in ['Consommation (MW)', 'Nucléaire (MW)']:
    if col in df_clean.columns:
        erreurs = df_clean[col] < 0
        journal_qualite[f'Valeurs négatives impossibles - {col}'] = erreurs.sum()
        df_clean.loc[erreurs, col] = np.nan # Remplacé par du vide pour le moment

# Vérification Température (Bornes physiques France : -20°C à +45°C)
if 'Température réalisée lissée (°C)' in df_clean.columns:
    erreurs_temp = (df_clean['Température réalisée lissée (°C)'] < -20) | (df_clean['Température réalisée lissée (°C)'] > 45)
    journal_qualite['Températures aberrantes (hors bornes)'] = erreurs_temp.sum()
    df_clean.loc[erreurs_temp, 'Température réalisée lissée (°C)'] = np.nan

# IMPUTATION TEMPORELLE : On bouche les trous mathématiquement
df_clean.interpolate(method='time', inplace=True)


print("--- 3. APPLICATION DES RÈGLES STATISTIQUES / WINSORISATION (Critère B1) ---")
# Définition de la fonction IQR
def winsorize_iqr(dataframe, colonne, multiplier=3.0):
    # On utilise un multiplicateur de 3.0 (très tolérant) au lieu de 1.5 car l'énergie est un marché très volatil
    Q1 = dataframe[colonne].quantile(0.25)
    Q3 = dataframe[colonne].quantile(0.75)
    IQR = Q3 - Q1
    seuil_bas = Q1 - (multiplier * IQR)
    seuil_haut = Q3 + (multiplier * IQR)
    
    # Détection
    outliers = (dataframe[colonne] < seuil_bas) | (dataframe[colonne] > seuil_haut)
    nb_outliers = outliers.sum()
    
    # Traitement (Winsorisation = on plafonne les extrêmes aux seuils)
    dataframe[colonne] = np.clip(dataframe[colonne], seuil_bas, seuil_haut)
    return nb_outliers, seuil_bas, seuil_haut

# Application au Prix Spot
nb_outliers_prix, seuil_b, seuil_h = winsorize_iqr(df_clean, 'Price_EUR_MWh', multiplier=3.0)
journal_qualite[f"Outliers Statistiques Prix (écrêtés hors de [{seuil_b:.1f} , {seuil_h:.1f}])"] = nb_outliers_prix


print("\n=== LIVRABLE 1 : TABLEAU DE QUALITÉ DES DONNÉES ===")
df_bilan = pd.DataFrame(list(journal_qualite.items()), columns=['Type d\'Anomalie', 'Nombre de corrections'])
print(df_bilan.to_string(index=False))


print("\n--- 4. VISUALISATION AVANT / APRÈS (Critère C & D) ---")
plt.figure(figsize=(14, 6))

plt.subplot(1, 2, 1)
plt.boxplot(df['Price_EUR_MWh'].dropna())
plt.title("Avant : Présence de valeurs aberrantes extrêmes")
plt.ylabel("Prix (€/MWh)")

plt.subplot(1, 2, 2)
plt.boxplot(df_clean['Price_EUR_MWh'].dropna())
plt.title("Après : Ecrêtage par méthode IQR (Winsorisation)")

plt.tight_layout()
plt.savefig('génération graph/Outliers_Avant_Apres.png')
print("Graphique Avant/Après sauvegardé !")

# Sauvegarde du dataset parfaitement propre
df_clean.to_csv('génération graph/Master_Dataset_Cleaned.csv')
print("\n[SUCCÈS] Fichier 'Master_Dataset_Cleaned.csv' généré !")