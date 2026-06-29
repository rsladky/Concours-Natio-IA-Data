# POC — ProfilScan : pipeline Data/IA de profilomètre laser

> **Concept :** réemployer la chaîne caméra + ligne laser du FACOM SCANDIAG® (DX.TSCANPB)
> comme **profilomètre / scanner 3D open-source** alimentant un pipeline Data/IA.

---

## Architecture du pipeline

```
Image caméra (JPEG/PNG/série)
         │
         ▼
┌──────────────────┐
│  acquisition.py  │  ← fichier | caméra | UART/USB-TTL (device réel)
└────────┬─────────┘
         │ np.ndarray BGR
         ▼
┌───────────────────────┐
│  laser_extraction.py  │  ← seuillage + barycentre sous-pixel par colonne
└────────┬──────────────┘
         │ positions_y[W]  (pixels)
         ▼
┌──────────────────────┐
│  triangulation.py    │  ← conversion pixels → mm (calibration)
└────────┬─────────────┘
         │ profil_mm[W]
         ▼
┌──────────────────┐
│  analyse_ml.py   │  ← features (stats + FFT) → RandomForest → classe d'usure
└────────┬─────────┘
         │ {'classe': 'use', 'confiance': 0.87, ...}
         ▼
┌──────────────┐
│  rapport.py  │  ← texte console + figure PNG (profil + diagnostic)
└──────────────┘
```

---

## Installation

```bash
# Depuis le dossier 04-poc/
python -m venv .venv
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate       # Windows

pip install -r requirements.txt
```

---

## Lancer la démo

```bash
# Pipeline complet sur 4 cas de test synthétiques
python demo.py

# Un seul cas
python demo.py --cas defaut

# Dossier de sortie personnalisé
python demo.py --sortie ./mes-sorties
```

**Sorties générées** dans `./output/` :
- `rapport_<cas>.txt` — rapport de mesure texte
- `rapport_<cas>.png` — figure avec image + profil + diagnostic ML
- `modele_usure.pkl` — classificateur entraîné

---

## Brancher le vrai device SCANDIAG (jour J)

Dans `demo.py`, remplacer la ligne :

```python
image = generer_image_synthetique(profil=cas, bruit=1.5)
```

par l'une de ces alternatives :

```python
# Depuis un fichier photo pris avec le SCANDIAG
image = depuis_fichier("chemin/vers/image.jpg")

# Depuis la caméra USB du device (si redirigée)
image = depuis_camera(index=0)

# Depuis le port série (UART → USB/TTL)
image = depuis_serie(port="/dev/cu.usbserial-0001", baudrate=115200)
```

---

## Calibration (jour J)

La calibration convertit les pixels en millimètres réels :

1. Placer des **cales d'épaisseur connue** (ex. 0 mm, 1 mm, 2 mm, 5 mm) devant le scanner.
2. Acquérir un profil pour chaque cale.
3. Appeler `calibrer_depuis_mire()` dans `triangulation.py`.
4. Sauvegarder la calibration et la réutiliser :

```python
from src.triangulation import calibrer_depuis_mire, CalibrationTriangulation

calib = calibrer_depuis_mire(profils_reference=[...], hauteurs_connues_mm=[0, 1, 2, 5])
calib.sauvegarder("calibration.json")

# Réutilisation
calib = CalibrationTriangulation.charger("calibration.json")
```

---

## Structure des fichiers

```
04-poc/
├── demo.py                 # Point d'entrée — pipeline complet
├── requirements.txt        # Dépendances Python
├── README.md               # Ce fichier
├── src/
│   ├── __init__.py
│   ├── acquisition.py      # Sources d'image (fichier / caméra / série)
│   ├── laser_extraction.py # Détection de la ligne laser (barycentre sous-pixel)
│   ├── triangulation.py    # Conversion positions → profil mm + calibration
│   ├── analyse_ml.py       # Features + RandomForest pour classification d'usure
│   └── rapport.py          # Rapport texte + figure matplotlib
├── data/                   # Images exemples (à ajouter le jour J)
└── output/                 # Sorties de la démo (générées au runtime)
```

---

## Dépendances

| Bibliothèque | Usage |
|---|---|
| `opencv-python` | Lecture image, seuillage, dessin |
| `numpy` | Calcul vectoriel (barycentre, profil, features) |
| `scipy` | Filtre Savitzky-Golay (lissage du profil) |
| `scikit-learn` | RandomForest, validation croisée |
| `matplotlib` | Génération de la figure de rapport |

---

## Extension matérielle prévue

Pour un déploiement embarqué autonome (sans PC) :

| Composant ajouté | Rôle | Connexion |
|---|---|---|
| Raspberry Pi Zero 2W | Calcul Python + WiFi | USB/TTL UART |
| Écran OLED SSD1306 | Affichage résultat | I²C |
| Module WiFi (intégré RPi) | Envoi rapport cloud | — |
