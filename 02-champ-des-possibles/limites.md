# Champ des possibles — Limites fonctionnelles

> Documenter les limites honnêtement est essentiel pour crédibiliser le dossier auprès de FACOM.

---

## Limites identifiées

### L1 — Résolution et précision de la triangulation

La précision du profilomètre dépend de :
- L'**angle entre le laser et la caméra** (angle de triangulation) — fixé par le design mécanique.
- La **résolution du capteur CMOS** et la qualité de l'optique.
- La **stabilité du laser** (puissance, stabilité thermique).

Le SCANDIAG est calibré pour mesurer des épaisseurs de disques de frein (quelques mm) à une
distance de travail fixe (~5–15 cm). En dehors de cette plage, la précision se dégrade.

**Impact réemploi :** mesure précise seulement dans la gamme de hauteur / distance d'origine.
Pour d'autres géométries (pièces très grandes ou très petites), une recalibration est nécessaire.

---

### L2 — Distance de travail fixe

L'optique est conçue pour une distance caméra-surface fixe. La profondeur de champ est limitée.
Au-delà de ~±3 cm autour de la distance nominale, la ligne laser devient floue et la précision
chute.

**Impact réemploi :** le scanner ne fonctionne bien que pour des objets d'une certaine taille
et à une distance fixe. Il n'est pas adapté à la numérisation de grands objets ou à la mesure
longue portée.

---

### L3 — Laser classe 3R (risque oculaire)

La diode laser est classée **3R** : regarder directement dans le faisceau est dangereux.
L'utilisation dans des espaces publics ou par des non-avertis nécessite des protections physiques
(carter, détecteur de présence, interverrouillage).

**Impact réemploi :** tout produit final incluant le laser doit gérer la sécurité oculaire. Cela
peut compliquer une utilisation grand public.

---

### L4 — Capacité batterie limitée

620 mAh est suffisant pour 500 mesures courtes, mais insuffisant pour une utilisation continue
prolongée (ex. : monitoring permanent). Une application IoT de surveillance doit prévoir une
gestion fine de l'énergie (sleep modes, intervalles de mesure espacés).

---

### L5 — Accès au firmware propriétaire

Le firmware d'origine est protégé par la propriété intellectuelle de FACOM. Le re-flash avec un
firmware alternatif est techniquement possible (si le Read Protection n'est pas activé), mais
implique la **perte du fonctionnement d'origine**. Dans le cadre du concours RSE, cela est
acceptable (réemploi complet), mais doit être documenté.

---

### L6 — Interface caméra vers MCU propriétaire

Le protocole entre le capteur CMOS et le MCU peut être propriétaire (registres de configuration
spécifiques au modèle). Sans la datasheet du capteur (à trouver lors du démontage), la
réutilisation du flux caméra nécessite une phase de rétro-ingénierie supplémentaire.

**Contournement :** exfiltrer les images via USB/TTL (si le débit le permet) ou remplacer le MCU
par un Raspberry Pi Pi Zero 2W qui supporte nativement la caméra CSI.

---

### L7 — Connectivité WiFi absente

Le SCANDIAG ne dispose que du Bluetooth. Pour envoyer des données vers le cloud ou un dashboard
web, il faut ajouter un module WiFi (ESP8266) ou passer par un smartphone intermédiaire.

---

### L8 — Mécanique dédiée automobile

Le boîtier est conçu pour s'insérer entre les rayons de roue. Il n'est pas conçu pour s'adapter
à d'autres surfaces. Un réemploi dans un autre domaine nécessite probablement un **adaptateur
mécanique** ou de **retirer la carte du boîtier**.

---

## Tableau de synthèse des limites

| Limite | Sévérité | Contournement |
|--------|----------|---------------|
| L1 — Précision hors plage nominale | Moyenne | Recalibration + mire de calibration |
| L2 — Distance de travail fixe | Faible–Moyenne | Support mécanique ajusté |
| L3 — Laser 3R (sécurité) | Haute | Carter + interverrouillage |
| L4 — Batterie 620 mAh | Faible | Sleep modes, recharge USB fréquente |
| L5 — Firmware propriétaire | Faible (pour CE) | Re-flash avec firmware open-source |
| L6 — Interface caméra propriétaire | Moyenne | Datasheet + rétro-ingénierie des registres |
| L7 — Pas de WiFi | Faible | Module ESP8266 sur UART |
| L8 — Mécanique dédiée | Faible | Adaptateur imprimé 3D ou sortie de carte |
