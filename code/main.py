# =============================================================================
# main.py — Point d'entrée du jeu Combat de Robots
# =============================================================================

import sys
import pygame

from interface.constantes import LARGEUR, HAUTEUR
from interface.menu       import MenuPrincipal
from interface.creation   import EcranCreation
from interface.liste      import EcranListeRobots
from interface.combat_ui  import EcranCombat
from fichiers             import sauvegarder_robots, charger_robots


def main():
    """Lance le jeu et gère la navigation entre les écrans."""
    pygame.init()
    ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
    pygame.display.set_caption("iRon Legions")

    # Chargement des robots sauvegardés
    robots = charger_robots()

    menu        = MenuPrincipal(ecran)

    while True:
        action = menu.afficher()

        if action == "creation":
            creation = EcranCreation(ecran, robots)
            nouveau_robot = creation.afficher()
            if nouveau_robot is not None:
                robots.append(nouveau_robot)
                sauvegarder_robots(robots)

        elif action == "liste":
            liste = EcranListeRobots(ecran, robots)
            robots = liste.afficher()
            sauvegarder_robots(robots)

        elif action == "combat":
            combat_ui = EcranCombat(ecran, robots)
            combat_ui.afficher()

        elif action == "quitter":
            sauvegarder_robots(robots)
            pygame.quit()
            sys.exit()


if __name__ == "__main__":
    main()
