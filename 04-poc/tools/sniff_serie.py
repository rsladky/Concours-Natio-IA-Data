#!/usr/bin/env python3
"""
tools/sniff_serie.py — Découverte du protocole série du SCANDIAG

Ouvre un port série (Bluetooth SPP ou USB-TTL) et affiche le flux brut
en hexadécimal + ASCII pour comprendre ce que le device émet réellement
avant d'adapter acquisition.depuis_serie().

Utilisation typique :
    # Après appairage BT, trouver le port :
    ls /dev/cu.*
    # Écoute 10 s sur le port trouvé :
    python tools/sniff_serie.py --port /dev/cu.SCANDIAG-SerialPort --duree 10
    # Tester plusieurs baudrates automatiquement :
    python tools/sniff_serie.py --port /dev/cu.SCANDIAG-SerialPort --auto-baud
    # Sauvegarder le dump brut :
    python tools/sniff_serie.py --port /dev/cu.SCANDIAG-SerialPort --sortie dump.bin
"""

import argparse
import sys
import time
from pathlib import Path

# Baudrates courants classés par probabilité pour un scanner industriel BT
BAUDRATES_COURANTS = [115200, 57600, 38400, 19200, 9600]

# Marqueurs JPEG
JPEG_SOI = bytes([0xFF, 0xD8])   # Start Of Image
JPEG_EOI = bytes([0xFF, 0xD9])   # End Of Image


def hexdump(data: bytes, offset: int = 0, largeur: int = 16) -> str:
    """Formate un bloc de bytes en hexdump lisible (offset | hex | ASCII)."""
    lignes = []
    for i in range(0, len(data), largeur):
        chunk = data[i : i + largeur]
        hex_part = " ".join(f"{b:02X}" for b in chunk)
        asc_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lignes.append(f"  {offset + i:06X}  {hex_part:<{largeur * 3}}  {asc_part}")
    return "\n".join(lignes)


def analyser_jpeg(data: bytes) -> list[tuple[int, int]]:
    """Repère les trames JPEG complètes (FF D8 ... FF D9) dans le buffer."""
    trames = []
    pos = 0
    while pos < len(data) - 1:
        idx_soi = data.find(JPEG_SOI, pos)
        if idx_soi == -1:
            break
        idx_eoi = data.find(JPEG_EOI, idx_soi + 2)
        if idx_eoi == -1:
            break
        trames.append((idx_soi, idx_eoi + 2))
        pos = idx_eoi + 2
    return trames


def sniffer(port: str, baudrate: int, duree: float, sortie: str | None) -> bytes:
    """Lit le flux série pendant `duree` secondes et retourne les octets bruts."""
    try:
        import serial
    except ImportError:
        print("ERREUR : pyserial non installé. Lancez : pip install pyserial")
        sys.exit(1)

    print(f"\n{'═' * 60}")
    print(f"  Port    : {port}")
    print(f"  Baud    : {baudrate}")
    print(f"  Durée   : {duree} s")
    print(f"{'═' * 60}")

    try:
        ser = serial.Serial(port, baudrate, timeout=0.1)
    except serial.SerialException as e:
        print(f"ERREUR ouverture port : {e}")
        sys.exit(1)

    buffer = bytearray()
    debut = time.monotonic()
    derniere_affichage = debut
    octets_par_bloc = 0

    print(f"\n  Écoute en cours... (Ctrl+C pour arrêter)\n")
    try:
        while (time.monotonic() - debut) < duree:
            chunk = ser.read(256)
            if chunk:
                buffer.extend(chunk)
                octets_par_bloc += len(chunk)
                # Affichage progressif toutes les 0.5 s
                now = time.monotonic()
                if now - derniere_affichage >= 0.5:
                    elapsed = now - debut
                    print(f"  {elapsed:5.1f}s — {len(buffer):6d} octets reçus "
                          f"(+{octets_par_bloc} ce bloc)")
                    octets_par_bloc = 0
                    derniere_affichage = now
    except KeyboardInterrupt:
        print("\n  Arrêt utilisateur.")
    finally:
        ser.close()

    return bytes(buffer)


