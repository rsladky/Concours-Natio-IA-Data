# Champ des possibles — Extensions et ajouts potentiels

> Ce que l'on **pourrait ajouter** au système pour étendre ses capacités, et **où se brancher**
> pour le faire. Basé sur les bus et I/O typiques d'un MCU de cette classe.

---

## Extensions matérielles envisageables

| # | Extension | Comment s'y brancher | Difficulté | Valeur ajoutée |
|---|-----------|----------------------|------------|----------------|
| E1 | **Raspberry Pi / SBC** (host de traitement) | USB/TTL ou UART test pads | Faible | Traitement lourd, affichage, WiFi |
| E2 | **Capteur ToF** (VL53L1X) | I²C libre | Faible | Distance absolue en complément du profil |
| E3 | **IMU 6 axes** (BMI160) | I²C / SPI | Faible | Compensation d'inclinaison, détection de mouvement |
| E4 | **Écran OLED** (SSD1306) | I²C (si pas déjà câblé) | Faible | Affichage local du profil / résultat |
| E5 | **Module WiFi** (ESP8266 / ESP32) | UART | Faible | Upload cloud, tableau de bord web |
| E6 | **Deuxième caméra** | SPI ou I²C MIPI | Moyenne | Stéréovision, profil 3D plus riche |
| E7 | **Haut-parleur / buzzer** | GPIO + PWM | Faible | Alerte sonore si seuil dépassé |
| E8 | **Capteur de température** | I²C (1-Wire) | Faible | Compensation thermique des mesures |
| E9 | **Connecteur SD card** | SPI | Faible | Stockage de masse des profils mesurés |
| E10 | **Connexion PC via USB** | Convertisseur USB/TTL existant | Aucune | Pipeline Data/IA côté PC |

---

## I/O disponibles non utilisées (à cartographier le jour J)

*(TODO jour J — à compléter après lecture des traces et de la datasheet MCU)*

| Broche MCU | Type | Niveau | Utilisation actuelle | Disponible pour ajout |
|------------|------|--------|---------------------|----------------------|
| *(TODO)* | GPIO | 3,3 V | Libre | ✅ |
| *(TODO)* | I²C SDA | 3,3 V | ? | 🔍 |
| *(TODO)* | I²C SCL | 3,3 V | ? | 🔍 |
| *(TODO)* | SPI MOSI/MISO/SCK | 3,3 V | Flash externe | ✅ (ajout en parallèle) |
| *(TODO)* | UART TX/RX | 3,3 V | BT ou debug | 🔍 |
| *(TODO)* | ADC | 3,3 V | Batterie (mesure tension) | ✅ potentiellement |

---

## Points d'extension physiques recommandés

Pour connecter une extension sans modifier le PCB de façon invasive :

1. **Test pads UART / SWD** : souder des fils fins directement → connexion propre et réversible.
2. **Connecteur USB existant** : si USB/TTL présent, utiliser le USB pour passer des données vers
   un Raspberry Pi ou un PC sans modification HW.
3. **Pins de la flash SPI** : brancher en parallèle (ne pas oublier la résistance de pull-up si
   besoin de chip-select distinct).
4. **Alimentation 3,3 V du régulateur** : prendre l'alimentation pour les modules externes depuis
   le rail 3,3 V (test pad ou via), avec une résistance de limitation si le courant total dépasse
   la capacité du régulateur.

---

## Recommandation pour le POC

Pour le POC Data/IA, l'extension la plus simple et la plus impactante est :

> **E10 — Connexion PC via USB** (aucune modification HW)  
> Le flux image (ou les profils calculés) sort par UART → USB/TTL → PC Python.  
> Le pipeline ML tourne côté PC. Aucun composant ajouté, réemploi maximal.

En cas de besoin de puissance de calcul embarquée (démo autonome) :

> **E1 — Raspberry Pi Zero W** branché sur l'UART  
> Traitement Python + affichage sur écran SSD1306 (E4) + connexion WiFi (nativement sur Pi Zero W).
