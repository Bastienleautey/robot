# =============================================================================
# robot.py — Classes Robot et ses 4 types (Assaut, Défenseur, Agile, Équilibré)
# =============================================================================

import random
from exceptions import StatsInvalidesException


# ─────────────────────────────────────────────────────────────────────────────
# Validation des statistiques
# ─────────────────────────────────────────────────────────────────────────────

def valider_stats(pv, attaque, defense, vitesse):
    """
    Vérifie que les stats respectent toutes les contraintes de la consigne.
    Lève StatsInvalidesException si une règle est violée.
    """
    if not (50 <= pv <= 150):
        raise StatsInvalidesException(f"PV invalide : {pv} (doit être entre 50 et 150)")
    if not (10 <= attaque <= 50):
        raise StatsInvalidesException(f"Attaque invalide : {attaque} (doit être entre 10 et 50)")
    if not (5 <= defense <= 40):
        raise StatsInvalidesException(f"Défense invalide : {defense} (doit être entre 5 et 40)")
    if not (5 <= vitesse <= 40):
        raise StatsInvalidesException(f"Vitesse invalide : {vitesse} (doit être entre 5 et 40)")
    if pv + attaque + defense + vitesse != 100:
        raise StatsInvalidesException(
            f"Total invalide : {pv + attaque + defense + vitesse} (doit être exactement 100)"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Classe de base Robot
# ─────────────────────────────────────────────────────────────────────────────

class Robot:
    """Classe de base représentant un robot combattant."""

    TYPES_VALIDES = ["Assaut", "Défenseur", "Agile", "Équilibré"]

    def __init__(self, nom, type_robot, pv, attaque, defense, vitesse):
        # Validation du nom
        if not (3 <= len(nom) <= 20):
            raise ValueError(f"Nom invalide : '{nom}' (doit contenir entre 3 et 20 caractères)")
        if type_robot not in self.TYPES_VALIDES:
            raise ValueError(f"Type invalide : '{type_robot}' (doit être parmi {self.TYPES_VALIDES})")

        # Validation des stats
        valider_stats(pv, attaque, defense, vitesse)

        self.nom = nom
        self.type = type_robot
        self.pv = pv
        self.pv_max = pv
        self.attaque = attaque
        self.defense = defense
        self.vitesse = vitesse
        self.energie = 100
        self.capacites = []       # à remplir par les sous-classes
        self.buffs_actifs = {}    # {"nom_buff": tours_restants}

    # ── Méthodes de combat ────────────────────────────────────────────────────

    def est_vivant(self):
        """Retourne True si le robot a encore des PV."""
        return self.pv > 0

    def recevoir_degats(self, degats):
        """Inflige des dégâts au robot (minimum 0 PV)."""
        self.pv = max(0, self.pv - degats)

    def regenerer_energie(self):
        """Régénère 20 points d'énergie par tour (max 100)."""
        self.energie = min(100, self.energie + 20)

    def utiliser_capacite(self, index):
        """
        Utilise la capacité à l'index donné (0 ou 1).
        Retourne un dictionnaire décrivant l'effet appliqué.
        Lève EnergieInsuffisanteException si énergie insuffisante.
        """
        from exceptions import EnergieInsuffisanteException
        capacite = self.capacites[index]
        cout = capacite["cout"]

        if self.energie < cout:
            raise EnergieInsuffisanteException(
                f"{self.nom} n'a pas assez d'énergie ({self.energie}/{cout})"
            )

        self.energie -= cout
        return capacite  # le moteur de combat applique l'effet

    # ── Sérialisation ─────────────────────────────────────────────────────────

    def to_dict(self):
        """Convertit le robot en dictionnaire pour la sauvegarde JSON."""
        return {
            "nom": self.nom,
            "type": self.type,
            "pv": self.pv,
            "pv_max": self.pv_max,
            "attaque": self.attaque,
            "defense": self.defense,
            "vitesse": self.vitesse,
            "energie": self.energie,
        }

    @staticmethod
    def from_dict(data):
        """Recrée un robot depuis un dictionnaire (chargement JSON)."""
        constructeurs = {
            "Assaut": RobotAssaut,
            "Défenseur": RobotDefenseur,
            "Agile": RobotAgile,
            "Équilibré": RobotEquilibre,
        }
        cls = constructeurs.get(data["type"])
        if cls is None:
            raise ValueError(f"Type inconnu lors du chargement : {data['type']}")
        return cls(data["nom"], data["pv_max"], data["attaque"], data["defense"], data["vitesse"])

    def __str__(self):
        return (f"{self.nom} [{self.type}] | "
                f"PV:{self.pv}/{self.pv_max} | "
                f"ATT:{self.attaque} DEF:{self.defense} VIT:{self.vitesse} | "
                f"ÉNERGIE:{self.energie}")


# ─────────────────────────────────────────────────────────────────────────────
# Sous-classes — 4 types de robots
# ─────────────────────────────────────────────────────────────────────────────

class RobotAssaut(Robot):
    """Robot offensif : dégâts maximaux mais fragile."""

    def __init__(self, nom, pv, attaque, defense, vitesse):
        super().__init__(nom, "Assaut", pv, attaque, defense, vitesse)
        self.capacites = [
            {
                "nom": "Tir de barrage",
                "cout": 30,
                "description": "Inflige 1.5× les dégâts d'attaque",
                "effet": "multiplicateur",
                "valeur": 1.5,
                "duree": 0,
            },
            {
                "nom": "Rage de combat",
                "cout": 40,
                "description": "+20 en attaque pendant 2 tours",
                "effet": "buff_attaque",
                "valeur": 20,
                "duree": 2,
            },
        ]


class RobotDefenseur(Robot):
    """Robot tanky : absorbe les dégâts et se régénère."""

    def __init__(self, nom, pv, attaque, defense, vitesse):
        super().__init__(nom, "Défenseur", pv, attaque, defense, vitesse)
        self.capacites = [
            {
                "nom": "Bouclier renforcé",
                "cout": 35,
                "description": "+15 en défense pendant 3 tours",
                "effet": "buff_defense",
                "valeur": 15,
                "duree": 3,
            },
            {
                "nom": "Régénération",
                "cout": 50,
                "description": "Récupère 30 PV",
                "effet": "soin",
                "valeur": 30,
                "duree": 0,
            },
        ]


class RobotAgile(Robot):
    """Robot rapide : attaque en premier et peut esquiver."""

    def __init__(self, nom, pv, attaque, defense, vitesse):
        super().__init__(nom, "Agile", pv, attaque, defense, vitesse)
        self.capacites = [
            {
                "nom": "Attaque rapide",
                "cout": 25,
                "description": "2 attaques normales d'affilée",
                "effet": "double_attaque",
                "valeur": 2,
                "duree": 0,
            },
            {
                "nom": "Esquive",
                "cout": 30,
                "description": "Évite la prochaine attaque (100%)",
                "effet": "esquive",
                "valeur": 1,
                "duree": 1,
            },
        ]


class RobotEquilibre(Robot):
    """Robot polyvalent : aucune faiblesse majeure."""

    def __init__(self, nom, pv, attaque, defense, vitesse):
        super().__init__(nom, "Équilibré", pv, attaque, defense, vitesse)
        self.capacites = [
            {
                "nom": "Frappe puissante",
                "cout": 35,
                "description": "Inflige 1.3× les dégâts d'attaque",
                "effet": "multiplicateur",
                "valeur": 1.3,
                "duree": 0,
            },
            {
                "nom": "Recharge rapide",
                "cout": 20,
                "description": "Récupère 40 énergie immédiatement",
                "effet": "recharge_energie",
                "valeur": 40,
                "duree": 0,
            },
        ]


# ─────────────────────────────────────────────────────────────────────────────
# Fonctions de création
# ─────────────────────────────────────────────────────────────────────────────

# Correspondance type → classe
_CONSTRUCTEURS = {
    "Assaut": RobotAssaut,
    "Défenseur": RobotDefenseur,
    "Agile": RobotAgile,
    "Équilibré": RobotEquilibre,
}

# Stats par défaut suggérées par type (total = 100, toutes contraintes respectées)
_STATS_PAR_TYPE = {
    "Assaut":    {"pv": 52, "attaque": 27, "defense":  9, "vitesse": 12},
    "Défenseur": {"pv": 54, "attaque": 11, "defense": 22, "vitesse": 13},
    "Agile":     {"pv": 52, "attaque": 12, "defense":  7, "vitesse": 29},
    "Équilibré": {"pv": 52, "attaque": 16, "defense": 16, "vitesse": 16},
}


def creer_robot_manuel(nom, type_robot, pv, attaque, defense, vitesse):
    """
    Crée un robot avec des stats manuelles.
    Lève ValueError ou StatsInvalidesException si les données sont invalides.
    """
    if type_robot not in _CONSTRUCTEURS:
        raise ValueError(f"Type invalide : '{type_robot}'")
    cls = _CONSTRUCTEURS[type_robot]
    return cls(nom, pv, attaque, defense, vitesse)


def creer_robot_aleatoire(nom, type_robot):
    """
    Crée un robot avec des stats aléatoires équilibrées (total = 100 garanti).
    Utilise des plages cohérentes par type pour éviter les déséquilibres.
    """
    if type_robot not in _CONSTRUCTEURS:
        raise ValueError(f"Type inconnu : '{type_robot}'")

    # Plages de génération aléatoire par type
    plages = {
        "Assaut":    {"pv": (50, 55), "attaque": (25, 28), "defense": (7,  11)},
        "Défenseur": {"pv": (52, 57), "attaque": (10, 12), "defense": (20, 24)},
        "Agile":     {"pv": (50, 55), "attaque": (10, 14), "defense": (5,   9)},
        "Équilibré": {"pv": (50, 55), "attaque": (12, 18), "defense": (12, 18)},
    }

    p = plages[type_robot]
    pv = random.randint(*p["pv"])
    attaque = random.randint(*p["attaque"])
    defense = random.randint(*p["defense"])
    vitesse = 100 - pv - attaque - defense  # garantit total = 100

    # Correction si vitesse hors limites
    if not (5 <= vitesse <= 40):
        stats = _STATS_PAR_TYPE[type_robot]
        pv, attaque, defense, vitesse = (
            stats["pv"], stats["attaque"], stats["defense"], stats["vitesse"]
        )

    cls = _CONSTRUCTEURS[type_robot]
    return cls(nom, pv, attaque, defense, vitesse)
