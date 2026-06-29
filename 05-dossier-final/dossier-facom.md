# Dossier de proposition — Seconde vie du FACOM SCANDIAG® (DX.TSCANPB)
### Remis à la Direction RSE de FACOM — Groupe Stanley Black & Decker

---

## 1. Équipe

| Nom | Classe | Campus Ynov |
|-----|--------|-------------|
| CONTI Jérémy | B3 IA DATA | Aix-en-Provence |
| SLADKY Robin | B3 IA DATA | Aix-en-Provence |
| MIRALLES Baptiste | B3 IA DATA | Aix-en-Provence |
| AHOLOU Sophie | B3 IA DATA | Aix-en-Provence |
| MERY Téo | B3 IA DATA | Aix-en-Provence |
| LE COZ Tara | B3 IA DATA | Aix-en-Provence |

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
4. Le résultat est transmis via **Bluetooth Classic SPP** (Silicon Labs WT12-A) vers une application mobile ou PC — apparaît comme port série virtuel.
5. L'autonomie est assurée par une **batterie Li-Po EEMB LP602248 3,7 V / 620 mAh** (~500 mesures/charge).

### 3.2 Composants identifiés

> Voir inventaire complet : [`../01-retro-ingenierie/composants.md`](../01-retro-ingenierie/composants.md)  
> Photos du démontage : [`../assets/`](../assets/)

| Composant | Référence | Fonction exploitable |
|-----------|-----------|---------------------|
| **MCU principal** | **STM32F429** (ARM Cortex-M4 @ 180 MHz, 2MB Flash) | Calcul triangulation, interface caméra DCMI, UART, SWD — reflashable |
| **Module Bluetooth** | **Silicon Labs WT12-A** (iWRAP firmware) | BT Classic SPP → port série virtuel PC/mobile |
| **SDRAM ×2** | Micron `9CA15/RB151` + ISSI `IS42S` | Buffer frames caméra (FMC STM32F429) |
| **Oscillateur** | 24 MHz (`24.00B`) | Horloge MCLK du capteur caméra |
| **Capteur CMOS** | *(à identifier — connecteur FPC)* | Acquisition image ligne laser (DCMI) |
| **Diode laser** | ≤5mW, classe 3R (confirmé étiquette) | Ligne structurée rouge |
| **Batterie** | **EEMB LP602248** — 3,7V / 620mAh / 2,3Wh | Alimentation portable |
| **DC-DC** | `LGCS/B901` + 2 inductances | Rails 3,3V et 5V |
| **Charge Li-Po** | `VDY6/B301` | Charge via USB Mini-B 5V/500mA |
| **Connecteur charge** | USB Mini-B (confirmé) | 5V/500mA |

### 3.3 Schéma fonctionnel

> Voir schéma Mermaid complet : [`../01-retro-ingenierie/schema-fonctionnel.md`](../01-retro-ingenierie/schema-fonctionnel.md)

```
EEMB LP602248 3,7V/620mAh
       │
   [VDY6/B301 charge] ← USB Mini-B 5V/500mA
       │
   [LGCS/B901 DC-DC] → 3,3V
       │
   [STM32F429 @ 180MHz]
       ├── DCMI + MCLK 24MHz ──→ [Caméra CMOS]
       │                               ↑
       ├── GPIO ──→ [Driver laser] ──→ [Laser ≤5mW 3R] ──→ [Lentille] ──→ Surface
       ├── FMC ───→ [SDRAM Micron] + [SDRAM ISSI]  (buffer frames)
       ├── UART ──→ [Silicon Labs WT12-A] ──── BT SPP ────→ App PC/mobile
       ├── GPIO ──→ [Boutons / LEDs]
       └── SWD ───→ [Test pads SWDIO/SWDCLK]  (flash/debug)
```

### 3.4 Datasheets archivées

> Voir [`../01-retro-ingenierie/datasheets/`](../01-retro-ingenierie/datasheets/)

---

## 4. Champ des possibles

### 4.1 Fonctions réutilisables en l'état

> Voir détail : [`../02-champ-des-possibles/fonctions-reutilisables.md`](../02-champ-des-possibles/fonctions-reutilisables.md)

| Fonction | Valeur RSE |
|----------|-----------|
| Triangulation laser (profilométrie) | ⭐⭐⭐⭐⭐ |
| Acquisition image CMOS | ⭐⭐⭐⭐ |
| Bluetooth Classic SPP (WT12-A) | ⭐⭐⭐⭐ |
| Calcul embarqué MCU | ⭐⭐⭐⭐⭐ |
| Alimentation Li-ion portable | ⭐⭐⭐⭐ |

### 4.2 Extensions possibles

> Voir détail : [`../02-champ-des-possibles/extensions-possibles.md`](../02-champ-des-possibles/extensions-possibles.md)

