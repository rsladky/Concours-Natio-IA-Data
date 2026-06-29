# Champ des possibles — Schéma fonctionnel « en l'état + extensions »

---

## Schéma complet (Mermaid)

```mermaid
flowchart TD
    subgraph PRODUIT["🔵 SCANDIAG® — Fonctions en l'état"]
        direction TB

        subgraph ALIM["⚡ Alimentation"]
            BAT["Li-ion 3,7V / 620mAh"]
            CHG["Charge USB"]
            REG["Régulateur 3,3V"]
            BAT --> REG
            CHG --> BAT
        end

        subgraph MESURE["📐 Mesure (cœur de valeur)"]
            LASER["🔴 Laser ligne\n650nm Classe 3R"]
            CAM["📷 Caméra CMOS"]
            LASER -->|lumière structurée| SURFACE["Surface\n(objet à mesurer)"]
            SURFACE -->|image déformée| CAM
        end

        MCU["🧠 MCU\n(calcul profil,\ncontrôle laser/caméra)"]
        BT["📡 Module BT BLE"]
        FLASH["💾 Flash SPI"]
        BTNS["🔘 Boutons / LEDs"]
        ECRAN["🖥️ Écran\n(si présent)"]

        REG -->|3,3V| MCU
        REG -->|3,3V| BT
        REG -->|3,3V| LASER
        REG -->|3,3V| CAM
        MCU <-->|DVP/CSI| CAM
        MCU -->|GPIO/PWM| LASER
        MCU <-->|UART/SPI| BT
        MCU <-->|SPI| FLASH
        MCU <-->|GPIO| BTNS
        MCU <-->|I2C/SPI| ECRAN
    end

    subgraph USB_OUT["🔌 Sortie USB (accès existant)"]
        USBTL["Convertisseur\nUSB/TTL"]
        MCU <-->|UART| USBTL
    end

    subgraph EXTENSIONS["🟢 Extensions possibles"]
        direction TB

        E_PC["💻 PC / Raspberry Pi\n(pipeline Data/IA Python)"]
        E_WIFI["📶 Module WiFi\n(ESP8266 → UART)"]
        E_TOF["📏 Capteur ToF\n(VL53L1X → I²C)"]
        E_IMU["🧭 IMU 6 axes\n(BMI160 → I²C/SPI)"]
        E_OLED["📟 Écran OLED\n(SSD1306 → I²C)"]
        E_SD["💿 Carte SD\n(→ SPI)"]
        E_APP["📱 App mobile\n(→ BLE existant)"]
    end

    USBTL <-->|USB → Python| E_PC
    MCU <-->|UART libre| E_WIFI
    MCU <-->|I²C libre| E_TOF
    MCU <-->|I²C/SPI libre| E_IMU
    MCU <-->|I²C libre| E_OLED
    MCU <-->|SPI libre| E_SD
    BT <-->|BLE| E_APP

    style PRODUIT fill:#dbeafe,stroke:#3b82f6,color:#1e3a8a
    style EXTENSIONS fill:#dcfce7,stroke:#16a34a,color:#14532d
    style USB_OUT fill:#fef9c3,stroke:#ca8a04,color:#713f12
```

---

## Légende

| Couleur | Signification |
|---------|--------------|
| 🔵 Bleu | Fonctions disponibles **en l'état** dans le SCANDIAG |
| 🟡 Jaune | Point de sortie **existant** (USB/TTL) utilisable sans modification |
| 🟢 Vert | **Extensions** potentielles (composants à ajouter si nécessaire) |

---

## Points de connexion prioritaires pour le POC

| Connexion | Type | Modification HW | Priorité |
|-----------|------|-----------------|----------|
| USB/TTL existant → PC | USB | Aucune | ⭐⭐⭐⭐⭐ |
| UART MCU → ESP8266 WiFi | Fil | Très faible | ⭐⭐⭐ |
| I²C MCU → TOF VL53L1X | Fils | Faible | ⭐⭐ |
| SPI → Carte SD | Fils | Faible | ⭐⭐ |
| BLE → App mobile | Aucune | Aucune | ⭐⭐⭐⭐ |
