"""
laser_extraction.py — Détection de la ligne laser dans une image caméra

Algorithme :
  1. Convertir en niveaux de gris (ou isoler le canal rouge pour laser rouge).
  2. Appliquer un seuillage adaptatif pour isoler la ligne laser.
  3. Pour chaque colonne, calculer le **barycentre** (centre de masse) des pixels
     lumineux → position sous-pixel de la ligne (précision améliorée vs max).
  4. Retourner le tableau de positions Y par colonne.
"""

import cv2
import numpy as np


def extraire_ligne_laser(
    image: np.ndarray,
    canal: str = "rouge",
    seuil: int | None = None,
    min_pixels: int = 3,
) -> np.ndarray:
    """Détecte la position sous-pixel de la ligne laser pour chaque colonne.

    Args:
        image: Image BGR uint8 (H x W x 3).
        canal: Canal à utiliser pour la détection :
            - 'rouge' : canal R de l'image BGR (optimal pour laser rouge 650 nm)
            - 'gris'  : luminance (utile si le laser est blanc ou vert)
        seuil: Seuil de binarisation (0–255). Si None, utilise Otsu automatiquement.
        min_pixels: Nombre minimum de pixels lumineux par colonne pour valider la détection.
            Les colonnes avec moins de pixels sont marquées NaN.

    Returns:
        Tableau float64 de longueur W : position Y (en pixels, sous-pixel) de la ligne
        pour chaque colonne. Valeur NaN si la détection échoue pour une colonne.
    """
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("L'image doit être BGR (H x W x 3)")

    # Extraire le canal pertinent
    if canal == "rouge":
        # Le canal rouge (indice 2 en BGR) capte mieux un laser 650 nm rouge
        canal_img = image[:, :, 2].astype(np.float32)
        # Soustraire les autres canaux pour réduire le fond coloré
        fond = image[:, :, 0].astype(np.float32) * 0.5 + image[:, :, 1].astype(np.float32) * 0.5
        canal_img = np.clip(canal_img - fond, 0, 255).astype(np.uint8)
    elif canal == "gris":
        canal_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        raise ValueError(f"Canal inconnu : '{canal}'. Choisir 'rouge' ou 'gris'.")

    # Seuillage
    if seuil is None:
        # Otsu détermine le seuil optimal automatiquement
        _, binaire = cv2.threshold(canal_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    else:
        _, binaire = cv2.threshold(canal_img, seuil, 255, cv2.THRESH_BINARY)

    H, W = canal_img.shape
    positions = np.full(W, np.nan)  # NaN par défaut (colonne non détectée)

    intensites = canal_img.astype(float)
    y_indices = np.arange(H, dtype=float)

    for col in range(W):
        colonne = intensites[:, col] * (binaire[:, col] / 255.0)
        somme = colonne.sum()

        if somme < min_pixels * 10:  # Seuil minimal d'énergie
            continue  # Colonne sans signal suffisant → NaN

        # Barycentre (centre de masse) = position sous-pixel
        positions[col] = (y_indices * colonne).sum() / somme

    return positions


def lisser_positions(
    positions: np.ndarray,
    fenetre: int = 7,
    ordre: int = 2,
) -> np.ndarray:
    """Lisse le profil de positions par un filtre de Savitzky-Golay.

    Réduit le bruit de mesure tout en préservant les discontinuités réelles
    (défauts de surface).

    Args:
        positions: Tableau de positions Y (peut contenir des NaN).
        fenetre: Largeur de la fenêtre de lissage (doit être impair).
        ordre: Ordre du polynôme de lissage (typiquement 2 ou 3).

    Returns:
        Tableau de positions lissées (NaN aux mêmes endroits que l'entrée).
    """
    from scipy.signal import savgol_filter

    if fenetre % 2 == 0:
        fenetre += 1  # Savitzky-Golay requiert une fenêtre impaire

    lisse = positions.copy()
    valides = ~np.isnan(positions)

    if valides.sum() < fenetre:
        return lisse  # Pas assez de points valides

    # Interpoler les NaN pour appliquer le filtre sur une séquence continue
    x = np.arange(len(positions))
    interpolee = np.interp(x, x[valides], positions[valides])

    lissee = savgol_filter(interpolee, window_length=fenetre, polyorder=ordre)
    lisse[valides] = lissee[valides]

    return lisse


def visualiser_detection(
    image: np.ndarray,
    positions: np.ndarray,
    couleur: tuple[int, int, int] = (0, 255, 0),
    epaisseur: int = 2,
) -> np.ndarray:
    """Superpose la ligne détectée sur l'image originale pour vérification visuelle.

    Args:
        image: Image BGR originale.
        positions: Tableau de positions Y de la ligne.
        couleur: Couleur de la ligne superposée (BGR).
        epaisseur: Épaisseur de la ligne en pixels.

    Returns:
        Image BGR avec la ligne laser détectée superposée en vert (ou couleur choisie).
    """
    visu = image.copy()
    W = len(positions)
    H = image.shape[0]

    pts_valides = [
        (int(col), int(round(positions[col])))
        for col in range(W)
        if not np.isnan(positions[col]) and 0 <= positions[col] < H
    ]

    for i in range(1, len(pts_valides)):
        cv2.line(visu, pts_valides[i - 1], pts_valides[i], couleur, epaisseur)

    return visu
