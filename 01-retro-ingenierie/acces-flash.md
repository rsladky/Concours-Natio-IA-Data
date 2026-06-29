# Rétro-ingénierie — Accès bootloader et firmware

> **Objectif :** identifier comment se connecter au MCU pour lire, modifier ou remplacer le firmware.  
> **TODO jour J :** compléter les sections marquées après ouverture et inspection visuelle du PCB.

---

## 1. Méthode de détection des points de flash

### 1.1 Inspection visuelle
- Chercher des **rangées de trous non peuplés** ou de **pastilles exposées** près du MCU — ce sont
  généralement les test pads UART / SWD / JTAG.
- Points typiques à repérer :
  - `GND`, `VCC` (3,3 V)
  - `TX`, `RX` (UART — débogage / flash série)
  - `SWDIO`, `SWDCLK` (SWD — debug ARM Cortex-M)
  - `TCK`, `TMS`, `TDI`, `TDO`, `TRST` (JTAG complet)
  - `BOOT0` / `BOOT` (sélection du mode bootloader sur STM32 / NXP)
- Sur les STM32 courants : mettre `BOOT0` à `1` (3,3 V) au démarrage → MCU passe en mode
  bootloader UART / DFU USB.

### 1.2 Suivi de traces PCB
- Tracer les fils depuis le connecteur USB vers le MCU — identifier si le USB est câblé en
  **DFU natif** (USB Device) ou via un convertisseur USB/TTL (CP2102 / CH340).
- Tracer les fils du module BT vers le MCU pour localiser l'UART associé.

### 1.3 Continuité au multimètre
- Avec le produit **hors tension**, mesurer la continuité entre le connecteur USB et les broches
  MCU pour cartographier le câblage.

---

## 2. Cartographie des points de connexion

*(TODO jour J — remplir après inspection)*

| Point | Localisation sur PCB | Signal | Niveau logique | Notes |
|-------|----------------------|--------|----------------|-------|
| TP1 | *(TODO)* | *(TODO)* | *(TODO)* | |
| TP2 | *(TODO)* | *(TODO)* | *(TODO)* | |
| TP3 | *(TODO)* | *(TODO)* | *(TODO)* | |
| TP4 | *(TODO)* | *(TODO)* | *(TODO)* | |
| TP5 | *(TODO)* | *(TODO)* | *(TODO)* | |

---

## 3. Procédure de lecture du firmware existant

### Via UART (STM32 type)
```bash
# Installer stm32flash
brew install stm32flash   # macOS
# Mettre BOOT0 = HIGH, reset, puis :
stm32flash -r firmware_backup.bin /dev/cu.usbserial-XXXX
```

### Via SWD (OpenOCD)
```bash
# Avec une sonde ST-Link V2 (ou clone) :
openocd -f interface/stlink.cfg -f target/stm32f1x.cfg \
  -c "init; halt; dump_image firmware_backup.bin 0x08000000 0x40000; exit"
```

### Via DFU USB natif (STM32 / NXP)
```bash
pip install dfu-util
# Mettre le MCU en mode DFU, puis :
dfu-util -a 0 -s 0x08000000 -U firmware_backup.bin
```

> ⚠️ La lecture du firmware peut être protégée par le **Read Protection (RDP)**. Dans ce cas,
> la lecture est impossible sans effacer la flash. Ne pas effacer si l'on veut conserver le
> fonctionnement d'origine.

---

## 4. Procédure de flash d'un firmware alternatif

*(Une fois le MCU identifié et les test pads localisés)*

1. Sauvegarder le firmware d'origine (si lecture possible).
2. Écrire le nouveau firmware via UART / SWD / DFU selon l'interface disponible.
3. Tester la stabilité avant de remonter le boîtier.
4. Documenter la procédure complète dans ce fichier.

---

## 5. Observations jour J

*(TODO — compléter au fil du démontage)*

- Type de MCU confirmé : ___
- Interface de flash disponible : ___
- RDP activé : Oui / Non / Inconnu
- Firmware lu et archivé : Oui / Non
- Firmware alternatif flashé : Oui / Non
- Notes : ___
