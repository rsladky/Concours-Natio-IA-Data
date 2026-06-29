# Dossier de proposition — Seconde vie du FACOM SCANDIAG® (DX.TSCANPB)
### Remis à la Direction RSE de FACOM — Groupe Stanley Black & Decker

---

## 1. Équipe

| Nom | Classe |
|-----|--------|
| CONTI Jérémy | B3 IA DATA |
| SLADKY Robin | B3 IA DATA |
| MIRALLES Baptiste | B3 IA DATA |
| AHOLOU Sophie | B3 IA DATA |
| MERY Téo | B3 IA DATA |
| LE COZ Tara | B3 IA DATA |

**Date :** Concours National Ynov Informatique — 29/06/2026

---

## 2. Contexte et enjeu RSE

Le **FACOM SCANDIAG® (DX.TSCANPB)** est un analyseur d'usure de disques de frein et de pneus
qui n'est plus commercialisé. Un stock conséquent reste immobilisé. FACOM, fidèle à ses
engagements RSE, refuse de mettre ces produits au rebut et mandate les équipes Ynov pour
imaginer une **seconde vie** pour leurs composants.

L'enjeu est double :
- **Économique :** valoriser un stock de matériel fonctionnel plutôt que de le déclasser.
- **Environnemental :** éviter le traitement en déchets d'équipements électriques et
  électroniques (DEEE) de composants de précision (MCU, capteur CMOS, diode laser,
  module Bluetooth).

---

## 3. Rétro-ingénierie du produit

### 3.1 Fonctionnement d'origine

Le SCANDIAG® fonctionne par **triangulation laser** :
1. Une **diode laser classe 3R** (rouge, 650 nm) équipée d'une lentille cylindrique projette
   une **ligne laser** sur la surface à mesurer (disque de frein ou flanc de pneu).
2. Un **capteur CMOS** (module caméra) observe la déformation de cette ligne.
3. Un **MCU** calcule le profil de hauteur à partir de la déformation géométrique (principe
   de triangulation).
4. Le résultat est transmis via **Bluetooth Low Energy** vers une application mobile ou PC.
5. L'autonomie est assurée par une **batterie Li-ion 3,7 V / 0,62 Ah** (~500 mesures/charge).

### 3.2 Composants identifiés

> *(TODO jour J : compléter les références et joindre les datasheets)*  
> Voir inventaire détaillé : [`../01-retro-ingenierie/composants.md`](../01-retro-ingenierie/composants.md)

| Composant | Référence | Fonction exploitable |
|-----------|-----------|---------------------|
| MCU / SoC principal | *(TODO)* | Calcul, contrôle, BT host |
| Module Bluetooth BLE | *(TODO)* | Communication sans fil |
| Capteur CMOS | *(TODO)* | Acquisition image |
| Diode laser 650 nm | *(TODO)* | Projection ligne structurée |
| Batterie Li-ion | *(TODO)* | Alimentation portable 3,7 V / 620 mAh |
| Régulateur / DC-DC | *(TODO)* | Rail 3,3 V pour toute la logique |
| Flash externe SPI | *(TODO)* | Stockage firmware / données |

### 3.3 Schéma fonctionnel

> Voir schéma Mermaid complet : [`../01-retro-ingenierie/schema-fonctionnel.md`](../01-retro-ingenierie/schema-fonctionnel.md)

Synthèse :

```
Batterie Li-ion 3,7V
       │
   [DC-DC / Régulateur] → 3,3V
       │
   [MCU] ─── DVP/CSI ───→ [Caméra CMOS]
       │                       ↑
       ├── GPIO/PWM ───→ [Driver laser] ─→ [Laser 650nm] ─→ [Lentille cylindrique]
       ├── UART/SPI ───→ [Module BT BLE] ──── BLE ───→ App mobile
       ├── SPI ─────────→ [Flash externe]
       └── GPIO ─────→ [Boutons / LEDs / Écran]
       UART ─────────→ [USB/TTL] ──── USB ───→ PC (debug/flash)
```

### 3.4 Datasheets archivées

> *(TODO jour J : joindre les PDF dans `../01-retro-ingenierie/datasheets/`)*

---

## 4. Champ des possibles

### 4.1 Fonctions réutilisables en l'état

> Voir détail : [`../02-champ-des-possibles/fonctions-reutilisables.md`](../02-champ-des-possibles/fonctions-reutilisables.md)

