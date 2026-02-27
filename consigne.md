🦾 Combat de Robots
Contexte
Plongez dans l’arène des étincelles ! Ici, des robots surpuissants s’affrontent dans des duels aussi spectaculaires que stratégiques. Chaque machine est unique, caractéristiques personnalisées, capacités spéciales dévastatrices, et une seule règle : survivre !

Concevez un jeu de combat futuriste, avec une interface graphique immersive pour vivre chaque coup, esquive et explosion tour par tour. Que le meilleur robot l’emporte !

Exigence technique
Un seul langage autorisé : Python (léger, polyvalent, compatible tous OS).

Livrables
Archive ZIP unique : [1PYTH]-Projet-PYTHON-NOM-Prénom.zip
Code source complet, organisé, commenté
README.txt avec instructions de lancement
Documentation complète :
Schéma des modules et classes
Algorithmes en pseudo-code
Formules de calcul
Maquettes de l’interface
Guide de jeu avec captures d’écran
Explication des 4 types de robots
Description du projet, bibliothèques utilisées
Vidéo de démonstration (vous vs robot)
Date limite : 27 février 2026 à 19h00
Retard : -2 points/jour
Remise via lien WIMI (personnel)

Critères d’évaluation
Catégorie	Critères	Points	Détails
Documents	Spécifications techniques	2	Cahier des charges complet, justification des choix algorithmiques et structures de données
Clarté et structure	1	Document bien organisé, lisible, sans ambiguïté
Schémas et diagrammes	1	Présence de schémas (diagrammes de flux, UML simplifié)
Code	Fonctionnalités	6	Implémentation complète des fonctionnalités demandées
Modularité	4	Modules Python, fonctions bien découpées, respect du principe DRY
Gestion des fichiers	2	Sauvegarde/chargement des données
Gestion des erreurs	3	try/except, messages d’erreur clairs, validation des entrées
Qualité du code	3	PEP 8, noms explicites, commentaires pertinents
Recherche & Développement	1	Interface graphique ou fonctionnalité avancée non enseignée
Exécution	Exécution sans erreur	2	Programme robuste, tests de validation
Robustesse	1	Comportement cohérent face aux cas limites
Tests et validation	1	Tests unitaires (pytest)
Malus
Programme qui crash : -5 pts
Code non exécutable : -5 pts
Absence de gestion d’erreurs : -3 pts
Copie détectée : 0/20

Cahier des charges
Module de création de robots
Classe Robot
Attributs obligatoires :

nom : str (3-20 caractères, unique)
type : str (Assaut, Défenseur, Agile, Équilibré)
pv : int (points de vie, 50-150)
pv_max : int (valeur initiale des PV)
attaque : int (puissance d’attaque, 10-50)
defense : int (réduction des dégâts, 5-40)
vitesse : int (ordre d’attaque, 5-40)
energie : int (0-100, commence à 100)
capacites : list (2 capacités spéciales selon le type)
buffs_actifs : dict (effets temporaires en cours)
Contrainte importante : le total de pv + attaque + defense + vitesse doit être exactement égal à 100 points.

Validation des statistiques
Fonction : valider_stats(pv, attaque, defense, vitesse)

Vérifier que pv est entre 50 et 150
Vérifier que attaque est entre 10 et 50
Vérifier que defense est entre 5 et 40
Vérifier que vitesse est entre 5 et 40
Vérifier que pv + attaque + defense + vitesse = 100
Lever StatsInvalidesException si une condition n’est pas respectée


Types de robots et capacités
Chaque type de robot possède 2 capacités spéciales uniques :

1. Type Assaut
Tir de barrage (30 énergie) : inflige 1.5× dégâts d’attaque
Rage de combat (40 énergie) : +20 attaque pendant 2 tours
2. Type Défenseur
Bouclier renforcé (35 énergie) : +15 défense pendant 3 tours
Régénération (50 énergie) : récupère 30 PV
3. Type Agile
Attaque rapide (25 énergie) : 2 attaques normales d’affilée
Esquive (30 énergie) : évite la prochaine attaque (100%)
4. Type Équilibré
Frappe puissante (35 énergie) : inflige 1.3× dégâts d’attaque
Recharge rapide (20 énergie) : récupère 40 énergie immédiatement
Création manuelle et aléatoire
Fonction : creer_robot_manuel(nom, type, pv, attaque, defense, vitesse)

Valider le nom (3-20 caractères, pas de doublons)
Valider le type (dans la liste autorisée)
Appeler valider_stats()
Créer l’objet Robot avec les capacités correspondantes
Fonction : creer_robot_aleatoire(nom, type)

Générer aléatoirement pv, attaque, defense, vitesse
S’assurer que le total = 100
Respecter les limites min/max de chaque stat
Retourner le robot créé

Module de système de combat
Initialisation du combat
Classe : Combat

Attributs :

robot1 : Robot
robot2 : Robot
tour : int (numéro du tour actuel)
journal : list (historique des actions du combat)
mode : str (manuel, auto, rapide)
vainqueur : Robot ou None
Validation :

