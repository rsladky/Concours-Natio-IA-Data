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

| #   | Composant                                    | Référence relevée | Fabricant probable                      | Fonction exploitable                                                                             | Datasheet archivée |
| --- | -------------------------------------------- | ----------------- | --------------------------------------- | ------------------------------------------------------------------------------------------------ | ------------------ |
| 1   | **MCU / SoC principal**                      | *(TODO — photo macro du gros chip IMG_0347)* | *(TODO)*  | Calcul profil, contrôle laser/caméra, gestion batterie | *(TODO)*    |
| 2   | **Module WiFi + Bluetooth**                  | **u-blox NINA-W10x** (SN: 1934A01HDX) — ⚠️ ESP32 intégré ! | u-blox | WiFi 802.11 b/g/n + BT 5.0 + dual-core 240 MHz — reprogrammable via UART ; remplace un Raspberry Pi pour le POC | A chercher sur u-blox.com |
| 3   | **Capteur CMOS (module caméra)**             | *(TODO — FPC à droite sur IMG_0347)*  | *(TODO)*  | Acquisition image ligne laser déformée                  | *(TODO)*    |
| 4   | **Optique caméra**                           | *(TODO)*              | —         | Focale fixe ~5–15 cm ; à caractériser                   | —           |
| 5   | **Diode laser + driver**                     | *(TODO)*              | *(TODO)*  | Ligne rouge ≤5mW, classe 3R, IEC 60825-1:2014 (confirmé étiquette) | *(TODO)* |
| 6   | **Lentille cylindrique / diffractive**       | *(TODO)*              | —         | Point laser → ligne structurée                          | —           |
| 7   | **Batterie Li-Po**                           | **EEMB LP602248** — 3,7V / 620mAh / 2,3Wh (confirmé IMG_0346) | EEMB | Alimentation portable ; réutilisable tel quel | A chercher EEMB LP602248 |
| 8   | **Régulateur de tension / DC-DC**            | *(TODO)*              | TI / Ricoh / Semtech | 3,7V → 3,3V et/ou 5V                       | *(TODO)*    |
| 9   | **Circuit de charge USB**                    | *(TODO)*              | TI BQ24xxx / MPS | Charge 5V/500mA via Mini-B (confirmé étiquette)    | *(TODO)*    |
| 10  | **Mémoire flash externe**                    | *(TODO)*              | Winbond / Macronix | Stockage firmware SPI                             | *(TODO)*    |
| 11  | **Convertisseur USB/TTL**                    | *(TODO)*              | CP2102 / CH340 | Pont UART↔USB (debug/flash du NINA-W10 via UART)    | *(TODO)*    |
| 12  | **Boutons / LEDs**                           | *(visible IMG_0347)*  | —         | UI minimaliste                                          | —           |
| 13  | **Connecteur USB Mini-B**                    | USB Mini-B (confirmé) | —         | Charge 5V/0,5A + potentiellement debug série            | —           |

---

## Notes de démontage

- **Nombre de PCB** : 1 PCB principal (visible IMG_0347/0349/0350)
- **Marquage PCB** : `PCS24-E` / `3909305` (visible IMG_0347)
- **Fabrication** : Made in Italy, Stanley Black & Decker France (69570 Dardilly)
- **Photos archivées dans** : [`../assets/`](../assets/) — IMG_0346 à IMG_0350
- **Découverte clé** : le module de communication est un **u-blox NINA-W10x** (ESP32 intégré), pas juste BT — ajoute WiFi et puissance de calcul embarquée !
- **TODO** : photo macro du gros chip carré (MCU principal) sur IMG_0347 pour lire le marquage

---

## Procédure de relevé des références

1. Ouvrir le produit (vis cruciformes, éventuellement clips plastiques — ne pas forcer).
2. Photographier chaque face du PCB **avant** tout démontage de composant.
3. Pour chaque CI discret : lire le marquage imprimé en lumière rasante / loupe.
4. Rechercher la datasheet sur le site du fabricant, [Datasheet360](https://www.datasheet360.com), ou
   [AllDatasheet](https://www.alldatasheet.com).
5. Archiver le PDF dans [`datasheets/`](datasheets/) avec le nom `<référence>.pdf`.
6. Compléter le tableau ci-dessus ligne par ligne.
