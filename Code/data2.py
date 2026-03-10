import pandas as pd
import glob
import matplotlib.pyplot as plt

# 1. Lister les fichiers qui commencent par "donnees-de-temperature"
fichiers_meteo = glob.glob("donnees-de-temperature-et-de-pseudo-rayonnement_*.csv")
fichiers_meteo.sort()

# Vérification (pour éviter la même erreur ValueError)
print("Fichiers Météo trouvés :", fichiers_meteo)

if len(fichiers_meteo) == 0:
    print("Erreur : Aucun fichier météo trouvé dans ce dossier.")
else:
    dfs_meteo = []

    # 2. Boucle de lecture (Attention au sep=';')
    for f in fichiers_meteo:
        # On lit le fichier CSV avec le séparateur point-virgule
        df = pd.read_csv(f, sep=';')
        dfs_meteo.append(df)

    # 3. Concaténation des années 2021 à 2024
    all_meteo = pd.concat(dfs_meteo, ignore_index=True)

    # 4. Traitement des Dates et des Fuseaux Horaires (très important !)
    # Le format brut inclut les fuseaux (+01:00, +02:00). On harmonise tout en UTC.
    all_meteo['Horodate'] = pd.to_datetime(all_meteo['Horodate'], utc=True)

    # Trier chronologiquement et définir la date comme index du tableau
    all_meteo.sort_values('Horodate', inplace=True)
    all_meteo.set_index('Horodate', inplace=True)

    # 5. HARMONISATION : Passage de la demi-heure à l'heure !
    # On sélectionne uniquement les colonnes numériques utiles et on fait la moyenne (mean) par heure ('1H')
    colonnes_utiles = ['Température réalisée lissée (°C)', 'Pseudo rayonnement (%)']
    meteo_horaire = all_meteo[colonnes_utiles].resample('1H').mean()

    # Affichage des premières lignes et de la forme de la table (nombre de lignes et colonnes)
    print("\nInfos sur les données météo ramenées au pas horaire :")
    print(meteo_horaire.info())
    print("\nExtrait :")
    print(meteo_horaire.head())

    # 6. Visualisation
    plt.figure(figsize=(14, 6))
    plt.plot(meteo_horaire.index, meteo_horaire['Température réalisée lissée (°C)'], color='darkorange', linewidth=0.5, label='Température moyenne horaire')
    plt.title("Température Réalisée Lissée en France (2021-2024)", fontsize=14)
    plt.ylabel("Température (°C)", fontsize=12)
    plt.xlabel("Date", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.show()
    
    # (Optionnel) Sauvegarder ce fichier propre pour la suite de votre projet
    # meteo_horaire.to_csv('Meteo_Nettoyee_Horaire.csv')