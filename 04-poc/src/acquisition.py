"""
acquisition.py — Module d'entrée image du pipeline ProfilScan

Sources d'image supportées :
  1. Fichier image (JPEG / PNG) — utilisé pour le POC et les tests
  2. Flux série / USB TTL (interface prévue pour le vrai device SCANDIAG le jour J)
  3. Caméra locale (webcam) — pour tests avec un laser externe

Le module retourne toujours un np.ndarray BGR (format OpenCV standard).
"""

import cv2
import numpy as np
from pathlib import Path


def depuis_fichier(chemin: str | Path) -> np.ndarray:
    """Charge une image depuis un fichier disque.

    Args:
        chemin: Chemin vers le fichier image (JPEG, PNG, BMP…).

    Returns:
        Image BGR uint8 (H x W x 3).

    Raises:
        FileNotFoundError: si le fichier n'existe pas.
        ValueError: si l'image ne peut pas être décodée.
    """
    chemin = Path(chemin)
    if not chemin.exists():
        raise FileNotFoundError(f"Fichier introuvable : {chemin}")

    img = cv2.imread(str(chemin))
    if img is None:
        raise ValueError(f"Impossible de décoder l'image : {chemin}")

    return img


def depuis_camera(index: int = 0, largeur: int = 640, hauteur: int = 480) -> np.ndarray:
    """Capture une image depuis une caméra locale (webcam ou caméra USB).

    Utile pour tester le pipeline avec un laser externe pendant le développement.

    Args:
        index: Index de la caméra (0 = caméra par défaut).
        largeur: Largeur souhaitée de la capture.
        hauteur: Hauteur souhaitée de la capture.

    Returns:
        Image BGR uint8.

    Raises:
        RuntimeError: si la caméra n'est pas accessible.
    """
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        raise RuntimeError(f"Impossible d'ouvrir la caméra {index}")

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, largeur)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, hauteur)

    ret, frame = cap.read()
    cap.release()

    if not ret or frame is None:
        raise RuntimeError("Échec de la capture de l'image")

    return frame


def depuis_serie(port: str, baudrate: int = 115200, timeout: float = 5.0) -> np.ndarray:
    """Reçoit une image encodée JPEG depuis le SCANDIAG via UART/USB-TTL.

    Interface prévue pour brancher le vrai device le jour J. Le protocole
    attendu est un flux JPEG précédé d'un en-tête de 4 octets indiquant la
    taille (big-endian uint32).

    Args:
        port: Port série (ex. '/dev/cu.usbserial-0001' sur macOS, 'COM3' sur Windows).
        baudrate: Vitesse de communication (à adapter selon le firmware SCANDIAG).
        timeout: Délai maximum d'attente en secondes.

    Returns:
        Image BGR uint8.

    Raises:
        ImportError: si pyserial n'est pas installé.
        RuntimeError: en cas d'erreur de communication.
    """
    try:
        import serial  # pyserial — ajouter à requirements.txt si nécessaire
    except ImportError:
        raise ImportError("pyserial est requis pour l'acquisition série : pip install pyserial")

    with serial.Serial(port, baudrate, timeout=timeout) as ser:
        # Lire l'en-tête de taille (4 octets big-endian)
        header = ser.read(4)
        if len(header) < 4:
            raise RuntimeError("Timeout : en-tête non reçu")

        taille = int.from_bytes(header, byteorder='big')
        if taille <= 0 or taille > 10 * 1024 * 1024:  # Sanity check : max 10 Mo
            raise RuntimeError(f"Taille d'image invalide : {taille} octets")

        # Lire le payload JPEG
        donnees = ser.read(taille)
        if len(donnees) < taille:
            raise RuntimeError(f"Trame incomplète : {len(donnees)}/{taille} octets reçus")

    buf = np.frombuffer(donnees, dtype=np.uint8)
    img = cv2.imdecode(buf, cv2.IMREAD_COLOR)
    if img is None:
        raise RuntimeError("Décodage JPEG échoué")

    return img


def generer_image_synthetique(
    largeur: int = 640,
    hauteur: int = 480,
    profil: str = "sinusoide",
    bruit: float = 1.5,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """Génère une image synthétique simulant la vue de la caméra SCANDIAG.

    La ligne laser rouge apparaît déformée selon le profil de hauteur simulé.
    Utilisé pour le POC en l'absence du matériel physique.

    Args:
        largeur: Largeur de l'image en pixels.
        hauteur: Hauteur de l'image en pixels.
        profil: Type de profil simulé :
            - 'sinusoide'  : profil ondulé (surface gaufrée)
            - 'plat'       : surface parfaitement plane
            - 'rampe'      : pente linéaire croissante
            - 'defaut'     : surface plane avec un creux local (défaut d'usure)
        bruit: Écart-type du bruit gaussien ajouté à la position de la ligne (pixels).
        rng: Générateur de nombres aléatoires (pour reproductibilité).

    Returns:
        Image BGR uint8 simulant la vue caméra.
    """
    if rng is None:
        rng = np.random.default_rng(seed=42)

    img = np.zeros((hauteur, largeur, 3), dtype=np.uint8)

    # Ligne laser au centre de l'image en l'absence de surface (référence)
    y_ref = hauteur // 2

    x = np.arange(largeur, dtype=float)

    # Calcul du déplacement vertical selon le profil
    if profil == "plat":
        dy = np.zeros(largeur)

    elif profil == "sinusoide":
        dy = 40 * np.sin(2 * np.pi * x / (largeur / 3))

    elif profil == "rampe":
        dy = np.linspace(-60, 60, largeur)

    elif profil == "defaut":
        dy = np.zeros(largeur)
        # Creux local simulant une zone d'usure
        centre_defaut = largeur // 2
        largeur_defaut = 80
        profondeur = 30
        masque = np.abs(x - centre_defaut) < largeur_defaut / 2
        dy[masque] = profondeur * np.cos(
            np.pi * (x[masque] - centre_defaut) / largeur_defaut
        )
    else:
        raise ValueError(f"Profil inconnu : '{profil}'. Choisir parmi : plat, sinusoide, rampe, defaut")

    # Ajouter du bruit pour simuler les conditions réelles
    dy += rng.normal(0, bruit, largeur)

    # Dessiner la ligne laser : trait rouge fin avec dégradé gaussien (simulation)
    y_laser = (y_ref + dy).astype(int)
    y_laser = np.clip(y_laser, 2, hauteur - 3)

    for col in range(largeur):
        y_c = y_laser[col]
        # Intensité gaussienne sur 5 pixels de hauteur
        for dy_px in range(-2, 3):
            y_px = y_c + dy_px
            if 0 <= y_px < hauteur:
                intensite = int(255 * np.exp(-0.5 * (dy_px / 1.0) ** 2))
                img[y_px, col, 2] = min(255, img[y_px, col, 2] + intensite)  # Canal rouge

    return img
