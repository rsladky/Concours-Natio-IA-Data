"""
rapport.py — Génération d'un rapport de mesure ProfilScan

Le rapport reproduit l'esprit du rapport SCANDIAG d'origine (restitution claire de la mesure)
mais dans un contexte de profilomètre générique.

Sorties possibles :
  - Rapport texte (console / fichier .txt)
  - Figure matplotlib (profil + diagnostic) sauvegardable en PNG
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")  # Mode non-interactif (pas besoin d'écran pour les tests)
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from datetime import datetime
from pathlib import Path


# ── Rapport textuel ──────────────────────────────────────────────────────────

def generer_rapport_texte(
    profil_mm: np.ndarray,
    stats: dict,
    resultat_ml: dict,
    nom_surface: str = "Surface",
    seuil_alerte_mm: float = 0.5,
) -> str:
    """Génère un rapport de mesure en texte structuré.

    Args:
        profil_mm: Profil de hauteur en mm.
        stats: Dictionnaire de statistiques (depuis triangulation.statistiques_profil).
        resultat_ml: Dictionnaire de résultat (depuis ClassificateurUsure.predire).
        nom_surface: Nom de la surface mesurée.
        seuil_alerte_mm: Seuil d'étendue au-delà duquel une alerte est émise.

    Returns:
        Rapport formaté en chaîne de caractères.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    alerte = stats["etendue"] > seuil_alerte_mm

    lignes = [
        "=" * 60,
        "  RAPPORT DE MESURE — ProfilScan (FACOM SCANDIAG® REemploi)",
        "=" * 60,
        f"  Date             : {now}",
        f"  Surface mesurée  : {nom_surface}",
        f"  Points valides   : {stats['n_points_valides']}",
        "-" * 60,
        "  PROFIL DE HAUTEUR",
        f"    Minimum        : {stats['min']:+.3f} mm",
        f"    Maximum        : {stats['max']:+.3f} mm",
        f"    Étendue (Rz)   : {stats['etendue']:.3f} mm",
        f"    Moyenne        : {stats['moyenne']:+.3f} mm",
        f"    Écart-type     : {stats['ecart_type']:.3f} mm",
        f"    Rugosité Ra    : {stats['Ra']:.3f} mm",
        "-" * 60,
        "  DIAGNOSTIC IA",
        f"    État           : {resultat_ml['label_fr']}",
        f"    Confiance      : {resultat_ml['confiance'] * 100:.1f}%",
        "    Probabilités   :",
    ]

    for classe, proba in resultat_ml["probabilites"].items():
        labels_fr = {"neuf": "Neuf", "use": "Usé", "tres_use": "Très usé"}
        lignes.append(f"      {labels_fr.get(classe, classe):<12}: {proba * 100:5.1f}%")

    lignes += [
        "-" * 60,
        "  VERDICT",
    ]

    if alerte:
        lignes.append(f"  ⚠️  ALERTE : étendue {stats['etendue']:.3f} mm > seuil {seuil_alerte_mm:.3f} mm")
        lignes.append("      Inspection approfondie recommandée.")
    else:
        lignes.append("  ✅  Mesure dans les limites nominales.")

    lignes += [
        "=" * 60,
        "  Généré par ProfilScan — Réemploi RSE FACOM SCANDIAG® (DX.TSCANPB)",
        "  Concours National Informatique Ynov",
        "=" * 60,
    ]

    return "\n".join(lignes)


# ── Rapport graphique ────────────────────────────────────────────────────────

