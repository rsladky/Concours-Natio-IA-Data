#!/usr/bin/env python3
"""
demo.py — Démonstration bout-en-bout du pipeline ProfilScan

Simule ou effectue une mesure complète du FACOM SCANDIAG :
  1. Acquisition de l'image (synthétique, fichier, série BT, ou caméra)
  2. Extraction de la ligne laser dans l'image
  3. Conversion des positions en profil de hauteur (mm)
  4. Classification de l'état de surface avec un modèle RandomForest
  5. Génération d'un rapport texte + figure PNG

Utilisation :
    # Mode synthétique (aucun matériel)
    python demo.py                              # 4 cas de test
    python demo.py --cas defaut                 # Un seul cas
    python demo.py --sortie ./output            # Dossier de sortie personnalisé

    # Photo réelle (ligne laser photographiée)
    python demo.py --source fichier --image data/scan_outil.jpg

    # Liaison Bluetooth SPP (WT12-A appairé)
    python demo.py --source serie --port /dev/cu.SCANDIAG-SerialPort

    # Caméra locale
    python demo.py --source camera

    # Avec calibration réelle
    python demo.py --source fichier --image data/scan.jpg --calib data/calibration.json

Découverte du protocole série avant utilisation :
    python tools/sniff_serie.py --port /dev/cu.SCANDIAG-SerialPort --auto-baud

Calibration depuis mire d'épaisseur connue :
    python tools/calibrer.py --images data/ref_0mm.jpg data/ref_2mm.jpg --hauteurs 0.0 2.0
"""

import argparse
import sys
from pathlib import Path

import numpy as np

# Assurer que le module src est importable depuis n'importe quel répertoire courant
sys.path.insert(0, str(Path(__file__).parent))

from src.acquisition import (
    generer_image_synthetique,
    depuis_fichier,
    depuis_serie,
    depuis_camera,
)
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

# Calibration par défaut (remplacée par --calib si fourni)
CALIBRATION_DEFAUT = CalibrationTriangulation(
    y_reference=240.0,            # Centre vertical de l'image 480 px
    facteur_mm_par_pixel=0.05,    # 0.05 mm/pixel (à mesurer avec une mire)
    offset_mm=0.0,
)

SEUIL_ALERTE_MM = 0.5  # Étendue max acceptable avant alerte


# ── Pipeline ─────────────────────────────────────────────────────────────────

