"""
analyse_ml.py — Classification ML de l'état de surface à partir du profil

Pipeline :
  1. Extraire des features du profil de hauteur (statistiques, FFT).
  2. Entraîner un classificateur (RandomForest) sur des profils labellisés.
  3. Prédire l'état d'une nouvelle mesure.

Classes de surface :
  - 'neuf'      : surface plane, rugosité minimale
  - 'use'       : profil avec creux, rugosité modérée
  - 'tres_use'  : profil irrégulier, rugosité élevée, profondeur importante
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import cross_val_score
import pickle
from pathlib import Path


# ── Feature extraction ──────────────────────────────────────────────────────

def extraire_features(profil_mm: np.ndarray) -> np.ndarray:
    """Extrait un vecteur de features numériques à partir d'un profil 1D.

    Features calculées (total : 14) :
      Statistiques de base : min, max, étendue, moyenne, écart-type
      Rugosité : Ra (ISO 4287), Rq (RMS)
      Forme : skewness, kurtosis
      Fréquentiel : 5 premières amplitudes FFT normalisées

    Args:
        profil_mm: Tableau de hauteurs en mm (peut contenir NaN).

    Returns:
        Vecteur numpy float64 de 14 features.
    """
    valides = profil_mm[~np.isnan(profil_mm)]

    if len(valides) < 10:
        return np.zeros(14)

    moyenne = float(np.mean(valides))
    ecart_type = float(np.std(valides))
    mini = float(np.min(valides))
    maxi = float(np.max(valides))
    etendue = maxi - mini

    # Rugosité Ra et Rq
    ra = float(np.mean(np.abs(valides - moyenne)))
    rq = float(np.sqrt(np.mean((valides - moyenne) ** 2)))

    # Forme statistique
    if ecart_type > 1e-9:
        normalise = (valides - moyenne) / ecart_type
        skewness = float(np.mean(normalise ** 3))
        kurtosis = float(np.mean(normalise ** 4))
    else:
        skewness, kurtosis = 0.0, 3.0  # Surface parfaitement plane

    # Analyse fréquentielle (FFT) — 5 premières harmoniques
    fft_mag = np.abs(np.fft.rfft(valides - moyenne))
    # Normaliser par le nombre de points
    fft_norm = fft_mag / (len(valides) / 2)
    # Prendre les 5 premières amplitudes (hors composante DC)
    n_harmoniques = 5
    if len(fft_norm) > n_harmoniques:
        harmoniques = fft_norm[1:n_harmoniques + 1]
    else:
        harmoniques = np.pad(fft_norm[1:], (0, n_harmoniques - len(fft_norm) + 1))

    features = np.array([
        mini, maxi, etendue, moyenne, ecart_type,
        ra, rq,
        skewness, kurtosis,
        *harmoniques[:n_harmoniques],
    ], dtype=float)

    return features


# ── Génération de données d'entraînement synthétiques ───────────────────────

def generer_dataset_synthetique(
    n_par_classe: int = 200,
    longueur: int = 640,
    rng: np.random.Generator | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Génère un dataset synthétique de profils pour entraînement.

    Simule trois classes d'état de surface :
      - 'neuf'     : profil quasi-plat, faible bruit
      - 'use'      : profil avec creux de profondeur modérée
      - 'tres_use' : profil très irrégulier, forte rugosité

    Args:
        n_par_classe: Nombre d'exemples par classe.
        longueur: Longueur du profil (nombre de colonnes).
        rng: Générateur aléatoire (pour reproductibilité).

    Returns:
        Tuple (X, y) :
          X : matrice (n_samples, n_features) float64
          y : vecteur (n_samples,) str avec les labels de classe
    """
    if rng is None:
        rng = np.random.default_rng(seed=42)

    X_liste, y_liste = [], []
    x = np.linspace(0, 2 * np.pi, longueur)

    for _ in range(n_par_classe):
        # Classe 'neuf' : surface quasi-plane
        profil = rng.normal(0, 0.02, longueur)
        X_liste.append(extraire_features(profil))
        y_liste.append("neuf")

        # Classe 'use' : creux locaux + bruit modéré
        profil = (
            rng.normal(0, 0.05, longueur)
            + rng.uniform(0.1, 0.5) * np.sin(rng.uniform(1, 4) * x)
            - rng.uniform(0.1, 0.3)
        )
        X_liste.append(extraire_features(profil))
        y_liste.append("use")

        # Classe 'tres_use' : profil très irrégulier
        profil = (
            rng.normal(0, 0.15, longueur)
            + rng.uniform(0.3, 1.0) * np.sin(rng.uniform(2, 6) * x)
            + rng.uniform(0.5, 1.5) * np.cos(rng.uniform(1, 3) * x + rng.uniform(0, np.pi))
            - rng.uniform(0.5, 1.5)
        )
        X_liste.append(extraire_features(profil))
        y_liste.append("tres_use")

    return np.array(X_liste), np.array(y_liste)


