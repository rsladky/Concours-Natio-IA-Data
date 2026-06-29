# Concours National Informatique Ynov — FACOM SCANDIAG® : Réemploi RSE

> **Événement :** Concours National Ynov Informatique — 7h en équipe  
> **Sujet :** Donner une seconde vie aux composants du FACOM SCANDIAG® (DX.TSCANPB)  
> **Commanditaire :** Direction RSE de FACOM (groupe Stanley Black & Decker)

---

## Équipe

| Nom | Classe | Campus |
|-----|--------|--------|
| *(TODO jour J)* | | |
| | | |
| | | |
| | | |
| | | |

---

## Navigation du dossier

| Étape | Dossier | Contenu |
|-------|---------|---------|
| 1 — Rétro-ingénierie | [`01-retro-ingenierie/`](01-retro-ingenierie/) | Composants, schéma fonctionnel, accès flash |
| 2 — Champ des possibles | [`02-champ-des-possibles/`](02-champ-des-possibles/) | Fonctions réutilisables, extensions, limites |
| 3 — Idéation | [`03-ideation/`](03-ideation/) | 7 concepts notés + concept retenu |
| 4 — Preuve de concept | [`04-poc/`](04-poc/) | Pipeline Data/IA Python (profilomètre laser) |
| 5 — Dossier final | [`05-dossier-final/`](05-dossier-final/) | Document consolidé remis à FACOM |

---

## Contexte produit

Le **SCANDIAG® (DX.TSCANPB)** est un analyseur d'usure des disques de frein et des pneus.  
Il fonctionne par **triangulation laser** : une ligne laser (classe 3R) est projetée sur la
surface ; une **caméra CMOS** observe la déformation de cette ligne ; un **MCU** calcule le
profil de hauteur. La communication vers l'application mobile s'effectue via **Bluetooth®**.
L'autonomie est assurée par une **batterie Li-ion 3,7 V / 0,62 Ah** (~500 mesures/charge).

Le produit n'est plus commercialisé. FACOM refuse de mettre le stock au rebut pour des raisons
RSE et mandate Ynov pour imaginer des **secondes vies** pour ses composants.

---

## Concept retenu

**Profilomètre / Scanner 3D open-source à ligne laser**  
Réemploi de la chaîne caméra+laser+MCU comme capteur de profil de surface générique,
alimentant un **pipeline Data/IA** (extraction de profil → classification ML → rapport).  
Application : mesure d'usure tous corps (outils, semelles, pièces industrielles), contrôle
qualité léger, outil pédagogique. Voir [`03-ideation/concepts.md`](03-ideation/concepts.md).

---

## ⚠️ Règles de sécurité

- **Batterie Li-ion** : ne pas court-circuiter, surveiller toute chauffe anormale.
- **Laser classe 3R** : ne jamais regarder directement dans le faisceau. Porter des lunettes de
  protection adaptées à la longueur d'onde lors des manipulations actives.
- **Aucun composant jeté** : tout ce qui sort du produit reste dans la zone de travail (RSE oblige).
- **Documentation continue** : photos et notes au fil de l'eau, ne pas tout garder pour la fin.