def executer_pipeline(
    nom: str,
    calib: CalibrationTriangulation,
    classificateur: ClassificateurUsure,
    dossier_sortie: Path,
    image: np.ndarray | None = None,
) -> None:
    """Exécute le pipeline complet pour un cas de test ou une image réelle.

    Args:
        nom: Identifiant du cas (profil synthétique ou nom de fichier/mesure).
             Doit être un nom de fichier valide (utilisé pour les sorties).
        calib: Paramètres de calibration triangulation.
        classificateur: Modèle ML entraîné.
        dossier_sortie: Dossier où sauvegarder les rapports.
        image: Image BGR (np.ndarray H×W×3 uint8) pré-acquise, ou None pour
               générer une image synthétique basée sur `nom` comme profil.
    """
    est_synthetique = (image is None)
    nom_surface = f"Simulation — {nom}" if est_synthetique else nom

    print(f"\n{'─' * 60}")
    print(f"  {'CAS' if est_synthetique else 'MESURE'} : {nom.upper()}")
    print(f"{'─' * 60}")

    # ── Étape 1 : Acquisition ────────────────────────────────────────────
    if est_synthetique:
        print("[1/5] Génération de l'image synthétique...")
        image = generer_image_synthetique(profil=nom, bruit=1.5)
        print(f"      → Image {image.shape[1]}×{image.shape[0]} px générée (profil={nom})")
    else:
        print(f"[1/5] Image fournie ({image.shape[1]}×{image.shape[0]} px)")

    # ── Étape 2 : Extraction de la ligne laser ───────────────────────────
    print("[2/5] Extraction de la ligne laser...")
    positions_brutes = extraire_ligne_laser(image, canal="rouge")
    positions = lisser_positions(positions_brutes, fenetre=11, ordre=2)
    n_valides = int((~np.isnan(positions)).sum())
    print(f"      → {n_valides}/{len(positions)} colonnes détectées")
    if n_valides < len(positions) * 0.5:
        print(f"      ⚠  Moins de 50 % des colonnes détectées — vérifier "
              f"l'éclairage ou essayer canal='gris'")

    # ── Étape 3 : Triangulation → profil mm ─────────────────────────────
    print("[3/5] Conversion en profil de hauteur (mm)...")
    profil_mm = positions_vers_profil(positions, calib)
    stats = statistiques_profil(profil_mm)
    print(f"      → Étendue (Rz) : {stats['etendue']:.3f} mm | Ra : {stats['Ra']:.3f} mm")

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
        nom_surface=nom_surface,
        seuil_alerte_mm=SEUIL_ALERTE_MM,
    )
    print("\n" + rapport_txt)

    chemin_txt = dossier_sortie / f"rapport_{nom}.txt"
    chemin_txt.write_text(rapport_txt, encoding="utf-8")
    print(f"\n      → Rapport texte sauvegardé : {chemin_txt}")

    # Rapport figure PNG
    chemin_png = dossier_sortie / f"rapport_{nom}.png"
    fig = generer_rapport_figure(
        image_brute=image,
        positions_laser=positions,
        profil_mm=profil_mm,
        stats=stats,
        resultat_ml=resultat,
        nom_surface=nom_surface,
        chemin_sortie=chemin_png,
    )
    import matplotlib.pyplot as plt
    plt.close(fig)
    print(f"      → Rapport graphique sauvegardé : {chemin_png}")