| Fonction | Valeur RSE |
|----------|-----------|
| Triangulation laser (profilométrie) | ⭐⭐⭐⭐⭐ |
| Acquisition image CMOS | ⭐⭐⭐⭐ |
| Bluetooth Low Energy | ⭐⭐⭐⭐ |
| Calcul embarqué MCU | ⭐⭐⭐⭐⭐ |
| Alimentation Li-ion portable | ⭐⭐⭐⭐ |

### 4.2 Extensions possibles

> Voir détail : [`../02-champ-des-possibles/extensions-possibles.md`](../02-champ-des-possibles/extensions-possibles.md)

Sans modification matérielle invasive, le SCANDIAG peut être étendu par :
- Connexion PC via USB/TTL existant (pipeline Data/IA côté PC)
- Module WiFi ESP8266 sur UART libre
- Capteur ToF VL53L1X sur I²C libre
- Carte SD sur SPI libre pour logging autonome

### 4.3 Limites fonctionnelles

> Voir détail : [`../02-champ-des-possibles/limites.md`](../02-champ-des-possibles/limites.md)

- Plage de mesure calibrée pour l'automobile (~5–15 cm, quelques mm d'étendue).
- Laser 3R : usage encadré, protection oculaire requise.
- Batterie 620 mAh : autonomie suffisante pour les usages intermittents.
- Firmware propriétaire : re-flash nécessaire pour les usages alternatifs.

---

## 5. Idéation — Concepts de réemploi

> Voir fiches complètes : [`../03-ideation/concepts.md`](../03-ideation/concepts.md)

### Tableau de synthèse

| Concept | Description | Valeur | Difficulté | Réemploi |
|---------|-------------|--------|------------|---------|
| 1 — **ProfilScan** ⭐ | Profilomètre open-source + pipeline Data/IA | 9/10 | 6/10 | **95%** |
| 2 — WearAI | Détecteur d'usure universel (vélo, moto, EPI) | 8/10 | 5/10 | 90% |
| 3 — RecycloScan | Scanner de tri matériaux pour recyclage | 8/10 | 7/10 | 70% |
| 4 — LevelSense | Capteur de niveau par triangulation laser | 7/10 | 5/10 | 80% |
| 5 — StemKit | Kit pédagogique vision + laser (lycées / BTS) | 7/10 | 4/10 | 100% |
| 6 — InspectBot | Caméra d'inspection IoT Bluetooth | 6/10 | 7/10 | 55% |
| 7 — RoadScan | Détection d'obstacles micromobilité | 7/10 | 8/10 | 75% |

---

## 6. Concept retenu — ProfilScan

### 6.1 Description

**ProfilScan** transforme le SCANDIAG® en un **profilomètre / scanner 3D à ligne laser
open-source**. La chaîne matérielle est préservée à 95% (seul le firmware est remplacé).
Un pipeline Data/IA tourne côté PC ou Raspberry Pi :

1. **Acquisition** : la caméra CMOS envoie l'image de la ligne laser déformée.
2. **Extraction** : détection de la ligne par barycentre sous-pixel (OpenCV).
3. **Triangulation** : conversion pixels → profil de hauteur (mm) par calibration.
4. **Analyse ML** : RandomForest classifie l'état de surface (neuf / usé / très usé).
5. **Rapport** : sortie texte + figure PNG, dans l'esprit du rapport SCANDIAG d'origine.

### 6.2 Applications RSE et métier

| Domaine | Application | Valeur RSE |
|---------|-------------|-----------|
| Industrie | Contrôle qualité de pièces mécaniques sans instrument dédié | Évite l'achat d'un profilomètre neuf (~5 000–50 000 €) |
| Maintenance | Mesure d'usure multi-domaines (outils, plaquettes, EPI) | Remplace le remplacement préventif inutile |
| Pédagogie | Kit vision + laser pour cours STEM (lycée, BTS, Licence) | Seconde vie éducative, zéro DEEE |
| Recherche | Profilomètre open-source pour laboratoires sans budget | Démocratisation de la métrologie |

### 6.3 Justification du choix

1. **Réemploi maximal (95%)** : la totalité de la chaîne de valeur du SCANDIAG (laser, caméra,
   MCU, Bluetooth, batterie) est exploitée. Aucun composant n'est mis au rebut.

2. **Faisabilité démontrée** : la triangulation laser est une technique bien documentée,
   implémentable en Python/OpenCV en quelques centaines de lignes — prouvé par le POC joint.

3. **Cohérence avec la démarche RSE de FACOM** : le produit ne disparaît pas, il change
   d'application. Il reste un instrument de mesure — sa vocation première.