# ── Modèle ───────────────────────────────────────────────────────────────────

class ClassificateurUsure:
    """Classificateur d'état d'usure de surface basé sur RandomForest.

    Usage :
        clf = ClassificateurUsure()
        clf.entrainer_sur_donnees_synthetiques()
        etat = clf.predire(profil_mm)
    """

    LABELS_FR = {
        "neuf": "Neuf ✅",
        "use": "Usé ⚠️",
        "tres_use": "Très usé ❌",
    }

    def __init__(self, n_arbres: int = 100, seed: int = 42):
        self.modele = RandomForestClassifier(
            n_estimators=n_arbres,
            random_state=seed,
            class_weight="balanced",
        )
        self.est_entraine = False

    def entrainer(self, X: np.ndarray, y: np.ndarray) -> dict:
        """Entraîne le modèle et retourne les métriques de validation croisée.

        Args:
            X: Matrice de features (n_samples, n_features).
            y: Labels de classe (n_samples,).

        Returns:
            Dictionnaire avec accuracy_cv_mean et accuracy_cv_std.
        """
        scores = cross_val_score(self.modele, X, y, cv=5, scoring="accuracy")
        self.modele.fit(X, y)
        self.classes_ = self.modele.classes_
        self.est_entraine = True

        return {
            "accuracy_cv_mean": float(scores.mean()),
            "accuracy_cv_std": float(scores.std()),
            "n_classes": len(self.classes_),
            "classes": list(self.classes_),
        }

    def entrainer_sur_donnees_synthetiques(
        self, n_par_classe: int = 200, seed: int = 42
    ) -> dict:
        """Raccourci : génère les données synthétiques et entraîne le modèle."""
        rng = np.random.default_rng(seed)
        X, y = generer_dataset_synthetique(n_par_classe=n_par_classe, rng=rng)
        return self.entrainer(X, y)

    def predire(self, profil_mm: np.ndarray) -> dict:
        """Classifie l'état d'un profil de hauteur.

        Args:
            profil_mm: Profil de hauteur en mm (tableau 1D).

        Returns:
            Dictionnaire avec :
              - 'classe' : classe prédite ('neuf', 'use', 'tres_use')
              - 'label_fr' : libellé français avec emoji
              - 'probabilites' : dict {classe: probabilité}
              - 'features' : vecteur de features utilisé
        """
        if not self.est_entraine:
            raise RuntimeError("Modèle non entraîné. Appeler .entrainer() d'abord.")

        features = extraire_features(profil_mm).reshape(1, -1)
        classe = self.modele.predict(features)[0]
        probas = self.modele.predict_proba(features)[0]

        return {
            "classe": classe,
            "label_fr": self.LABELS_FR.get(classe, classe),
            "probabilites": dict(zip(self.modele.classes_, probas.tolist())),
            "features": features[0],
            "confiance": float(max(probas)),
        }

    def sauvegarder(self, chemin: str) -> None:
        """Sauvegarde le modèle entraîné (pickle)."""
        if not self.est_entraine:
            raise RuntimeError("Rien à sauvegarder : modèle non entraîné.")
        with open(chemin, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def charger(cls, chemin: str) -> "ClassificateurUsure":
        """Charge un modèle sauvegardé."""
        with open(chemin, "rb") as f:
            return pickle.load(f)