# ── Point d'entrée ───────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="ProfilScan — Pipeline Data/IA de profilomètre laser (FACOM SCANDIAG réemploi)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples :
  python demo.py                                                # données synthétiques (4 cas)
  python demo.py --source fichier --image data/scan.jpg        # photo réelle
  python demo.py --source serie   --port /dev/cu.SCANDIAG-xxx  # liaison Bluetooth SPP
  python demo.py --source fichier --image data/scan.jpg \\
                 --calib data/calibration.json                 # avec vraie calibration
        """,
    )
    parser.add_argument(
        "--source",
        choices=["synth", "fichier", "serie", "camera"],
        default="synth",
        help="Source d'acquisition : synth (défaut), fichier, serie, camera",
    )
    # Options synthétiques
    parser.add_argument(
        "--cas",
        choices=CAS_TEST + ["tous"],
        default="tous",
        help="[--source synth] Cas de test à exécuter (défaut : tous)",
    )
    # Options source fichier
    parser.add_argument(
        "--image",
        type=str,
        default=None,
        help="[--source fichier] Chemin vers l'image à analyser",
    )
    # Options source série
    parser.add_argument(
        "--port",
        type=str,
        default=None,
        help="[--source serie] Port série, ex. /dev/cu.SCANDIAG-SerialPort",
    )
    parser.add_argument(
        "--baud",
        type=int,
        default=115200,
        help="[--source serie] Baudrate (défaut : 115200)",
    )
    # Options source caméra
    parser.add_argument(
        "--index-camera",
        type=int,
        default=0,
        help="[--source camera] Index de la caméra OpenCV (défaut : 0)",
    )
    # Options communes
    parser.add_argument(
        "--calib",
        type=str,
        default=None,
        help="Fichier calibration.json (si absent : calibration par défaut)",
    )
    parser.add_argument(
        "--nom",
        type=str,
        default=None,
        help="Nom de la mesure pour les rapports (auto-détecté sinon)",
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
    print("  ProfilScan — Pipeline Data/IA")
    print("  Réemploi RSE du FACOM SCANDIAG® (DX.TSCANPB)")
    print("  Concours National Informatique Ynov")
    print("=" * 60)

    # ── Calibration ──────────────────────────────────────────────────────────
    if args.calib:
        try:
            calib = CalibrationTriangulation.charger(args.calib)
            print(f"\n[INIT] Calibration chargée depuis {args.calib}")
            print(f"       y_ref={calib.y_reference:.1f} px | "
                  f"facteur={calib.facteur_mm_par_pixel:.4f} mm/px | "
                  f"offset={calib.offset_mm:.4f} mm")
        except (FileNotFoundError, KeyError) as e:
            print(f"ERREUR : impossible de charger {args.calib} : {e}")
            sys.exit(1)
    else:
        calib = CALIBRATION_DEFAUT
        print("\n[INIT] Calibration par défaut (facteur=0.05 mm/px — à remplacer par --calib)")

    # ── Entraînement du modèle ML (une seule fois) ───────────────────────────
    print("\n[INIT] Entraînement du classificateur ML sur données synthétiques...")
    clf = ClassificateurUsure()
    metriques = clf.entrainer_sur_donnees_synthetiques(n_par_classe=200)
    print(f"       → Accuracy CV : {metriques['accuracy_cv_mean'] * 100:.1f}%"
          f" ± {metriques['accuracy_cv_std'] * 100:.1f}%")

    chemin_modele = dossier_sortie / "modele_usure.pkl"
    clf.sauvegarder(str(chemin_modele))
    print(f"       → Modèle sauvegardé : {chemin_modele}")

    # ── Dispatch selon --source ───────────────────────────────────────────────
    if args.source == "synth":
        # Mode synthétique : itérer sur les cas demandés
        cas_a_executer = CAS_TEST if args.cas == "tous" else [args.cas]
        for cas in cas_a_executer:
            executer_pipeline(
                nom=cas,
                calib=calib,
                classificateur=clf,
                dossier_sortie=dossier_sortie,
                image=None,
            )

    elif args.source == "fichier":
        if not args.image:
            parser.error("--source fichier requiert --image <chemin>")
        print(f"\n[ACQU] Chargement de l'image : {args.image}")
        image = depuis_fichier(args.image)
        print(f"       → {image.shape[1]}×{image.shape[0]} px")
        nom = args.nom or Path(args.image).stem
        executer_pipeline(
            nom=nom,
            calib=calib,
            classificateur=clf,
            dossier_sortie=dossier_sortie,
            image=image,
        )

    elif args.source == "serie":
        if not args.port:
            parser.error(
                "--source serie requiert --port <port>\n"
                "Astuce : ls /dev/cu.* pour trouver le port après appairage BT.\n"
                "Découverte : python tools/sniff_serie.py --port <port> --auto-baud"
            )
        print(f"\n[ACQU] Acquisition série : {args.port} @ {args.baud} baud")
        image = depuis_serie(args.port, baudrate=args.baud)
        print(f"       → Image {image.shape[1]}×{image.shape[0]} px reçue")
        nom = args.nom or "scandiag_reel"
        executer_pipeline(
            nom=nom,
            calib=calib,
            classificateur=clf,
            dossier_sortie=dossier_sortie,
            image=image,
        )

    elif args.source == "camera":
        print(f"\n[ACQU] Capture caméra (index={args.index_camera})...")
        image = depuis_camera(index=args.index_camera)
        print(f"       → {image.shape[1]}×{image.shape[0]} px capturée")
        nom = args.nom or "camera_reel"
        executer_pipeline(
            nom=nom,
            calib=calib,
            classificateur=clf,
            dossier_sortie=dossier_sortie,
            image=image,
        )

    print(f"\n{'=' * 60}")
    print(f"  Terminé. Sorties dans : {dossier_sortie.resolve()}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
