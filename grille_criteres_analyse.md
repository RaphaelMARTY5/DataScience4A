# Grille de critères — Analyse de données (version renforcée)

## 1) Objectif attendu
Produire une **analyse fiable, traçable et explicable** qui reflète la réalité physique/économique des variables étudiées (prix, consommation, production, température), en **éliminant ou traitant** les valeurs trop éloignées de ce qu’elles représentent réellement.

---

## 2) Critères d’évaluation détaillés

### A. Qualité des données (25%)
- Vérification du schéma : types, unités, fuseau horaire, doublons, valeurs manquantes.
- Contrôle de cohérence minimale :
  - pas de consommation négative,
  - pas de production nucléaire négative,
  - bornes plausibles pour les températures.
- Harmonisation temporelle : granularité homogène (horaire/journalière) et alignement des séries.

**Attendu minimum :** tableau de contrôle qualité (nombre de NA, doublons, incohérences, corrections appliquées).

### B. Détection des valeurs aberrantes (30%)
La détection doit combiner **méthode statistique + contrainte métier**.

1. **Règles statistiques robustes** (au moins une méthode obligatoire) :
   - IQR : outlier si `x < Q1 - 1.5*IQR` ou `x > Q3 + 1.5*IQR`,
   - Z-score robuste (MAD),
   - seuil quantile (ex: P1–P99) pour analyse de sensibilité.

2. **Règles métier** (obligatoires) :
   - bornes physiques réalistes (ex: température France métropolitaine),
   - pics compatibles avec les saisons/heures de pointe,
   - évènements exceptionnels justifiés (crise énergétique, maintenance, météo extrême).

3. **Traitement des aberrants** (à expliciter) :
   - suppression,
   - winsorisation,
   - imputation temporelle (rolling median/interpolation),
   - ou conservation justifiée si événement réel.

**Attendu minimum :** justification du choix + impact mesuré avant/après traitement.

### C. Pertinence analytique (25%)
- Analyse descriptive claire : tendances, saisonnalité, corrélations principales.
- Analyse multivariée cohérente : lien prix ↔ consommation ↔ production ↔ météo.
- Séparation explicite entre signal structurel et bruit/anomalies.

**Attendu minimum :** conclusions alignées avec les indicateurs et graphiques produits.

### D. Validation et robustesse (20%)
- Comparaison des résultats **avec** et **sans** traitement des outliers.
- Test de robustesse selon plusieurs seuils (ex: IQR 1.5 vs 3.0 ; P1–P99 vs P5–P95).
- Vérification de stabilité temporelle (par année/saison).

**Attendu minimum :** section dédiée à la robustesse avec tableau comparatif.

---

## 3) Pipeline recommandé (pratique)
1. Ingestion + normalisation des colonnes/horodatages.
2. Audit qualité initial (NA, doublons, bornes métier).
3. Détection outliers (statistique robuste + règles métier).
4. Traitement choisi et journal des transformations.
5. Recalcul des métriques clés et comparaison avant/après.
6. Conclusions + limites + hypothèses.

---

## 4) Livrables attendus
- Un notebook/script reproductible.
- Un tableau « qualité des données ».
- Un tableau « outliers détectés/traités » avec méthode et justification.
- Des visualisations avant/après traitement.
- Une synthèse finale orientée décision.

---

## 5) Formulation courte (résumé à intégrer dans le rapport)
> Nous devons produire une analyse précise qui écarte (ou corrige) les données trop éloignées de la réalité de la variable étudiée. Cette étape doit reposer à la fois sur des méthodes statistiques robustes et sur des règles métier, avec une justification claire de l’impact avant/après traitement des valeurs aberrantes.
