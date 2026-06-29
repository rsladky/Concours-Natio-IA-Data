#!/usr/bin/env python3
"""
demo.py — Démonstration bout-en-bout du pipeline ProfilScan

Simule une mesure complète sans le matériel physique :
  1. Génère des images synthétiques simulant la vue caméra du SCANDIAG
  2. Extrait la ligne laser dans chaque image
  3. Convertit les positions en profil de hauteur (mm)
  4. Classifie l'état de surface avec un modèle RandomForest
  5. Génère un rapport texte + une figure PNG

Utilisation :
    python demo.py                   # 4 cas de test (plat, sinusoide, rampe, defaut)
    python demo.py --cas defaut      # Un seul cas
    python demo.py --sortie ./output # Dossier de sortie personnalisé

Le jour J : remplacer generer_image_synthetique() par depuis_fichier() ou depuis_serie()
             dans acquisition.py pour brancher le vrai device SCANDIAG.
"""

import argparse
import sys
from pathlib import Path

# Assurer que le module src est importable depuis n'importe quel répertoire courant
sys.path.insert(0, str(Path(__file__).parent))

from src.acquisition import generer_image_synthetique
from src.laser_extraction import extraire_ligne_laser, lisser_positions, visualiser_detection
from src.triangulation import (
    CalibrationTriangulation,
    positions_vers_profil,
    statistiques_profil,
)
from src.analyse_ml import ClassificateurUsure
from src.rapport import generer_rapport_texte, generer_rapport_figure


# ── Configuration ────────────────────────────────────────────────────────────

CAS_TEST = ["plat", "sinusoide", "rampe", "defaut"]

# Calibration par défaut (à remplacer par la vraie calibration le jour J)
CALIBRATION_DEFAUT = CalibrationTriangulation(
    y_reference=240.0,       # Centre vertical de l'image 480px
    facteur_mm_par_pixel=0.05,  # 0.05 mm/pixel (à mesurer avec une mire)
    offset_mm=0.0,
)

SEUIL_ALERTE_MM = 0.5  # Étendue max acceptable avant alerte


# ── Pipeline ─────────────────────────────────────────────────────────────────

def executer_pipeline(
    cas: str,
    calib: CalibrationTriangulation,
    classificateur: ClassificateurUsure,
    dossier_sortie: Path,
) -> None:
    """Exécute le pipeline complet pour un cas de test.

    Args:
        cas: Type de profil synthétique ('plat', 'sinusoide', 'rampe', 'defaut').
        calib: Paramètres de calibration.
        classificateur: Modèle ML entraîné.
        dossier_sortie: Dossier où sauvegarder les sorties.
    """
    print(f"\n{'─' * 50}")
    print(f"  CAS : {cas.upper()}")
    print(f"{'─' * 50}")

    # ── Étape 1 : Acquisition (synthétique) ─────────────────────────────
    print("[1/5] Génération de l'image synthétique...")
    image = generer_image_synthetique(profil=cas, bruit=1.5)
    print(f"      → Image {image.shape[1]}×{image.shape[0]} px générée")

    # ── Étape 2 : Extraction de la ligne laser ───────────────────────────
    print("[2/5] Extraction de la ligne laser...")
    positions_brutes = extraire_ligne_laser(image, canal="rouge")
    positions = lisser_positions(positions_brutes, fenetre=11, ordre=2)
    n_valides = int((~__import__("numpy").isnan(positions)).sum())
    print(f"      → {n_valides}/{len(positions)} colonnes détectées")

    # ── Étape 3 : Triangulation → profil mm ─────────────────────────────
    print("[3/5] Conversion en profil de hauteur (mm)...")
    profil_mm = positions_vers_profil(positions, calib)
    stats = statistiques_profil(profil_mm)
    print(f"      → Étendue : {stats['etendue']:.3f} mm | Ra : {stats['Ra']:.3f} mm")

    # ── Étape 4 : Classification ML ──────────────────────────────────────
    print("[4/5] Classification de l'état de surface...")
    resultat = classificateur.predire(profil_mm)
    print(f"      → {resultat['label_fr']} (confiance : {resultat['confiance'] * 100:.0f}%)")

    # ── Étape 5 : Rapport ────────────────────────────────────────────────
    print("[5/5] Génération du rapport...")

    # Rapport texte
    rapport_txt = generer_rapport_texte(
        profil_mm=profil_mm,
        stats=stats,
        resultat_ml=resultat,
        nom_surface=f"Simulation — {cas}",
        seuil_alerte_mm=SEUIL_ALERTE_MM,
    )
    print("\n" + rapport_txt)

    # Sauvegarder le rapport texte
    chemin_txt = dossier_sortie / f"rapport_{cas}.txt"
    chemin_txt.write_text(rapport_txt, encoding="utf-8")
    print(f"\n      → Rapport texte sauvegardé : {chemin_txt}")

    # Rapport figure PNG
    image_visu = visualiser_detection(image, positions)
    chemin_png = dossier_sortie / f"rapport_{cas}.png"
    fig = generer_rapport_figure(
        image_brute=image,
        positions_laser=positions,
        profil_mm=profil_mm,
        stats=stats,
        resultat_ml=resultat,
        nom_surface=f"Simulation — {cas}",
        chemin_sortie=chemin_png,
    )
    import matplotlib.pyplot as plt
    plt.close(fig)
    print(f"      → Rapport graphique sauvegardé : {chemin_png}")


# ── Point d'entrée ───────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Démo ProfilScan — Pipeline Data/IA de profilomètre laser (FACOM SCANDIAG réemploi)"
    )
    parser.add_argument(
        "--cas",
        choices=CAS_TEST + ["tous"],
        default="tous",
        help="Cas de test à exécuter (défaut : tous)",
    )
    parser.add_argument(
        "--sortie",
        type=str,
        default="./output",
        help="Dossier de sortie pour les rapports (défaut : ./output)",
    )
    args = parser.parse_args()

    dossier_sortie = Path(args.sortie)
    dossier_sortie.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("  ProfilScan — Démo pipeline Data/IA")
    print("  Réemploi RSE du FACOM SCANDIAG® (DX.TSCANPB)")
    print("  Concours National Informatique Ynov")
    print("=" * 60)

    # ── Entraînement du modèle ML (une seule fois) ───────────────────────
    print("\n[INIT] Entraînement du classificateur ML sur données synthétiques...")
    clf = ClassificateurUsure()
    metriques = clf.entrainer_sur_donnees_synthetiques(n_par_classe=200)
    print(f"       → Accuracy CV : {metriques['accuracy_cv_mean'] * 100:.1f}%"
          f" ± {metriques['accuracy_cv_std'] * 100:.1f}%")

    # Sauvegarder le modèle entraîné
    chemin_modele = dossier_sortie / "modele_usure.pkl"
    clf.sauvegarder(str(chemin_modele))
    print(f"       → Modèle sauvegardé : {chemin_modele}")

    # ── Exécuter les cas ─────────────────────────────────────────────────
    cas_a_executer = CAS_TEST if args.cas == "tous" else [args.cas]

    for cas in cas_a_executer:
        executer_pipeline(
            cas=cas,
            calib=CALIBRATION_DEFAUT,
            classificateur=clf,
            dossier_sortie=dossier_sortie,
        )

    print(f"\n{'=' * 60}")
    print(f"  Démo terminée. Sorties dans : {dossier_sortie.resolve()}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
