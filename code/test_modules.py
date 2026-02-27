import sys
sys.path.insert(0, '.')

from exceptions import StatsInvalidesException, CombatImpossibleException, EnergieInsuffisanteException
print("✅ exceptions.py OK")

from robot import Robot, RobotAssaut, RobotDefenseur, RobotAgile, RobotEquilibre, creer_robot_manuel, creer_robot_aleatoire
print("✅ robot.py OK")

from combat import Combat, calculer_degats, determiner_premier_attaquant, decider_action_ia
print("✅ combat.py OK")

from fichiers import sauvegarder_robots, charger_robots
print("✅ fichiers.py OK")

# Test fonctionnel
r1 = creer_robot_manuel("TitanX", "Assaut", 50, 30, 10, 10)
r2 = creer_robot_aleatoire("ViperBot", "Agile")
print(f"\nRobot 1 : {r1}")
print(f"Robot 2 : {r2}")

c = Combat(r1, r2, "auto")
print("\n--- 5 premiers tours ---")
for _ in range(5):
    action, idx = decider_action_ia(c.attaquant_actuel, c.defenseur_actuel)
    res = c.jouer_tour(action, idx)
    print(res["message"])
    if res["fin"]:
        break

# Test sauvegarde
ok = sauvegarder_robots([r1, r2], "test_robots.json")
print(f"\n✅ Sauvegarde JSON : {ok}")
robots_charges = charger_robots("test_robots.json")
print(f"✅ Chargement JSON : {len(robots_charges)} robots chargés")

import os
os.remove("test_robots.json")
print("\n✅ Tous les modules fonctionnent correctement !")