Vérifier que robot1 et robot2 sont bien des objets Robot
Vérifier que les deux robots sont différents
Lever CombatImpossibleException si problème
Ordre d’attaque
Fonction : determiner_premier_attaquant(robot1, robot2)

Comparer la vitesse des deux robots
Le robot avec la plus grande vitesse attaque en premier
En cas d’égalité, choisir aléatoirement
Retourner le robot qui commence
Calcul des dégâts
Fonction : calculer_degats(attaquant, defenseur, type_attaque)

Formule de base :

degats_base = attaquant.attaque - defenseur.defense
degats_base = max(5, degats_base) (minimum 5 dégâts)
Appliquer variation aléatoire de ±10% : degats = degats_base × random(0.9, 1.1)
10% de chance de coup critique : degats × 1.5
Si capacité utilisée, appliquer le multiplicateur correspondant
Arrondir au nombre entier le plus proche
Actions de combat
Les 4 actions possibles par tour :

Attaque normale
Utilise la formule de dégâts standard
Ne coûte pas d’énergie
Capacité spéciale 1 ou 2
Vérifier que l’énergie est suffisante
Déduire le coût en énergie
Appliquer l’effet de la capacité
Lever EnergieInsuffisanteException si énergie < coût
Défense
Réduit de 50% les dégâts reçus au prochain tour
Ne coûte pas d’énergie
Ajouter un buff temporaire defense_active

Gestion de l’énergie
À chaque tour :

Augmenter l’énergie de +20
Maximum 100 énergie
Condition de victoire
Fonction : verifier_fin_combat()

Vérifier si robot1.pv <= 0 ou robot2.pv <= 0
Le robot avec pv > 0 est déclaré vainqueur
Limite de sécurité : maximum 50 tours (match nul si dépassé)
Module d’intelligence artificielle
Logique de décision de l’IA
Fonction : decider_action_ia(robot, adversaire)

Algorithme de décision simple :

Si energie < 30 : action = défense
Sinon si energie >= 60 et capacité disponible : utiliser capacité aléatoire
Sinon si pv < 30% et possède régénération : utiliser régénération
Sinon : attaque normale
Retourner l’action choisie
Module de sauvegarde et persistance

Sauvegarde des robots
Fonction : sauvegarder_robots(liste_robots, fichier=robots.json)

Convertir chaque robot en dictionnaire
Sauvegarder dans un fichier JSON avec indentation
Gérer les erreurs d’écriture (try/except)
Retourner True si succès, False sinon
Fonction : charger_robots(fichier=robots.json)

Vérifier si le fichier existe
Lire et parser le JSON
Recréer les objets Robot à partir des dictionnaires
Si fichier absent ou corrompu : retourner liste vide
Retourner la liste des robots chargés
Module d’interface graphique
Menu principal
Classe : MenuPrincipal

Éléments requis :

Titre du jeu (police grande taille)
4 boutons : Créer Robot | Mes Robots | Combat | Quitter
Centrer les éléments à l’écran
Chaque bouton redirige vers l’écran correspondant
Création de robot
Classe : EcranCreation

Éléments requis :

Champ texte pour le nom (validation 3-20 caractères)
Menu déroulant pour choisir le type
4 sliders pour PV, Attaque, Défense, Vitesse
Affichage en temps réel du total (doit = 100)
Indicateur visuel : vert si total = 100, rouge sinon
Bouton Créer Aléatoire qui génère des stats valides
Bouton Créer Robot (actif seulement si total = 100)
Affichage des capacités spéciales du type sélectionné
Bouton Retour vers le menu
Liste des robots
Classe : EcranListeRobots

Éléments requis :

Grille de cartes affichant chaque robot
Chaque carte affiche : Nom, Type, PV, Attaque, Défense, Vitesse
Icône représentant le type
Bouton Supprimer sur chaque carte (avec confirmation)
Message si aucun robot créé : Aucun robot disponible
Bouton Retour


Combat
Classe : EcranCombat

Affichage des robots :

Deux zones côte à côte (gauche = robot 1, droite = robot 2)
Icône du robot (changement visuel lors d’attaque)
Nom du robot
Barre de vie : affichage graphique avec animation progressive (ne doit pas diminuer instantanément)
Texte : PV: X/Y
Barre d’énergie : affichage graphique avec animation progressive
Texte : ENERGIE: X/100
Statistiques : ATT: X DEF: Y VIT: Z
Icônes de buffs actifs (si applicable)
Actions :

4 boutons : Attaque | Capacité 1 | Capacité 2 | Défense
Afficher le coût en énergie sur les boutons de capacités
Désactiver les boutons de capacités si énergie insuffisante
En mode auto/rapide : cacher cette zone
Sélection pré-combat :

Écran de sélection avant le combat
2 menus déroulants pour choisir robot 1 et robot 2
Vérifier qu’au moins 2 robots existent
Vérifier que les deux robots sont différents
3 boutons mode : Manuel | Auto | Rapide
Bouton Lancer le combat
Contraintes techniques strictes
Structure du projet
Autres
Gestion des erreurs
Un programme sans crash
Utilisation de pygame
Python 3.12
