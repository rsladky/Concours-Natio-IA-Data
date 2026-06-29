# Rétro-ingénierie — Inventaire des composants

> Photos du démontage archivées dans [`../assets/`](../assets/) — IMG_0346 à IMG_0350.

## Spécifications confirmées (fiche produit officielle FACOM)

| Paramètre | Valeur officielle |
|-----------|-------------------|
| Référence produit | DX.TSCANPB |
| Batterie | Li-ion 3,7 V / 0,620 Ah |
| Classification laser | 3R |
| Communication | Bluetooth® intégré |
| Connecteur de charge | **USB Mini-B** |
| Tension d'entrée charge | **5 V / 0,5 A** (USB 2.0 standard) |
| Source alimentation externe | 100/240 VCA → USB Mini-B |
| Température de fonctionnement | 0 à 40 °C |
| Température de stockage | −20 à 60 °C |
| Autonomie | ~500 mesures (~60 véhicules) |
| Dimensions boîtier transport | 330 × 215 × 60 mm |
| Certifications | RoHS (2011/65/EU), EMC (2014/30/EU), RED (2014/53/EU) |

---

## Tableau des composants clés

| #   | Composant                       | Référence relevée | Fabricant | Fonction exploitable | Datasheet |
| --- | ------------------------------- | ----------------- | --------- | -------------------- | --------- |
| 1   | **MCU principal**               | **STM32F429** (ARM Cortex-M4 @ 180 MHz, 2MB Flash, 256KB RAM) — marquage à l'envers img#9 | STMicroelectronics | Calcul triangulation laser, interface caméra DCMI, USB OTG, UART×4, SPI, I2C, FMC (SDRAM) — **reflashable via SWD ou UART BOOT0** | st.com/stm32f4 |
| 2   | **SDRAM externe (Micron)**      | `9CA15 / RB151` (logo Micron) — img#9 bas gauche | Micron | Buffer de frames caméra (FMC du STM32F429) | micron.com |
| 3   | **SDRAM externe (ISSI)**        | `IS42S` (début lisible) — img#9 bas droite | ISSI | SDRAM 16-bit, buffer image supplémentaire | issi.com |
| 4   | **Module Bluetooth Classic**    | **Silicon Labs WT12-A** (FCC: QOQWT12, SN: 1934A01HOX) — img#1 | Silicon Labs (ex-Bluegiga) | BT 2.1+EDR, firmware iWRAP, AT commands UART → SPP port série virtuel PC | silabs.com/wt12 |
| 5   | **Oscillateur 24 MHz**          | `24.00B / 0B98HL` — img#5 | — | Horloge MCLK du capteur caméra (typique OV2640/OV7670) | — |
| 6   | **Capteur CMOS (caméra)**       | *(TODO — identifier via FPC)* | OmniVision probable (OV2640 ?) | Acquisition image ligne laser ; interface DCMI vers STM32F429 | *(TODO)* |
| 7   | **Optique caméra**              | *(TODO)* | — | Focale fixe ; à caractériser (FOV, distorsion) | — |
| 8   | **Diode laser + driver**        | *(TODO)* | — | Ligne rouge ≤5mW, classe 3R, IEC 60825-1:2014 | *(TODO)* |
| 9   | **Lentille cylindrique**        | *(TODO)* | — | Point laser → ligne structurée | — |
| 10  | **Batterie Li-Po**              | **EEMB LP602248** — 3,7V / 620mAh / 2,3Wh — img#0346 | EEMB | Alimentation portable réutilisable | eemb.com |
| 11  | **Contrôleur DC-DC**            | `LGCS / B901 / B910` (SO-8) — img#3 | *(TODO)* | Convertisseur boost/buck (2 inductances associées) — génère les rails 3,3V et/ou 5V | *(TODO)* |
| 12  | **Contrôleur de charge**        | `VDY6 / B301` (8 broches) — img#11 | *(TODO)* | Gestion charge Li-Po via USB Mini-B 5V/500mA | *(TODO)* |
| 13  | **Inductances DC-DC (×2)**      | Bobines SMD carrées — img#3, #6, #11 | — | Éléments passifs du convertisseur DC-DC | — |
| 14  | **Connecteurs JST (×2)**        | JST 3 et 4 broches — img#8 | JST | Câbles internes laser / caméra / boutons | — |
| 15  | **Connecteur USB Mini-B**       | USB Mini-B (confirmé fiche + étiquette) | — | Charge 5V/0,5A + debug UART possible | — |
| 16  | **Boutons / LEDs**              | Visibles sur PCB | — | UI minimaliste (mesure, mode, power) | — |

---

## Notes de démontage

- **Nombre de PCB** : 1 PCB principal (visible IMG_0347/0349/0350)
- **Marquage PCB** : `PCS24-E` / `3909305` (visible IMG_0347)
- **Fabrication** : Made in Italy, Stanley Black & Decker France (69570 Dardilly)
- **Photos archivées dans** : [`../assets/`](../assets/) — IMG_0346 à IMG_0350
- **MCU identifié** : **STM32F429** — ARM Cortex-M4 @ 180 MHz, DCMI caméra, FMC SDRAM, 2MB Flash — reflashable SWD/UART
- **SDRAM ×2** : Micron (`9CA15/RB151`) + ISSI (`IS42S`) — buffer frames caméra
- **Module BT** : Silicon Labs WT12-A — BT Classic 2.1+EDR, iWRAP UART
- **Oscillateur 24 MHz** : MCLK du capteur caméra
- **DC-DC** : contrôleur `LGCS/B901` + 2 inductances — rails d'alimentation
- **Charge Li-Po** : CI `VDY6/B301` près des inductances et WT12-A
- **TODO restants** : identifier capteur CMOS (FPC caméra), diode laser/driver

---

## Procédure de relevé des références

1. Ouvrir le produit (vis cruciformes, éventuellement clips plastiques — ne pas forcer).
2. Photographier chaque face du PCB **avant** tout démontage de composant.
3. Pour chaque CI discret : lire le marquage imprimé en lumière rasante / loupe.
4. Rechercher la datasheet sur le site du fabricant, [Datasheet360](https://www.datasheet360.com), ou
   [AllDatasheet](https://www.alldatasheet.com).
5. Archiver le PDF dans [`datasheets/`](datasheets/) avec le nom `<référence>.pdf`.
6. Compléter le tableau ci-dessus ligne par ligne.