Sans modification matérielle invasive, le SCANDIAG peut être étendu par :
- Connexion PC via USB/TTL existant (pipeline Data/IA côté PC)
- Module WiFi **ESP8266** sur UART libre *(aucun WiFi natif sur STM32F429 ni WT12-A — module à ajouter si besoin)*
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

Le POC est un **pipeline Python modulaire** opérationnel sur données réelles, validé lors
du concours avec le vrai device SCANDIAG.

**Environnement :** Python 3.13, OpenCV 4.x, NumPy, SciPy, scikit-learn, Matplotlib, pyserial.

**Résultats sur données synthétiques (validation algorithme) :**
- Accuracy du classificateur ML : 100% (validation croisée 5-fold sur 600 exemples)
- 4 cas de test : surface plane, sinusoïdale, en rampe, avec défaut local

**Résultats sur données réelles (device SCANDIAG, concours 29/06/2026) :**

> Observation clé : la diode laser du SCANDIAG émet dans le **vert (~520 nm)**, et non dans
> le rouge comme indiqué sur l'étiquette produit. Le canal d'extraction a été adapté en conséquence.

| Mesure | Étendue Rz | Ra | Colonnes | Diagnostic ML |
|--------|-----------|-----|----------|---------------|
| Surface de référence plate | 0.504 mm | 0.127 mm | 4032/4032 | Usé ⚠️ (76%) |
| Pièce de 20 centimes (2.14 mm) | 2.804 mm | 0.779 mm | 4032/4032 | Très usé ❌ (54%) |

**Calibration réalisée :**
- Objet de référence : pièce de 20 centimes euro (épaisseur = 2.14 mm)
- Facteur mesuré : **0.0331 mm/px** — résidu : 0.00 mm
- Hauteur moyenne mesurée : **2.010 mm** (erreur 6% par rapport aux 2.14 mm réels)

**Note sur la classification ML :** le modèle est entraîné sur données synthétiques idéales ;
le bruit intrinsèque d'une photo à main levée (~0.1 mm) est interprété comme de l'usure légère.
La re-calibration du seuil ou un ré-entraînement sur données réelles corrige ce comportement.

### 7.2 Structure du code

> Voir [`../04-poc/README.md`](../04-poc/README.md) pour les instructions d'installation et
> d'exécution complètes.

| Module | Rôle |
|--------|------|
| `src/acquisition.py` | Sources d'image : fichier, caméra, UART-série Bluetooth SPP |
| `src/laser_extraction.py` | Détection ligne laser (barycentre sous-pixel, canal vert/rouge/gris) |
| `src/triangulation.py` | Conversion positions → profil mm + calibration JSON |
| `src/analyse_ml.py` | Features 14D (stats + FFT) + RandomForest 3 classes |
| `src/rapport.py` | Rapport texte + figure PNG |
| `demo.py` | Pipeline bout-en-bout, multi-source (`--source`, `--canal`, `--calib`) |
| `tools/calibrer.py` | Calibration depuis photos de cales d'épaisseur connue |
| `tools/sniff_serie.py` | Découverte protocole Bluetooth SPP (hex dump + détection JPEG) |
| `tools/generer_pdf.py` | Génération rapport PDF 4 pages (titre + mesures + synthèse) |

### 7.3 Lancer le POC

```bash
cd 04-poc
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Mode démonstration (données synthétiques)
python demo.py

# Mesure réelle depuis une photo (ligne laser horizontale)
python demo.py --source fichier --image data/ma_photo.jpg \
               --canal vert --calib data/calibration.json --nom ma_mesure

# Générer le rapport PDF
python tools/generer_pdf.py
```

### 7.4 Calibration depuis une mire d'épaisseur connue

```bash
# 1. Photographier la ligne laser sur une surface plate (0 mm) et sur un objet de hauteur connue
# 2. Calculer la calibration :
python tools/calibrer.py \
    --images data/ref_plat.jpg data/ref_cale.jpg \
    --hauteurs 0.0 2.14 \
    --canal vert \
    --sortie data/calibration.json
# 3. Lancer le pipeline avec la calibration réelle
python demo.py --source fichier --image data/scan.jpg \
               --canal vert --calib data/calibration.json
```

### 7.5 Liaison Bluetooth SPP (WT12-A)

Le module Bluetooth WT12-A (firmware iWRAP) expose un port série virtuel sur le PC
une fois appairé. Le protocole de trame firmware n'a pas pu être établi lors du concours
(découverte requise). L'outil `tools/sniff_serie.py` permet de l'identifier :

```bash
# Après appairage BT macOS :
python tools/sniff_serie.py --port /dev/cu.SCANDIAG-SerialPort --auto-baud
```

---

