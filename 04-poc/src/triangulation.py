"""
triangulation.py — Conversion positions laser → profil de hauteur

Principe de triangulation laser (lumière structurée) :
  - Une ligne laser est projetée sous un angle θ par rapport à l'axe de la caméra.
  - Quand la surface s'élève, la ligne se déplace vers le haut dans l'image.
  - La relation hauteur ↔ déplacement pixel est linéaire pour une géométrie fixe :

        h = (y_ref - y_mesure) × facteur_calibration

  où facteur_calibration = distance_de_travail / (focale_px × tan(θ))

Le facteur peut être déterminé expérimentalement avec une mire de calibration.
"""

import numpy as np
from dataclasses import dataclass, field


@dataclass
class CalibrationTriangulation:
    """Paramètres de calibration du scanner laser.

    Attributes:
        y_reference: Position Y de la ligne laser sur une surface plane de référence (pixels).
        facteur_mm_par_pixel: Conversion (mm par pixel de déplacement vertical).
            Par défaut estimé à 0.05 mm/pixel (à mesurer expérimentalement).
        offset_mm: Décalage zéro en mm (optionnel, pour corriger l'origine).
    """
    y_reference: float = 240.0          # Centre de l'image (480px / 2) par défaut
    facteur_mm_par_pixel: float = 0.05  # À calibrer avec une mire graduée
    offset_mm: float = 0.0

    def sauvegarder(self, chemin: str) -> None:
        """Sauvegarde la calibration dans un fichier texte simple."""
        import json
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump({
                "y_reference": self.y_reference,
                "facteur_mm_par_pixel": self.facteur_mm_par_pixel,
                "offset_mm": self.offset_mm,
            }, f, indent=2)

    @classmethod
    def charger(cls, chemin: str) -> "CalibrationTriangulation":
        """Charge une calibration depuis un fichier JSON."""
        import json
        with open(chemin, encoding="utf-8") as f:
            donnees = json.load(f)
        return cls(**donnees)


def positions_vers_profil(
    positions_y: np.ndarray,
    calib: CalibrationTriangulation,
) -> np.ndarray:
    """Convertit les positions Y de la ligne laser en profil de hauteur (mm).

    Args:
        positions_y: Tableau float64 de positions Y par colonne (peut contenir NaN).
        calib: Paramètres de calibration.

    Returns:
        Tableau float64 de hauteurs en mm par colonne.
        Valeur NaN là où la détection a échoué.
    """
    # Déplacement en pixels par rapport à la référence
    # Signe : si y_mesure < y_ref → la surface est plus haute (ligne remonte dans l'image)
    deplacement_px = calib.y_reference - positions_y

    # Conversion en mm + offset
    hauteur_mm = deplacement_px * calib.facteur_mm_par_pixel + calib.offset_mm

    return hauteur_mm


def calibrer_depuis_mire(
    profils_reference: list[np.ndarray],
    hauteurs_connues_mm: list[float],
) -> CalibrationTriangulation:
    """Détermine le facteur de calibration à partir de mesures sur une mire.

    Protocole :
      1. Placer des cales d'épaisseur connue devant le scanner.
      2. Acquérir un profil pour chaque hauteur de cale.
      3. Passer ces profils ici → la calibration est calculée par régression linéaire.

    Args:
        profils_reference: Liste de tableaux de positions Y (un par cale).
        hauteurs_connues_mm: Hauteurs réelles correspondantes en mm.

    Returns:
        CalibrationTriangulation avec y_reference et facteur calculés.
    """
    if len(profils_reference) != len(hauteurs_connues_mm):
        raise ValueError("Nombre de profils et de hauteurs connues différents")
    if len(profils_reference) < 2:
        raise ValueError("Au moins 2 points de calibration nécessaires")

    # Médiane de chaque profil comme position de référence pour ce niveau
    medianes_px = [float(np.nanmedian(p)) for p in profils_reference]

    # Régression linéaire : hauteur_mm = a × pixel_y + b
    # → facteur = −a (le signe dépend de la convention choisie)
    x = np.array(medianes_px)
    y = np.array(hauteurs_connues_mm, dtype=float)

    coeffs = np.polyfit(x, y, 1)
    pente = coeffs[0]       # mm par pixel
    intercept = coeffs[1]   # mm à y=0

    # y_reference = position Y correspondant à hauteur = 0
    y_ref = -intercept / pente if pente != 0 else medianes_px[0]

    return CalibrationTriangulation(
        y_reference=float(y_ref),
        facteur_mm_par_pixel=float(-pente),  # Négatif car la ligne monte quand la surface monte
        offset_mm=0.0,
    )


def statistiques_profil(profil_mm: np.ndarray) -> dict:
    """Calcule les statistiques descriptives d'un profil.

    Returns:
        Dictionnaire avec : min, max, etendue, moyenne, ecart_type,
        rugosité Ra (moyenne des écarts à la moyenne), n_points_valides.
    """
    valides = profil_mm[~np.isnan(profil_mm)]
    if len(valides) == 0:
        return {k: float("nan") for k in
                ["min", "max", "etendue", "moyenne", "ecart_type", "Ra", "n_points_valides"]}

    moyenne = float(np.mean(valides))
    return {
        "min": float(np.min(valides)),
        "max": float(np.max(valides)),
        "etendue": float(np.max(valides) - np.min(valides)),
        "moyenne": moyenne,
        "ecart_type": float(np.std(valides)),
        "Ra": float(np.mean(np.abs(valides - moyenne))),  # Rugosité arithmétique ISO 4287
        "n_points_valides": int(len(valides)),
    }