def rapport(data: bytes, baudrate: int) -> None:
    """Affiche le rapport d'analyse du buffer capturé."""
    n = len(data)
    print(f"\n{'─' * 60}")
    print(f"  RÉSUMÉ — {n} octets capturés @ {baudrate} baud")
    print(f"{'─' * 60}")

    if n == 0:
        print("\n  ⚠  Aucun octet reçu.")
        print("  Causes possibles :")
        print("  • Device non connecté / hors tension")
        print("  • Mauvais baudrate → essayez --auto-baud")
        print("  • Le MCU attend une commande pour démarrer l'émission")
        print("  • Port série fermé côté macOS → dépairer/réappairer le device BT")
        return

    # Hexdump des 256 premiers octets
    limite = min(256, n)
    print(f"\n  Hexdump des {limite} premiers octets :\n")
    print(hexdump(data[:limite]))
    if n > limite:
        print(f"  ... ({n - limite} octets supplémentaires non affichés)")

    # Analyse JPEG
    trames = analyser_jpeg(data)
    print(f"\n  Trames JPEG complètes détectées : {len(trames)}")
    for i, (debut, fin) in enumerate(trames[:5]):
        taille = fin - debut
        print(f"    [{i}] offset {debut:06X}–{fin:06X}  ({taille} octets)")

    # Marqueurs incomplets
    n_soi = data.count(JPEG_SOI)
    n_eoi = data.count(JPEG_EOI)
    if n_soi or n_eoi:
        print(f"\n  Marqueurs JPEG : {n_soi}× FF D8 (SOI)  |  {n_eoi}× FF D9 (EOI)")
        if n_soi != n_eoi:
            print("  ⚠  Déséquilibre SOI/EOI → trames peut-être incomplètes "
                  "(timeout trop court ?)")

    # Caractères ASCII / texte
    ascii_bytes = sum(32 <= b < 127 or b in (9, 10, 13) for b in data)
    pct_ascii = ascii_bytes / n * 100 if n else 0
    print(f"\n  Caractères ASCII printables : {ascii_bytes}/{n} ({pct_ascii:.0f}%)")
    if pct_ascii > 70:
        # Essayer d'afficher le début comme texte
        try:
            apercu = data[:200].decode("ascii", errors="replace").replace("\r", "")
            print("  → Probable format TEXTE / NMEA / JSON :")
            for ligne in apercu.split("\n")[:10]:
                print(f"    {ligne}")
        except Exception:
            pass
    elif len(trames) > 0:
        print("  → Format JPEG détecté — from_serie() pourrait fonctionner tel quel.")
    elif n_soi > 0:
        print("  → Marqueurs JPEG partiels — buffer peut-être trop court ou trop court.")
    else:
        print("  → Format binaire inconnu. Examiner l'hexdump pour trouver "
              "un header ou une séquence de synchronisation.")

    # Entropie rapide
    from collections import Counter
    dist = Counter(data)
    entropie = -sum((c / n) * __import__("math").log2(c / n)
                    for c in dist.values() if c)
    print(f"  Entropie Shannon : {entropie:.2f} bits/octet "
          f"(8.0 = aléatoire/compressé, <4 = texte/structuré)")


def auto_baud(port: str, duree_par_baud: float = 3.0) -> None:
    """Tente chaque baudrate et affiche combien d'octets arrivent."""
    print(f"\n  Mode auto-baud — test de {len(BAUDRATES_COURANTS)} vitesses "
          f"({duree_par_baud} s chacune)...\n")
    resultats = []
    for baud in BAUDRATES_COURANTS:
        print(f"  Test {baud:>7} baud...", end=" ", flush=True)
        data = sniffer(port, baud, duree_par_baud, sortie=None)
        n = len(data)
        print(f"{n:6d} octets")
        resultats.append((n, baud, data))

    print(f"\n  ── Classement (le plus d'octets en premier) ──")
    for n, baud, _ in sorted(resultats, reverse=True):
        marker = " ← meilleur candidat" if n == max(r[0] for r in resultats) else ""
        print(f"  {baud:>7} baud : {n:6d} octets{marker}")

    # Afficher le rapport du baudrate qui a reçu le plus
    meilleur = sorted(resultats, reverse=True)[0]
    if meilleur[0] > 0:
        print(f"\n  Rapport pour {meilleur[1]} baud :")
        rapport(meilleur[2], meilleur[1])


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Découverte du protocole série du SCANDIAG (sniffeur hex + analyse JPEG)"
    )
    parser.add_argument(
        "--port",
        required=True,
        help="Port série, ex. /dev/cu.SCANDIAG-SerialPort ou /dev/cu.usbserial-0001",
    )
    parser.add_argument(
        "--baud",
        type=int,
        default=115200,
        help="Baudrate (défaut : 115200)",
    )
    parser.add_argument(
        "--duree",
        type=float,
        default=10.0,
        help="Durée d'écoute en secondes (défaut : 10)",
    )
    parser.add_argument(
        "--auto-baud",
        action="store_true",
        help="Tester automatiquement tous les baudrates courants",
    )
    parser.add_argument(
        "--sortie",
        type=str,
        default=None,
        help="Fichier où sauvegarder le dump brut (binaire)",
    )
    args = parser.parse_args()

    if args.auto_baud:
        auto_baud(args.port)
    else:
        data = sniffer(args.port, args.baud, args.duree, args.sortie)
        rapport(data, args.baud)

        if args.sortie and data:
            chemin = Path(args.sortie)
            chemin.write_bytes(data)
            print(f"\n  Dump sauvegardé : {chemin.resolve()} ({len(data)} octets)")


if __name__ == "__main__":
    main()
