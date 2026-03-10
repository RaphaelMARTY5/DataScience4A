import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

print("1. Chargement du jeu de données préparé...")
df = pd.read_csv('génération graph/Master_Dataset_Projet_ML_V2.csv', index_col=0, parse_dates=True)

print("1.bis CORRECTION : Filtrage de la période de crise...")
# On supprime les années 2021 et 2022 qui faussent l'apprentissage à cause de la crise énergétique !
df = df[df.index >= '2023-01-01']
print(f"Nouvelle taille du dataset : {len(df)} heures (Marché post-crise).\n")

# 2. Définition des Features (X) et de la Target (y)
# On enlève la cible (Prix) de X. On enlève aussi "Température" si on veut éviter les doublons avec "Consommation" 
# (car la conso inclut déjà l'effet température), mais on peut la laisser pour le Random Forest.
colonnes_X = [
    'Consommation (MW)', 'Eolien (MW)', 'Solaire (MW)', 'Nucléaire (MW)',
    'Température réalisée lissée (°C)', 
    'Vitesse du vent à 100m (m/s)', 'Rayonnement solaire global (W/m2)', # Vos nouveautés physiques !
    'FC moyen mensuel éolien (%)', 'FC moyen mensuel solaire (%)',       # Vos nouveautés de capacité !
    'Mois', 'Jour_Semaine', 'Heure'
]
X = df[colonnes_X]
y = df['Price_EUR_MWh']

print("2. Séparation Train / Test (Critère 6)...")
# On ne prend pas un split aléatoire (shuffle=False) pour respecter la chronologie temporelle !
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
print(f"Entraînement sur {len(X_train)} heures, Test sur {len(X_test)} heures.\n")


print("3. Entraînement du Modèle 1 : Régression Linéaire (Baseline)...")
lr_model = LinearRegression()
lr_model.fit(X_train, y_train)

# Prédictions
y_pred_train_lr = lr_model.predict(X_train)
y_pred_test_lr = lr_model.predict(X_test)

# Scores (Critère 7)
print("--- Résultats Régression Linéaire ---")
print(f"R² Train : {r2_score(y_train, y_pred_train_lr):.3f} | R² Test : {r2_score(y_test, y_pred_test_lr):.3f}")
print(f"Erreur Moyenne (MAE) Test : {mean_absolute_error(y_test, y_pred_test_lr):.2f} €/MWh\n")


print("4. Entraînement du Modèle 2 : Random Forest (Avancé)...")
# On limite la profondeur (max_depth=10 au lieu de 15) pour éviter le surapprentissage (overfitting)
rf_model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
rf_model.fit(X_train, y_train)

# Prédictions
y_pred_train_rf = rf_model.predict(X_train)
y_pred_test_rf = rf_model.predict(X_test)

print("--- Résultats Random Forest ---")
print(f"R² Train : {r2_score(y_train, y_pred_train_rf):.3f} | R² Test : {r2_score(y_test, y_pred_test_rf):.3f}")
print(f"Erreur Moyenne (MAE) Test : {mean_absolute_error(y_test, y_pred_test_rf):.2f} €/MWh\n")

print("5. Analyse de l'importance des variables (Critère 8 : Analyse fine)...")
# Le Random Forest permet de savoir quelles variables ont le plus influencé le prix !
importances = rf_model.feature_importances_
indices = np.argsort(importances)

plt.figure(figsize=(10, 6))
plt.title("Importance des Variables (Features) dans la prédiction du Prix Spot", fontsize=14)
plt.barh(range(len(indices)), importances[indices], color='teal', align='center')
plt.yticks(range(len(indices)), [X.columns[i] for i in indices])
plt.xlabel("Poids relatif")
plt.tight_layout()
plt.savefig('génération graph/feature_importance.png')
print("Graphique d'importance des variables sauvegardé !")