def generer_rapport_figure(
    image_brute: np.ndarray,
    positions_laser: np.ndarray,
    profil_mm: np.ndarray,
    stats: dict,
    resultat_ml: dict,
    nom_surface: str = "Surface",
    chemin_sortie: str | Path | None = None,
) -> plt.Figure:
    """Génère une figure matplotlib complète avec image + profil + diagnostic.

    Disposition :
      Ligne 1 : Image caméra brute | Image avec ligne laser détectée
      Ligne 2 : Profil de hauteur (mm vs colonne)
      Ligne 3 : Tableau de synthèse + verdict ML

    Args:
        image_brute: Image BGR (H x W x 3).
        positions_laser: Positions Y de la ligne laser (pixels).
        profil_mm: Profil de hauteur en mm.
        stats: Statistiques du profil.
        resultat_ml: Résultat de classification ML.
        nom_surface: Nom de la surface mesurée.
        chemin_sortie: Si fourni, sauvegarde la figure en PNG à ce chemin.

    Returns:
        Figure matplotlib.
    """
    import cv2  # Import local pour éviter la dépendance au niveau module

    fig = plt.figure(figsize=(14, 10))
    fig.patch.set_facecolor("#f8f9fa")
    gs = gridspec.GridSpec(3, 2, figure=fig, hspace=0.45, wspace=0.3)

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    fig.suptitle(
        f"ProfilScan — Rapport de mesure : {nom_surface}\n{now}",
        fontsize=14, fontweight="bold", y=0.98,
    )

    # ── Panneau 1 : Image brute ──────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0, 0])
    img_rgb = cv2.cvtColor(image_brute, cv2.COLOR_BGR2RGB)
    ax1.imshow(img_rgb)
    ax1.set_title("Image caméra brute", fontsize=10)
    ax1.axis("off")

    # ── Panneau 2 : Image avec ligne détectée ───────────────────────────
    ax2 = fig.add_subplot(gs[0, 1])
    img_visu = image_brute.copy()
    H, W = img_visu.shape[:2]
    for col in range(W - 1):
        if not np.isnan(positions_laser[col]) and not np.isnan(positions_laser[col + 1]):
            y1 = int(round(np.clip(positions_laser[col], 0, H - 1)))
            y2 = int(round(np.clip(positions_laser[col + 1], 0, H - 1)))
            cv2.line(img_visu, (col, y1), (col + 1, y2), (0, 255, 0), 2)
    ax2.imshow(cv2.cvtColor(img_visu, cv2.COLOR_BGR2RGB))
    ax2.set_title("Ligne laser détectée (en vert)", fontsize=10)
    ax2.axis("off")

    # ── Panneau 3 : Profil de hauteur ───────────────────────────────────
    ax3 = fig.add_subplot(gs[1, :])
    x_cols = np.arange(len(profil_mm))
    valides = ~np.isnan(profil_mm)

    ax3.fill_between(
        x_cols[valides], profil_mm[valides],
        alpha=0.3, color="#3b82f6", label="Profil"
    )
    ax3.plot(x_cols[valides], profil_mm[valides], color="#1d4ed8", linewidth=1.5)
    ax3.axhline(y=0, color="gray", linestyle="--", linewidth=0.8, alpha=0.6, label="Référence (plan zéro)")
    ax3.axhline(
        y=stats["moyenne"],
        color="orange", linestyle=":", linewidth=1.2,
        label=f"Moyenne : {stats['moyenne']:+.3f} mm"
    )

    ax3.set_xlabel("Colonne (pixels)", fontsize=9)
    ax3.set_ylabel("Hauteur (mm)", fontsize=9)
    ax3.set_title("Profil de hauteur reconstruit", fontsize=10)
    ax3.legend(fontsize=8, loc="upper right")
    ax3.grid(True, alpha=0.3)
    ax3.set_facecolor("#f0f4ff")

    # ── Panneau 4 : Tableau de synthèse ─────────────────────────────────
    ax4 = fig.add_subplot(gs[2, :])
    ax4.axis("off")

    couleur_verdict = {
        "neuf": "#dcfce7",
        "use": "#fef9c3",
        "tres_use": "#fee2e2",
    }.get(resultat_ml["classe"], "#f3f4f6")

    # Libellés sans emoji (DejaVu Sans ne supporte pas les emojis Unicode)
    labels_figure = {"neuf": "Neuf [OK]", "use": "Use [ATT.]", "tres_use": "Tres use [!]"}
    label_figure = labels_figure.get(resultat_ml["classe"], resultat_ml["classe"])

    texte_verdict = (
        f"Diagnostic IA : {label_figure}  "
        f"(confiance : {resultat_ml['confiance'] * 100:.0f}%)"
    )

    tableau_data = [
        ["Min", "Max", "Étendue (Rz)", "Ra", "Écart-type"],
        [
            f"{stats['min']:+.3f} mm",
            f"{stats['max']:+.3f} mm",
            f"{stats['etendue']:.3f} mm",
            f"{stats['Ra']:.3f} mm",
            f"{stats['ecart_type']:.3f} mm",
        ],
    ]

    table = ax4.table(
        cellText=tableau_data[1:],
        colLabels=tableau_data[0],
        loc="upper center",
        cellLoc="center",
        bbox=[0.0, 0.4, 1.0, 0.55],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)

    ax4.text(
        0.5, 0.1, texte_verdict,
        ha="center", va="center",
        fontsize=12, fontweight="bold",
        transform=ax4.transAxes,
        bbox=dict(boxstyle="round,pad=0.4", facecolor=couleur_verdict, edgecolor="#6b7280"),
    )

    ax4.text(
        0.5, -0.05,
        "ProfilScan — Réemploi RSE FACOM SCANDIAG® (DX.TSCANPB) — Concours National Ynov",
        ha="center", va="bottom", fontsize=7, color="gray",
        transform=ax4.transAxes,
    )

    if chemin_sortie is not None:
        fig.savefig(str(chemin_sortie), dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())

    return fig
