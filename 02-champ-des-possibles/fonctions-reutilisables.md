# Champ des possibles — Fonctions matérielles réutilisables

> Liste exhaustive des fonctions hardware exploitables **en l'état**, sans modification matérielle
> majeure. C'est la base sur laquelle l'idéation doit s'appuyer.

---

## Vue synthétique

| # | Fonction | Composants concernés | Réemploi direct | Valeur potentielle |
|---|----------|----------------------|-----------------|-------------------|
| F1 | **Triangulation laser (profilométrie)** | Laser + lentille cylindrique + caméra CMOS + MCU | ✅ Oui | ⭐⭐⭐⭐⭐ |
| F2 | **Acquisition image** | Capteur CMOS + optique | ✅ Oui (driver caméra) | ⭐⭐⭐⭐ |
| F3 | **Projection d'une ligne laser** | Diode laser + lentille cylindrique | ✅ Oui | ⭐⭐⭐⭐ |
| F4 | **Communication Bluetooth Low Energy** | Module BT | ✅ Oui | ⭐⭐⭐⭐ |
| F5 | **Calcul embarqué** | MCU | ✅ Oui (reflaçable) | ⭐⭐⭐⭐⭐ |
| F6 | **Stockage local** | Flash externe | ✅ Oui | ⭐⭐⭐ |
| F7 | **Source d'alimentation autonome** | Batterie Li-ion + circuit de charge | ✅ Oui | ⭐⭐⭐⭐ |
| F8 | **Charge par USB** | Circuit de charge | ✅ Oui | ⭐⭐⭐ |
| F9 | **Interface utilisateur minimale** | Boutons + LEDs | ✅ Oui | ⭐⭐ |
| F10 | **Affichage résultat** | Écran (si présent) | 🔍 À confirmer | ⭐⭐⭐ |
| F11 | **Debug / flash série** | Convertisseur USB/TTL | ✅ Oui (pont UART) | ⭐⭐ |

---

## Détail des fonctions

### F1 — Triangulation laser (profilométrie)
La **chaîne complète** de mesure de profil par lumière structurée est disponible en un seul bloc :
- Source laser structurée (ligne rouge)
- Capteur image pour lire la déformation de la ligne
- MCU pour calculer le profil de hauteur

C'est la fonction la plus précieuse : elle transforme le SCANDIAG en **profilomètre / scanner
3D à triangulation** réutilisable dans n'importe quel domaine nécessitant une mesure de forme
ou d'usure de surface.

### F2 — Acquisition image
Le capteur CMOS avec son optique peut être exploité comme **caméra industrielle compacte** :
inspection visuelle, détection de présence, lecture de codes, etc.

### F3 — Projection ligne laser
La diode laser + lentille cylindrique produit une ligne droite précise. Réutilisable :
- En scanner 3D (voir F1)
- En métrologie (alignement, planéité)
- En détection de niveau (liquide, matière)

### F4 — Bluetooth Low Energy
Le module BT permet de transmettre des données sans fil vers un smartphone ou un PC. Applications :
IoT industriel, capteur connecté, objet communicant autonome.

### F5 — Calcul embarqué (MCU)
Après reflash, le MCU peut exécuter n'importe quelle logique embarquée adaptée au nouveau projet :
extraction de profil laser, filtrage, détection d'anomalie locale, protocoles de communication.

### F6 — Stockage flash
La mémoire flash SPI stocke firmware et/ou données. Réutilisable pour logging local, cache de
mesures avant envoi BT.

### F7 — Alimentation autonome
La cellule Li-ion 3,7 V / 620 mAh et son circuit de charge USB offrent une **plateforme
d'alimentation portable complète** pour tout projet électronique 3,3–5 V.

### F8 — Charge USB
Le circuit de charge permet de recharger le système via USB sans matériel supplémentaire.

### F9 — Interface utilisateur
Les boutons et LEDs permettent une interaction minimale : démarrage de mesure, changement de mode,
indication d'état. Suffisant pour un produit embarqué autonome.

### F10 — Affichage
Si un écran est présent (OLED SSD1306 ou LCD), il peut afficher des mesures ou des résultats
directement sur le device, sans dépendance à un smartphone.

### F11 — Debug / passerelle série
Le convertisseur USB/TTL, s'il est présent, sert à la fois d'interface de flash du firmware et
de pont UART → USB réutilisable dans d'autres projets.
