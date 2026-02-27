import pygame
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

pygame.init()
screen = pygame.display.set_mode((900, 700))
pygame.display.set_caption("iRon Legions")

from interface.constantes import charger_image, IMAGE_DIR
print(f"IMAGE_DIR : {IMAGE_DIR}")

from interface.menu import MenuPrincipal
from interface.creation import EcranCreation
from interface.liste import EcranListeRobots
import interface.combat_ui as cui

# Forcer le chargement des images robots
from robot import creer_robot_manuel
r1 = creer_robot_manuel("TitanX", "Assaut", 50, 30, 10, 10)
r2 = creer_robot_manuel("ViperBot", "Agile", 52, 10, 9, 29)

ec = cui.EcranCombat(screen, [r1, r2])
el = EcranListeRobots(screen, [r1, r2])
ec2 = EcranCreation(screen, [])

for k, v in cui.IMAGES_ROBOT.items():
    print(f"  {'✅' if v else '❌'} Image robot {k}")

print(f"  {'✅' if cui.FOND_ARENE else '❌'} Fond arène")
print(f"  {'✅' if cui.FOND_SELECTION else '❌'} Fond sélection")

pygame.quit()
print("\n✅ Interface pygame complète OK")