4. **Extensibilité** : WearAI (concept 2) et StemKit (concept 5) sont des déclinaisons du
   même hardware, exploitables sans développement supplémentaire majeur.

---

## 7. Preuve de concept (POC)

### 7.1 Description technique

Le POC est un **pipeline Python modulaire** démontrant la chaîne complète sans le matériel
(données synthétiques), conçu pour recevoir le vrai device SCANDIAG par simple substitution
de la source d'entrée.

**Environnement :** Python 3.10+, OpenCV, NumPy, SciPy, scikit-learn, Matplotlib.

**Résultats sur données synthétiques :**
- Accuracy du classificateur ML : ~95% (validation croisée 5-fold sur 600 exemples)
- 4 cas de test : surface plane, sinusoïdale, en rampe, avec défaut local

### 7.2 Structure du code

> Voir [`../04-poc/README.md`](../04-poc/README.md) pour les instructions d'installation et
> d'exécution complètes.

| Module | Rôle |
|--------|------|
| `src/acquisition.py` | Sources d'image (fichier / caméra / UART-série) |
| `src/laser_extraction.py` | Détection ligne laser (barycentre sous-pixel) |
| `src/triangulation.py` | Conversion positions → profil mm + calibration |
| `src/analyse_ml.py` | Features (stats + FFT) + RandomForest |
| `src/rapport.py` | Rapport texte + figure PNG |
| `demo.py` | Pipeline bout-en-bout sur données synthétiques |

### 7.3 Lancer le POC

```bash
cd 04-poc
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python demo.py
```

### 7.4 Brancher le vrai device (jour J)

Remplacer dans `demo.py` :
```python
# Avant (synthétique)
image = generer_image_synthetique(profil=cas, bruit=1.5)

# Après (device réel via UART/USB-TTL)
image = depuis_serie(port="/dev/cu.usbserial-0001", baudrate=115200)
```

---

## 8. Documentation des fonctions développées

### `acquisition.generer_image_synthetique()`
Génère une image simulant la vue caméra du SCANDIAG avec une ligne laser déformée selon
un profil de hauteur paramétrable (plat / sinusoïde / rampe / défaut).

### `laser_extraction.extraire_ligne_laser()`
Détecte la position sous-pixel de la ligne laser dans chaque colonne de l'image par
calcul du barycentre des pixels lumineux après seuillage Otsu sur le canal rouge.

### `laser_extraction.lisser_positions()`
Lisse le vecteur de positions par filtre de Savitzky-Golay pour réduire le bruit
sans dégrader les discontinuités réelles (défauts de surface).

### `triangulation.positions_vers_profil()`
Convertit les positions pixel de la ligne en profil de hauteur en mm via les paramètres
de calibration (y_reference, facteur mm/pixel).

### `triangulation.calibrer_depuis_mire()`
Détermine le facteur de calibration par régression linéaire sur des mesures prises
avec des cales d'épaisseur connue.

### `triangulation.statistiques_profil()`
Calcule min, max, étendue, moyenne, écart-type et rugosité Ra (ISO 4287) du profil.

### `analyse_ml.extraire_features()`
Extrait 14 features numériques d'un profil 1D : statistiques de base, rugosité Ra/Rq,
skewness, kurtosis, 5 premières amplitudes FFT.

### `analyse_ml.ClassificateurUsure`
Classificateur RandomForest 3 classes (neuf / usé / très usé). Méthodes : `entrainer()`,
`predire()`, `sauvegarder()`, `charger()`.

### `rapport.generer_rapport_texte()`
Produit un rapport de mesure formaté en texte (console + fichier .txt) avec les
statistiques du profil, le diagnostic ML et le verdict.

### `rapport.generer_rapport_figure()`
Génère une figure matplotlib 3 panneaux : image caméra brute + ligne détectée,
profil de hauteur, tableau de synthèse + verdict ML avec code couleur.

---

## 9. Bilan RSE

| Indicateur | Valeur |
|------------|--------|
| Taux de réemploi composants | **95%** |
| Déchets DEEE évités | 1 unité → 0 rebut |
| Nouveaux composants nécessaires | 0 (POC PC) / 1 Raspberry Pi (déploiement autonome) |
| Coût de la seconde vie | ~0 € (logiciel open-source) |
| Domaines d'application | Industrie, maintenance, pédagogie, recherche |

---

*Dossier produit dans le cadre du Concours National Informatique Ynov — Réemploi RSE FACOM SCANDIAG® (DX.TSCANPB).*  
*Proposé à la Direction RSE de FACOM / Stanley Black & Decker.*
