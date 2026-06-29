#!/usr/bin/env python3
"""
tools/calibrer.py — Calibration du profilomètre depuis une mire d'épaisseur connue

Prend des photos de la ligne laser projetée sur des cales d'épaisseur connue,
extrait les positions médianes, et calcule les 3 paramètres de calibration :
  y_reference         — position Y laser sur surface plane de référence (pixels)
  facteur_mm_par_pixel — mm par pixel de déplacement vertical
  offset_mm           — décalage zéro (usually 0.0)

Sauvegarde le résultat dans calibration.json (utilisable via --calib de demo.py).

Utilisation :
    # 2 cales minimum (ex : 0 mm et 2 mm)
    python tools/calibrer.py \\
        --images data/ref_0mm.jpg data/ref_2mm.jpg \\
        --hauteurs 0.0 2.0 \\
        --sortie data/calibration.json

    # Vérification sans écrire :
    python tools/calibrer.py \\
        --images data/ref_0mm.jpg data/ref_2mm.jpg \\
        --hauteurs 0.0 2.0 \\
        --dry-run
"""

import argparse
import sys
from pathlib import Path

# Assurer que le module src est importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.acquisition import depuis_fichier
from src.laser_extraction import extraire_ligne_laser, lisser_positions
from src.triangulation import calibrer_depuis_mire, CalibrationTriangulation

import numpy as np


def extraire_profil_median(chemin_image: str, canal: str = "rouge") -> np.ndarray:
    """Charge une image et extrait la position laser lissée.

    Args:
        chemin_image: Chemin vers l'image (JPG, PNG…).
        canal: Canal couleur de la ligne laser ('rouge' par défaut pour 650 nm).

    Returns:
        Tableau 1D de positions Y sub-pixel (pixels), NaN pour les colonnes sans signal.
    """
    print(f"  Chargement : {chemin_image}")
    img = depuis_fichier(chemin_image)
    print(f"    → Image {img.shape[1]}×{img.shape[0]} px")

    positions = extraire_ligne_laser(img, canal=canal)
    positions = lisser_positions(positions, fenetre=11, ordre=2)

    n_valides = int((~np.isnan(positions)).sum())
    mediane = float(np.nanmedian(positions))
    print(f"    → {n_valides}/{len(positions)} colonnes détectées | médiane Y = {mediane:.2f} px")

    return positions


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Calibration du profilomètre ProfilScan depuis une mire d'épaisseur connue"
    )
    parser.add_argument(
        "--images",
        nargs="+",
        required=True,
        metavar="IMAGE",
        help="Images de calibration (une par hauteur connue, ordre correspondant à --hauteurs)",
    )
    parser.add_argument(
        "--hauteurs",
        nargs="+",
        type=float,
        required=True,
        metavar="MM",
        help="Hauteurs connues en mm pour chaque image (ex : 0.0 1.0 2.0)",
    )
    parser.add_argument(
        "--canal",
        choices=["rouge", "gris"],
        default="rouge",
        help="Canal couleur de la ligne laser (défaut : rouge pour 650 nm)",
    )
    parser.add_argument(
        "--sortie",
        type=str,
        default="data/calibration.json",
        help="Fichier JSON de calibration à écrire (défaut : data/calibration.json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Calculer sans écrire le fichier",
    )
    args = parser.parse_args()

    # ── Validation ───────────────────────────────────────────────────────────
    if len(args.images) != len(args.hauteurs):
        parser.error(f"Nombre d'images ({len(args.images)}) ≠ "
                     f"nombre de hauteurs ({len(args.hauteurs)})")
    if len(args.images) < 2:
        parser.error("Au moins 2 images de calibration sont nécessaires.")

    # ── Extraction des profils ───────────────────────────────────────────────
    print("\n═══════════════════════════════════════════════════")
    print("  Calibration ProfilScan — extraction des profils")
    print("═══════════════════════════════════════════════════\n")

    profils = []
    for chemin in args.images:
        profil = extraire_profil_median(chemin, canal=args.canal)
        profils.append(profil)

    # ── Calibration ─────────────────────────────────────────────────────────
    print(f"\n  Calcul de la calibration ({len(profils)} points de référence)...")

    try:
        calib = calibrer_depuis_mire(profils, args.hauteurs)
    except ValueError as e:
        print(f"\nERREUR calibration : {e}")
        sys.exit(1)

    # ── Résultat ─────────────────────────────────────────────────────────────
    print(f"\n  ┌─ Résultat ─────────────────────────────────────┐")
    print(f"  │  y_reference         = {calib.y_reference:10.3f} px             │")
    print(f"  │  facteur_mm_par_pixel = {calib.facteur_mm_par_pixel:9.4f} mm/px          │")
    print(f"  │  offset_mm            = {calib.offset_mm:10.4f} mm             │")
    print(f"  └────────────────────────────────────────────────┘")

    # ── Vérification (résidu) ────────────────────────────────────────────────
    print(f"\n  Vérification des résidus :")
    for i, (profil, h_ref) in enumerate(zip(profils, args.hauteurs)):
        mediane_px = float(np.nanmedian(profil))
        h_calculee = (calib.y_reference - mediane_px) * calib.facteur_mm_par_pixel + calib.offset_mm
        residus = h_calculee - h_ref
        print(f"    Image {i} ({args.images[i]}) : h_ref={h_ref:.3f} mm "
              f"→ h_calc={h_calculee:.3f} mm  (résidu={residus:+.4f} mm)")

    # ── Sauvegarde ───────────────────────────────────────────────────────────
    if not args.dry_run:
        chemin_sortie = Path(args.sortie)
        chemin_sortie.parent.mkdir(parents=True, exist_ok=True)
        calib.sauvegarder(str(chemin_sortie))
        print(f"\n  ✓ Calibration sauvegardée : {chemin_sortie.resolve()}")
    else:
        print("\n  (dry-run : fichier non écrit)")


if __name__ == "__main__":
    main()
