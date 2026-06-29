#!/usr/bin/env python3
"""
tools/generer_pdf.py — Génération du rapport PDF final ProfilScan

Assemble le rapport de rendu de la Phase 4 (POC Data/IA) :
  - Page de titre
  - Rapport mesure : surface de référence plate
  - Rapport mesure : pièce de 20 centimes (validation calibration)
  - Synthèse technique et perspectives

Utilisation :
    python tools/generer_pdf.py
    python tools/generer_pdf.py --sortie output/mon_rapport.pdf
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages

sys.path.insert(0, str(Path(__file__).parent.parent))

GITHUB_URL = "https://github.com/rsladky/Concours-Natio-IA-Data"
COULEUR_VERT  = "#2ecc71"
COULEUR_BLEU  = "#2c3e50"
COULEUR_GRIS  = "#ecf0f1"
COULEUR_ORANGE = "#e67e22"
COULEUR_ROUGE = "#e74c3c"


def page_titre(pdf: PdfPages) -> None:
    fig = plt.figure(figsize=(11.69, 8.27))  # A4 paysage
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")

    # Fond
    ax.add_patch(mpatches.FancyBboxPatch((0, 0), 1, 1, boxstyle="square",
                                         fc=COULEUR_BLEU, ec="none", zorder=0))
    # Bande verte
    ax.add_patch(mpatches.FancyBboxPatch((0, 0.35), 1, 0.005, boxstyle="square",
                                         fc=COULEUR_VERT, ec="none", zorder=1))

    ax.text(0.5, 0.88, "ProfilScan", ha="center", va="center",
            fontsize=48, fontweight="bold", color="white", zorder=2)
    ax.text(0.5, 0.76, "POC Phase 4 — Data / IA", ha="center", va="center",
            fontsize=22, color=COULEUR_VERT, zorder=2)
    ax.text(0.5, 0.67, "Réemploi RSE du FACOM SCANDIAG® (DX.TSCANPB)", ha="center",
            va="center", fontsize=15, color="#bdc3c7", zorder=2)

    ax.text(0.5, 0.54, "Concours National Informatique & Data — Ynov",
            ha="center", va="center", fontsize=13, color="white",
            style="italic", zorder=2)

    # Boîte récap
    ax.add_patch(mpatches.FancyBboxPatch((0.08, 0.10), 0.84, 0.25,
                                         boxstyle="round,pad=0.01",
                                         fc="#34495e", ec=COULEUR_VERT,
                                         linewidth=1.5, zorder=1))

    lignes = [
        ("Pipeline :", "Acquisition → Extraction laser → Triangulation → ML → Rapport"),
        ("Calibration :", "Pièce de 20 centimes (2.14 mm) — résidu 0.00 mm"),
        ("Mesure réelle :", "4032/4032 colonnes détectées — facteur 0.0331 mm/px"),
        ("Dépôt GitHub :", GITHUB_URL),
        ("Date :", date.today().strftime("%d %B %Y")),
    ]
    for i, (label, val) in enumerate(lignes):
        y = 0.30 - i * 0.044
        ax.text(0.13, y, label, ha="left", va="center", fontsize=9.5,
                color=COULEUR_VERT, fontweight="bold", zorder=2)
        ax.text(0.30, y, val, ha="left", va="center", fontsize=9.5,
                color="white", zorder=2,
                url=GITHUB_URL if "github" in val else None)

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def page_rapport_png(pdf: PdfPages, chemin_png: str, titre: str) -> None:
    if not Path(chemin_png).exists():
        print(f"  [ABSENT] {chemin_png} — page ignorée")
        return

    img = mpimg.imread(chemin_png)
    fig = plt.figure(figsize=(11.69, 8.27))
    ax_titre = fig.add_axes([0, 0.93, 1, 0.07])
    ax_titre.axis("off")
    ax_titre.text(0.5, 0.5, titre, ha="center", va="center",
                  fontsize=13, fontweight="bold", color=COULEUR_BLEU)

    ax_img = fig.add_axes([0.02, 0.01, 0.96, 0.91])
    ax_img.imshow(img)
    ax_img.axis("off")

    pdf.savefig(fig, bbox_inches="tight", dpi=150)
    plt.close(fig)


def page_synthese(pdf: PdfPages, chemin_calib: str) -> None:
    fig = plt.figure(figsize=(11.69, 8.27))
    fig.patch.set_facecolor(COULEUR_GRIS)

    # Titre
    ax_t = fig.add_axes([0, 0.88, 1, 0.12])
    ax_t.set_facecolor(COULEUR_BLEU); ax_t.axis("off")
    ax_t.text(0.5, 0.55, "Synthèse technique — ProfilScan", ha="center", va="center",
              fontsize=16, fontweight="bold", color="white")
    ax_t.text(0.5, 0.15, "Réemploi RSE FACOM SCANDIAG® (DX.TSCANPB) — Concours Ynov 2026",
              ha="center", va="center", fontsize=10, color=COULEUR_VERT)

    # Colonne gauche : paramètres calibration + résultats
    ax_l = fig.add_axes([0.03, 0.04, 0.44, 0.82])
    ax_l.set_facecolor("white"); ax_l.axis("off")
    ax_l.add_patch(mpatches.FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.02",
                                            fc="white", ec="#bdc3c7", linewidth=1))

    calib = {}
    if Path(chemin_calib).exists():
        with open(chemin_calib) as f:
            calib = json.load(f)

    def tl(ax, y, txt, fs=9.5, col="#2c3e50", bold=False, italic=False):
        ax.text(0.06, y, txt, ha="left", va="center", fontsize=fs, color=col,
                fontweight="bold" if bold else "normal",
                fontstyle="italic" if italic else "normal",
                transform=ax.transAxes)

    tl(ax_l, 0.93, "CALIBRATION", fs=11, col=COULEUR_BLEU, bold=True)
    tl(ax_l, 0.85, f"y_reference  = {calib.get('y_reference', 0):.1f} px")
    tl(ax_l, 0.79, f"facteur      = {calib.get('facteur_mm_par_pixel', 0):.4f} mm/px")
    tl(ax_l, 0.73, f"offset       = {calib.get('offset_mm', 0):.4f} mm")
    tl(ax_l, 0.67, "Objet : pièce 20 ct (2.14 mm)", col="#7f8c8d", italic=True)
    tl(ax_l, 0.61, "Résidu : 0.00 mm (2 points)", col="#7f8c8d", italic=True)

    tl(ax_l, 0.52, "RÉSULTATS MESURES RÉELLES", fs=11, col=COULEUR_BLEU, bold=True)
    tl(ax_l, 0.44, "Surface plate (référence)", fs=10, bold=True)
    tl(ax_l, 0.38, "  Étendue Rz : 0.504 mm")
    tl(ax_l, 0.32, "  Ra         : 0.127 mm")
    tl(ax_l, 0.26, "  Colonnes   : 4032 / 4032")
    tl(ax_l, 0.18, "Pièce de 20 centimes (validation)", fs=10, bold=True)
    tl(ax_l, 0.12, "  Étendue Rz : 2.804 mm")
    tl(ax_l, 0.06, "  Moyenne    : 2.010 mm  (réel 2.14 mm — erreur 6%)",
       col=COULEUR_VERT)
    tl(ax_l, 0.01, "  Colonnes   : 4032 / 4032")

    # Colonne droite : pipeline + limitations + github
    ax_r = fig.add_axes([0.53, 0.04, 0.44, 0.82])
    ax_r.set_facecolor("white"); ax_r.axis("off")
    ax_r.add_patch(mpatches.FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.02",
                                            fc="white", ec="#bdc3c7", linewidth=1))

    texte_r = [
        ("PIPELINE (5 étapes)", 0.93, 11, COULEUR_BLEU, "bold"),
        ("1. Acquisition image     depuis_fichier() / depuis_serie()", 0.86, 9, "#2c3e50", "normal"),
        ("2. Extraction laser      canal vert + seuil Otsu + barycentre", 0.80, 9, "#2c3e50", "normal"),
        ("3. Triangulation         pixels → mm via calibration.json", 0.74, 9, "#2c3e50", "normal"),
        ("4. Classification ML     RandomForest (neuf / usé / très usé)", 0.68, 9, "#2c3e50", "normal"),
        ("5. Rapport               texte + figure PNG + PDF", 0.62, 9, "#2c3e50", "normal"),
        ("LIMITATIONS & PERSPECTIVES", 0.53, 11, COULEUR_BLEU, "bold"),
        ("• Calibration 2 points : précision ±6% (améliorer avec 4+ points)", 0.46, 9, "#7f8c8d", "normal"),
        ("• Modèle ML entraîné sur données synthétiques → bruit réel", 0.40, 9, "#7f8c8d", "normal"),
        ("  classifié \"usé\" ; ré-entraîner sur données réelles.", 0.34, 9, "#7f8c8d", "normal"),
        ("• Liaison Bluetooth SPP (WT12-A iWRAP) non établie ; proto-", 0.28, 9, "#7f8c8d", "normal"),
        ("  cole firmware inconnu → chemin photo retenu pour le POC.", 0.22, 9, "#7f8c8d", "normal"),
        ("DÉPÔT GITHUB", 0.12, 11, COULEUR_BLEU, "bold"),
        (GITHUB_URL, 0.05, 9, COULEUR_VERT, "normal"),
    ]
    for txt, y, fs, col, fw in texte_r:
        ax_r.text(0.04, y, txt, ha="left", va="center", fontsize=fs,
                  color=col, fontweight=fw, transform=ax_r.transAxes)

    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Génère le rapport PDF final du POC ProfilScan"
    )
    parser.add_argument(
        "--sortie",
        default="output/rapport_final_ProfilScan.pdf",
        help="Chemin du PDF de sortie",
    )
    args = parser.parse_args()

    chemin_pdf = Path(args.sortie)
    chemin_pdf.parent.mkdir(parents=True, exist_ok=True)

    print(f"Génération du rapport PDF : {chemin_pdf}")

    with PdfPages(str(chemin_pdf)) as pdf:
        print("  [1/4] Page de titre...")
        page_titre(pdf)

        print("  [2/4] Rapport surface plate...")
        page_rapport_png(
            pdf,
            "output/rapport_ref_plat.png",
            "Mesure 1 — Surface de référence plate (Rz = 0.504 mm)",
        )

        print("  [3/4] Rapport pièce de 20 centimes...")
        page_rapport_png(
            pdf,
            "output/rapport_piece_20c.png",
            "Mesure 2 — Pièce de 20 centimes (validation calibration, h = 2.14 mm)",
        )

        print("  [4/4] Synthèse technique...")
        page_synthese(pdf, "data/calibration.json")

        info = pdf.infodict()
        info["Title"] = "ProfilScan — Rapport POC Phase 4 Data/IA"
        info["Author"] = "Robin Sladky — Concours National Informatique Ynov 2026"
        info["Subject"] = "Réemploi RSE FACOM SCANDIAG® (DX.TSCANPB)"
        info["Keywords"] = "profilométrie laser triangulation IA réemploi RSE"

    print(f"\n  PDF généré : {chemin_pdf.resolve()}")
    print(f"  Taille     : {chemin_pdf.stat().st_size / 1024:.0f} Ko")


if __name__ == "__main__":
    main()
