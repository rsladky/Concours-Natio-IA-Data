# Rétro-ingénierie — Inventaire des composants

> **TODO jour J :** compléter les colonnes *Référence* et *Datasheet* après ouverture du produit.  
> Les *Fonctions exploitables* ci-dessous sont déduites de la documentation produit connue.

---

## Tableau des composants clés

| # | Composant | Référence relevée | Fabricant probable | Fonction exploitable | Datasheet archivée |
|---|-----------|-------------------|--------------------|---------------------|--------------------|
| 1 | **MCU / SoC principal** | *(TODO jour J)* | STMicroelectronics / NXP / Renesas | Calcul du profil par triangulation, contrôle des périphériques, gestion batterie, Bluetooth host | *(TODO jour J)* |
| 2 | **Module Bluetooth** | *(TODO jour J)* | Murata / u-blox / TI CC26xx / Microchip | Communication BLE vers application mobile ; réutilisable comme module IoT autonome | *(TODO jour J)* |
| 3 | **Capteur CMOS (module caméra)** | *(TODO jour J)* | OV76xx / OV2640 / Aptina | Acquisition image de la ligne laser déformée ; réutilisable en vision industrielle / inspection | *(TODO jour J)* |
| 4 | **Optique caméra** | *(TODO jour J)* | — | Focale fixe adaptée à la distance de mesure (~5–15 cm) ; à caractériser (FOV, distorsion) | — |
| 5 | **Diode laser + driver** | *(TODO jour J)* | OSRAM / Sharp / Rohm | Projection de la ligne rouge (650 nm, classe 3R) ; réutilisable comme source structurée | *(TODO jour J)* |
| 6 | **Lentille cylindrique / diffractive** | *(TODO jour J)* | — | Transforme le point laser en ligne ; réutilisable pour tout scanner à lumière structurée | — |
| 7 | **Batterie Li-ion** | *(TODO jour J)* | — | 3,7 V / 0,62 Ah (621 mAh) ; réutilisable comme source 3,3–5 V pour MCU/Raspberry/Arduino | *(TODO jour J)* |
| 8 | **Régulateur de tension / DC-DC** | *(TODO jour J)* | TI / Ricoh / Semtech | Conversion 3,7 V → 3,3 V (MCU) et/ou 5 V ; identifier les rails de sortie | *(TODO jour J)* |
| 9 | **Circuit de charge USB** | *(TODO jour J)* | TI BQ24xxx / MPS | Gestion de la charge via connecteur USB ; réutilisable pour alimenter tout projet DIY | *(TODO jour J)* |
| 10 | **Mémoire flash externe** | *(TODO jour J)* | Winbond / Macronix | Stockage firmware ou logs de mesure ; accès SPI | *(TODO jour J)* |
| 11 | **Convertisseur USB/TTL** | *(TODO jour J)* | CP2102 / CH340 / FTDI | Passerelle USB↔UART pour debug/flash ; peut servir de pont série DIY | *(TODO jour J)* |
| 12 | **Boutons / LEDs** | — | — | UI minimaliste ; 2–3 boutons (mesure, mode, power), LED(s) d'état | — |
| 13 | **Écran (si présent)** | *(TODO jour J)* | — | Affichage du résultat ; à confirmer (OLED SSD1306 / LCD ST7789 ?) | *(TODO jour J)* |
| 14 | **IMU / capteur d'inclinaison (si présent)** | *(TODO jour J)* | Bosch BMI160 / ST LSM6 | Détection de l'orientation du capteur, compensation de l'angle de mesure | *(TODO jour J)* |
| 15 | **Connecteurs externes** | — | — | Prise de charge USB, éventuels test pads UART/SWD ; cartographier précisément | — |

---

## Notes de démontage

*(TODO jour J — compléter en temps réel pendant l'ouverture du produit)*

- **Nombre de PCB** : ___
- **Dimensions PCB principal** : ___ mm × ___ mm
- **Photos archivées dans** : [`../assets/`](../assets/)
- **Marquages imprimés sur le PCB** : ___
- **Observations particulières** : ___

---

## Procédure de relevé des références

1. Ouvrir le produit (vis cruciformes, éventuellement clips plastiques — ne pas forcer).
2. Photographier chaque face du PCB **avant** tout démontage de composant.
3. Pour chaque CI discret : lire le marquage imprimé en lumière rasante / loupe.
4. Rechercher la datasheet sur le site du fabricant, [Datasheet360](https://www.datasheet360.com), ou
   [AllDatasheet](https://www.alldatasheet.com).
5. Archiver le PDF dans [`datasheets/`](datasheets/) avec le nom `<référence>.pdf`.
6. Compléter le tableau ci-dessus ligne par ligne.
