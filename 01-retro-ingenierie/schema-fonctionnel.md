# Rétro-ingénierie — Schéma fonctionnel de principe

> Schéma mis à jour avec les références réelles identifiées lors du démontage (29/06/2026).

---

## Schéma de principe (Mermaid)

```mermaid
flowchart TD
    subgraph ALIMENTATION["⚡ Alimentation"]
        BAT["EEMB LP602248\nLi-Po 3,7V / 620mAh"]
        CHG["Contrôleur charge\nVDY6/B301"]
        REG["DC-DC LGCS/B901\n3,7V → 3,3V & 5V"]
        USB_C["USB Mini-B\n5V / 500mA"]
        USB_C --> CHG --> BAT --> REG
    end

    subgraph MCU["🧠 STM32F429 — ARM Cortex-M4 @ 180 MHz"]
        CPU["STM32F429\n2MB Flash / 256KB RAM"]
        SDRAM1["SDRAM Micron\n9CA15/RB151\n(buffer frames)"]
        SDRAM2["SDRAM ISSI\nIS42Sxxxx\n(buffer frames)"]
        CPU <-->|FMC| SDRAM1
        CPU <-->|FMC| SDRAM2
    end

    subgraph MESURE["📐 Chaîne de mesure"]
        LASER["Diode laser\n≤5mW — Classe 3R"]
        LENTILLE["Lentille cylindrique\n→ ligne laser"]
        CAM["Capteur CMOS\n(TODO ref)\nMCLK 24MHz"]
        OPTIQUE["Optique focale fixe"]
        LASER --> LENTILLE
        LENTILLE -->|lumière structurée| SURFACE["Surface à mesurer"]
        SURFACE -->|image déformée| OPTIQUE --> CAM
    end

    subgraph COMM["📡 Communication"]
        BT["Silicon Labs WT12-A\nBT Classic 2.1+EDR\niWRAP / SPP"]
        APP["Application\nmobile / PC\n(port série virtuel)"]
        BT <-->|SPP BT| APP
    end

    subgraph UI["🖥️ Interface utilisateur"]
        BTN["Boutons\n(mesure, mode, power)"]
        LED["LEDs d'état"]
        ECRAN["Écran\n(OLED / LCD ?)"]
    end

    REG -->|3,3 V| CPU
    REG -->|3,3 V| BT
    REG -->|3,3 V / 5 V| LASER
    REG -->|3,3 V| CAM

    CPU <-->|UART| BT
    CPU <-->|DCMI + MCLK 24MHz| CAM
    CPU -->|GPIO / PWM| LASER
    CPU <-->|GPIO| BTN
    CPU -->|GPIO| LED
    CPU <-->|SWD SWDIO/SWDCLK| USBTL["Test pads SWD\n(flash/debug)"]

    CPU -->|calcul profil| BT
```

---

## Caractéristiques clés (à compléter le jour J)

| Paramètre | Valeur connue | À mesurer/confirmer |
|-----------|---------------|---------------------|
| Tension batterie | 3,7 V nominale | **EEMB LP602248 confirmé** |
| Capacité batterie | 620 mAh / 2,3 Wh | **Confirmé étiquette batterie** |
| MCU | STM32F429 ARM Cortex-M4 | **Confirmé marquage img#9** |
| Fréquence MCU | 180 MHz (max) | Via PLL interne depuis HSE |
| SDRAM | Micron 9CA15 + ISSI IS42S | **Confirmé img#9** |
| Oscillateur caméra | 24 MHz | **Confirmé img#5 — MCLK capteur** |
| Interface caméra → MCU | **DCMI** (STM32F429 natif) | Confirmé par MCU |
| Interface BT → MCU | **UART** (iWRAP WT12-A) | Confirmé par WT12-A |
| Classe laser | 3R, ≤5mW | **Confirmé étiquette produit** |
| Connecteur de charge | USB Mini-B 5V/500mA | **Confirmé étiquette + fiche** |
| Tension logique MCU | 3,3 V | À mesurer (probable pour STM32F429) |

---

## Interfaces bus disponibles (à cartographier)

| Bus | Rôle actuel | Disponibilité réemploi |
|-----|-------------|------------------------|
| UART (via USB/TTL) | Debug / Flash firmware | ✅ Accès probable via test pads |
| SWD / JTAG | Debug MCU bas niveau | ✅ Test pads à localiser |
| I²C | Écran, IMU éventuel | 🔍 À vérifier |
| SPI | Flash externe, caméra ? | 🔍 À vérifier |
| GPIO | Laser, boutons, LEDs | ✅ Identifiables par traces |
