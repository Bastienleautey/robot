# =============================================================================
# fichiers.py — Sauvegarde et chargement des robots en JSON
# =============================================================================

import json
import os
from robot import Robot

FICHIER_PAR_DEFAUT = "robots.json"


def sauvegarder_robots(liste_robots, fichier=FICHIER_PAR_DEFAUT):
    """
    Sauvegarde une liste de robots dans un fichier JSON.
    Retourne True si succès, False sinon.
    """
    try:
        donnees = [robot.to_dict() for robot in liste_robots]
        with open(fichier, "w", encoding="utf-8") as f:
            json.dump(donnees, f, indent=4, ensure_ascii=False)
        return True
    except (OSError, IOError) as e:
        print(f"Erreur lors de la sauvegarde : {e}")
        return False


def charger_robots(fichier=FICHIER_PAR_DEFAUT):
    """
    Charge la liste des robots depuis un fichier JSON.
    Retourne une liste de Robot (vide si fichier absent ou corrompu).
    """
    if not os.path.exists(fichier):
        return []

    try:
        with open(fichier, "r", encoding="utf-8") as f:
            donnees = json.load(f)

        robots = []
        for data in donnees:
            try:
                robot = Robot.from_dict(data)
                robots.append(robot)
            except (KeyError, ValueError) as e:
                print(f"Robot ignoré (données invalides) : {e}")

        return robots

    except (json.JSONDecodeError, OSError) as e:
        print(f"Erreur lors du chargement : {e}")
        return []
