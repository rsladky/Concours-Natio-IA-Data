# Rétro-ingénierie — Schéma fonctionnel de principe

> Schéma basé sur la fonction documentée du produit. À affiner avec les références réelles le jour J.

---

## Schéma de principe (Mermaid)

```mermaid
flowchart TD
    subgraph ALIMENTATION["⚡ Alimentation"]
        BAT["Batterie Li-ion\n3,7 V / 0,62 Ah"]
        CHG["Circuit de charge\nUSB (BQ24xxx)"]
        REG["Régulateur / DC-DC\n3,7 V → 3,3 V & 5 V"]
        USB_C["Connecteur USB\n(charge)"]
        USB_C --> CHG --> BAT --> REG
    end

    subgraph MCU["🧠 MCU / SoC principal"]
        CPU["MCU principal\n(TODO : référence)"]
        FLASH["Flash externe\nSPI"]
        CPU <-->|SPI| FLASH
    end

    subgraph MESURE["📐 Chaîne de mesure"]
        LASER["Diode laser\n650 nm — Classe 3R"]
        LENTILLE["Lentille cylindrique\n→ ligne laser"]
        CAM["Capteur CMOS\n(module caméra)"]
        OPTIQUE["Optique focale fixe"]
        LASER --> LENTILLE
        LENTILLE -->|lumière structurée| SURFACE["Surface à mesurer"]
        SURFACE -->|image déformée| OPTIQUE --> CAM
    end

    subgraph COMM["📡 Communication"]
        BT["Module Bluetooth\nBLE 4.x / 5.x"]
        USBTL["Convertisseur\nUSB/TTL\n(debug/flash)"]
        APP["Application\nmobile / PC"]
        BT <-->|BLE| APP
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

    CPU <-->|UART / SPI / I2C| BT
    CPU <-->|MIPI CSI / DVP / SPI| CAM
    CPU -->|GPIO / PWM| LASER
    CPU <-->|GPIO| BTN
    CPU -->|GPIO| LED
    CPU <-->|I2C / SPI| ECRAN
    CPU <-->|UART| USBTL

    CPU -->|calcul profil| BT
```

---

## Caractéristiques clés (à compléter le jour J)

| Paramètre | Valeur connue | À mesurer/confirmer |
|-----------|---------------|---------------------|
| Tension batterie | 3,7 V nominale | Tension réelle à la charge |
| Capacité batterie | 0,62 Ah (620 mAh) | Marque/référence cellule |
| Tension logique MCU | 3,3 V (probable) | À mesurer sur le rail |
| Tension laser | ~3,3 V ou 5 V | À mesurer sur les pads driver |
| Interface caméra → MCU | DVP / MIPI CSI (probable) | Traces PCB ou marquage |
| Interface BT → MCU | UART ou SPI | À confirmer par traces |
| Classe laser | 3R (documenté) | Puissance optique max ? |
| Autonomie | ~500 mesures | À vérifier |

---

## Interfaces bus disponibles (à cartographier)

| Bus | Rôle actuel | Disponibilité réemploi |
|-----|-------------|------------------------|
| UART (via USB/TTL) | Debug / Flash firmware | ✅ Accès probable via test pads |
| SWD / JTAG | Debug MCU bas niveau | ✅ Test pads à localiser |
| I²C | Écran, IMU éventuel | 🔍 À vérifier |
| SPI | Flash externe, caméra ? | 🔍 À vérifier |
| GPIO | Laser, boutons, LEDs | ✅ Identifiables par traces |