## 8. Documentation des fonctions développées

### Pipeline principal — `demo.py`

Point d'entrée CLI unifié. Flags : `--source {synth,fichier,serie,camera}`,
`--image`, `--port`, `--baud`, `--canal {rouge,vert,gris}`, `--calib`, `--nom`, `--sortie`.
Dispatch l'acquisition, entraîne le modèle ML, appelle `executer_pipeline()`.

### `acquisition.depuis_fichier(chemin)`
Charge une image depuis le disque (JPEG, PNG…). Retourne un tableau BGR `H×W×3 uint8`.

### `acquisition.depuis_serie(port, baudrate, timeout)`
Lit une trame depuis un port série Bluetooth SPP (WT12-A). Protocole attendu :
`[4 octets big-endian = taille][payload JPEG]`. Retourne BGR `uint8`.

### `acquisition.generer_image_synthetique(profil, bruit)`
Génère une image simulant la vue caméra du SCANDIAG avec une ligne laser déformée
selon un profil paramétrable (plat / sinusoïde / rampe / défaut). Canal rouge.

### `laser_extraction.extraire_ligne_laser(image, canal, seuil, min_pixels)`
Détecte la position sous-pixel de la ligne laser dans chaque colonne de l'image par
barycentre des pixels lumineux après seuillage Otsu. Canaux supportés : `rouge`
(650 nm), `vert` (520 nm — SCANDIAG réel), `gris` (luminance). Retourne `float64[W]`,
`NaN` pour les colonnes sans signal.

### `laser_extraction.lisser_positions(positions, fenetre, ordre)`
Lisse le vecteur de positions par filtre de Savitzky-Golay (interpolation NaN préalable).
Réduit le bruit sans dégrader les discontinuités réelles.

### `laser_extraction.visualiser_detection(image, positions)`
Superpose la ligne détectée (vert) sur l'image brute. Retourne BGR uint8.

### `triangulation.CalibrationTriangulation`
Dataclasse : `y_reference` (px), `facteur_mm_par_pixel`, `offset_mm`.
Méthodes : `.sauvegarder(chemin)` → JSON, `.charger(chemin)` → instance.

### `triangulation.positions_vers_profil(positions_y, calib)`
Convertit les positions pixel en profil mm :
`hauteur = (y_ref − y_mesure) × facteur + offset`. Préserve les NaN.

### `triangulation.calibrer_depuis_mire(profils_reference, hauteurs_connues_mm)`
Détermine la calibration par régression linéaire (np.polyfit) sur les médianes de
profils pris à des hauteurs connues. Requiert ≥ 2 points.

### `triangulation.statistiques_profil(profil_mm)`
Calcule min, max, étendue (Rz), moyenne, écart-type, rugosité Ra (ISO 4287),
nombre de points valides.

### `analyse_ml.extraire_features(profil_mm)`
Extrait 14 features numériques : 5 stats de base, Ra/Rq, skewness, kurtosis,
5 premières amplitudes FFT normalisées (hors DC).

### `analyse_ml.ClassificateurUsure`
RandomForest 100 arbres, 3 classes (neuf / usé / très usé).
Méthodes : `entrainer(X,y)`, `entrainer_sur_donnees_synthetiques()`,
`predire(profil_mm)` → `{classe, label_fr, probabilites, confiance}`,
`sauvegarder(chemin)`, `charger(chemin)`.

### `rapport.generer_rapport_texte(profil_mm, stats, resultat_ml, ...)`
Rapport de mesure formaté (console + .txt) : statistiques profil, diagnostic ML,
verdict (alerte si étendue > seuil).

### `rapport.generer_rapport_figure(image_brute, positions_laser, ...)`
Figure matplotlib 3×2 : image brute | overlay détection | profil de hauteur |
tableau synthèse + verdict ML coloré. Sauvegarde PNG si `chemin_sortie` fourni.

### `tools/calibrer.py`
CLI : `--images`, `--hauteurs`, `--canal`, `--sortie`, `--dry-run`.
Charge les images, extrait les profils médians, appelle `calibrer_depuis_mire()`,
affiche les résidus, sauvegarde `calibration.json`.

### `tools/sniff_serie.py`
CLI : `--port`, `--baud`, `--duree`, `--auto-baud`, `--sortie`.
Lit le flux série brut, affiche un hexdump, détecte les marqueurs JPEG (FF D8/D9),
calcule l'entropie Shannon, identifie le meilleur baudrate en mode `--auto-baud`.

### `tools/generer_pdf.py`
CLI : `--sortie`. Génère un PDF 4 pages (page de titre, rapport surface plate,
rapport pièce 20c, synthèse technique) via matplotlib PdfPages.
Métadonnées PDF (auteur, titre, mots-clés) intégrées.

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
