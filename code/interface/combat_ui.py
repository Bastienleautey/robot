# =============================================================================
# interface/combat_ui.py — Écran de sélection et de combat
# =============================================================================

import pygame
import time
from interface.constantes import (
    LARGEUR, HAUTEUR, NOIR, BLANC, GRIS, ROUGE, VERT, JAUNE, ORANGE,
    BLEU, GRIS_FONCE, CYAN, COULEUR_TYPE,
    POLICE_GRANDE, POLICE_NORMALE, POLICE_PETITE,
    dessiner_bouton, dessiner_barre, dessiner_robot, charger_image
)
from combat import Combat, decider_action_ia

# Images de robots par type
IMAGES_ROBOT = {}  # rempli à l'initialisation du premier EcranCombat

# Fond d'arène
FOND_ARENE = None
FOND_SELECTION = None


# Délais en secondes pour les modes auto/rapide
DELAI_AUTO   = 1.0
DELAI_RAPIDE = 0.3


class EcranCombat:
    """
    Gère l'écran de sélection pré-combat et l'écran de combat pygame.
    """

    def __init__(self, ecran, robots):
        self.ecran = ecran
        self.robots = robots

        # Chargement des images (une seule fois)
        global IMAGES_ROBOT, FOND_ARENE, FOND_SELECTION

        if not IMAGES_ROBOT:
            IMAGES_ROBOT = {
                "Assaut":    charger_image("robot1.JPG", (160, 160)),
                "Défenseur": charger_image("robot2.JPG", (160, 160)),
                "Agile":     charger_image("robot3.JPG", (160, 160)),
                "Équilibré": charger_image("robot4.JPG", (160, 160)),
            }
        if FOND_ARENE is None:
            FOND_ARENE    = charger_image("arene.JPG",        (LARGEUR, HAUTEUR))
        if FOND_SELECTION is None:
            FOND_SELECTION = charger_image("menue.png", (LARGEUR, HAUTEUR))

        # Sélection pré-combat
        self.index_r1 = 0
        self.index_r2 = 1 if len(robots) > 1 else 0
        self.mode = "manuel"
        self.erreur = ""

    def afficher(self):
        """
        Affiche d'abord l'écran de sélection, puis le combat si lancé.
        Retourne None dans tous les cas (retour au menu).
        """
        if len(self.robots) < 2:
            self._afficher_message_erreur("⚠️  Il faut au moins 2 robots pour combattre !")
            return None

        resultat = self._ecran_selection()
        if resultat == "retour":
            return None

        # Lancer le combat
        return self._lancer_combat(resultat["robot1"], resultat["robot2"], resultat["mode"])

    # ─────────────────────────────────────────────────────────────────────────
    # Écran de sélection pré-combat
    # ─────────────────────────────────────────────────────────────────────────

    def _ecran_selection(self):
        horloge = pygame.time.Clock()

        while True:
            if FOND_SELECTION:
                self.ecran.blit(FOND_SELECTION, (0, 0))
            else:
                self.ecran.fill(NOIR)
            self._dessiner_selection()
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "retour"
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    result = self._gerer_clic_selection(event.pos)
                    if result == "retour":
                        return "retour"
                    if isinstance(result, dict):
                        return result

            horloge.tick(60)

    def _dessiner_selection(self):
        titre = POLICE_GRANDE.render("⚔️  Sélection du Combat", True, JAUNE)
        self.ecran.blit(titre, (LARGEUR // 2 - titre.get_width() // 2, 20))

        # Robot 1 (gauche)
        self._dessiner_panneau_selection(60, 80, self.index_r1, "Joueur / Robot 1", "_r1")
        # Robot 2 (droite)
        self._dessiner_panneau_selection(470, 80, self.index_r2, "Adversaire / Robot 2", "_r2")

        # VS
        vs = POLICE_GRANDE.render("VS", True, ROUGE)
        self.ecran.blit(vs, (LARGEUR // 2 - vs.get_width() // 2, 200))

        # Mode de combat
        label_mode = POLICE_NORMALE.render("Mode :", True, BLANC)
        self.ecran.blit(label_mode, (LARGEUR // 2 - 140, 370))
        modes = [("Manuel", "manuel"), ("Auto", "auto"), ("Rapide", "rapide")]
        self._rects_modes = {}
        for i, (libelle, val) in enumerate(modes):
            couleur = VERT if self.mode == val else GRIS_FONCE
            r = dessiner_bouton(self.ecran, libelle,
                                LARGEUR // 2 - 140 + i * 105, 400, 95, 40,
                                couleur_fond=couleur)
            self._rects_modes[val] = r

        # Erreur
        if self.erreur:
            err_surf = POLICE_PETITE.render(self.erreur, True, ROUGE)
            self.ecran.blit(err_surf, (LARGEUR // 2 - err_surf.get_width() // 2, 460))

        # Boutons
        self._rect_lancer = dessiner_bouton(self.ecran, "⚔️  Lancer le Combat",
                                            LARGEUR // 2 - 140, 490, 280, 55,
                                            couleur_fond=(20, 80, 20))
        self._rect_retour = dessiner_bouton(self.ecran, "↩ Retour",
                                            LARGEUR // 2 - 60, 560, 120, 45)

    def _dessiner_panneau_selection(self, x, y, index, titre_str, suffixe):
        """Dessine un panneau de sélection de robot (gauche ou droite)."""
        LARGEUR_PANNEAU = 340

        label = POLICE_NORMALE.render(titre_str, True, BLANC)
        self.ecran.blit(label, (x, y))

        robot = self.robots[index]
        couleur = COULEUR_TYPE.get(robot.type, BLANC)

        # Flèches
        r_gauche = dessiner_bouton(self.ecran, "◀", x, y + 30, 36, 36)
        r_droite  = dessiner_bouton(self.ecran, "▶", x + LARGEUR_PANNEAU - 36, y + 30, 36, 36)

        # Nom et type
        nom_surf  = POLICE_NORMALE.render(robot.nom, True, BLANC)
        type_surf = POLICE_PETITE.render(robot.type, True, couleur)
        self.ecran.blit(nom_surf,  (x + 50, y + 36))
        self.ecran.blit(type_surf, (x + 50, y + 62))

        # Image ou forme du robot
        img = IMAGES_ROBOT.get(robot.type)
        if img:
            img_petit = pygame.transform.scale(img, (100, 100))
            self.ecran.blit(img_petit, (x + LARGEUR_PANNEAU // 2 - 50, y + 90))
        else:
            dessiner_robot(self.ecran, x + LARGEUR_PANNEAU // 2, y + 150, 36, robot.type)

        # Stats
        stats_lines = [
            f"PV : {robot.pv_max}    ATT : {robot.attaque}",
            f"DEF : {robot.defense}   VIT : {robot.vitesse}",
        ]
        for i, ligne in enumerate(stats_lines):
            surf = POLICE_PETITE.render(ligne, True, GRIS)
            self.ecran.blit(surf, (x + 20, y + 210 + i * 22))

        # Stocker les rects pour la gestion des clics
        setattr(self, f"_rect_gauche{suffixe}", r_gauche)
        setattr(self, f"_rect_droite{suffixe}", r_droite)

    def _gerer_clic_selection(self, pos):
        """Gère les clics sur l'écran de sélection."""
        # Navigation Robot 1
        if self._rect_gauche_r1.collidepoint(pos):
            self.index_r1 = (self.index_r1 - 1) % len(self.robots)
        if self._rect_droite_r1.collidepoint(pos):
            self.index_r1 = (self.index_r1 + 1) % len(self.robots)

        # Navigation Robot 2
        if self._rect_gauche_r2.collidepoint(pos):
            self.index_r2 = (self.index_r2 - 1) % len(self.robots)
        if self._rect_droite_r2.collidepoint(pos):
            self.index_r2 = (self.index_r2 + 1) % len(self.robots)

        # Modes
        for val, rect in self._rects_modes.items():
            if rect.collidepoint(pos):
                self.mode = val

        # Retour
        if self._rect_retour.collidepoint(pos):
            return "retour"

        # Lancer
        if self._rect_lancer.collidepoint(pos):
            if self.index_r1 == self.index_r2:
                self.erreur = "❌ Sélectionne deux robots différents !"
                return None
            return {
                "robot1": self.robots[self.index_r1],
                "robot2": self.robots[self.index_r2],
                "mode":   self.mode,
            }

        return None

    # ─────────────────────────────────────────────────────────────────────────
    # Écran de combat
    # ─────────────────────────────────────────────────────────────────────────

    def _lancer_combat(self, robot1, robot2, mode):
        """Démarre et affiche le combat tour par tour."""
        # Remettre les PV et l'énergie à leur maximum avant le combat
        robot1.pv = robot1.pv_max
        robot1.energie = 100
        robot1.buffs_actifs = {}
        robot2.pv = robot2.pv_max
        robot2.energie = 100
        robot2.buffs_actifs = {}

        combat = Combat(robot1, robot2, mode)

        # PV animés (affichage progressif)
        pv_affiche = {robot1: float(robot1.pv), robot2: float(robot2.pv)}
        energie_affiche = {robot1: float(robot1.energie), robot2: float(robot2.energie)}

        journal_visible = combat.journal[:]   # journal affiché à l'écran
        fin = False

        horloge = pygame.time.Clock()
        dernier_tour_auto = time.time()

        while True:
            dt = horloge.tick(60) / 1000.0    # secondes depuis le dernier frame

            # Animations : rapprocher les valeurs affichées des valeurs réelles
            for r in [robot1, robot2]:
                pv_affiche[r]      += (r.pv      - pv_affiche[r])      * min(1, dt * 6)
                energie_affiche[r] += (r.energie - energie_affiche[r]) * min(1, dt * 6)

            if FOND_ARENE:
                self.ecran.blit(FOND_ARENE, (0, 0))
            else:
                self.ecran.fill(NOIR)
            self._dessiner_combat(combat, robot1, robot2, pv_affiche, energie_affiche,
                                  journal_visible, fin, mode)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not fin:
                    if mode == "manuel":
                        action = self._detecter_action(event.pos, combat)
                        if action:
                            resultat = combat.jouer_tour(*action)
                            journal_visible = combat.journal[-8:]
                            if resultat["fin"]:
                                fin = True
                    elif self._rect_retour_combat and self._rect_retour_combat.collidepoint(event.pos):
                        return None

                if event.type == pygame.MOUSEBUTTONDOWN and fin:
                    return None

            # Mode auto/rapide : jouer automatiquement
            if not fin and mode in ("auto", "rapide"):
                delai = DELAI_AUTO if mode == "auto" else DELAI_RAPIDE
                if time.time() - dernier_tour_auto >= delai:
                    attaquant = combat.attaquant_actuel
                    adversaire = combat.defenseur_actuel
                    action, idx = decider_action_ia(attaquant, adversaire)
                    resultat = combat.jouer_tour(action, idx)
                    journal_visible = combat.journal[-8:]
                    dernier_tour_auto = time.time()
                    if resultat["fin"]:
                        fin = True

    def _dessiner_combat(self, combat, robot1, robot2, pv_affiche, energie_affiche,
                         journal, fin, mode):
        """Dessine tous les éléments de l'écran de combat."""
        # ── Panneau robot 1 (gauche) ──────────────────────────────────────────
        self._dessiner_panneau_robot(robot1, pv_affiche[robot1], energie_affiche[robot1],
                                     50, 30, combat.attaquant_actuel is robot1)

        # ── Panneau robot 2 (droite) ──────────────────────────────────────────
        self._dessiner_panneau_robot(robot2, pv_affiche[robot2], energie_affiche[robot2],
                                     510, 30, combat.attaquant_actuel is robot2)

        # ── Journal de combat ─────────────────────────────────────────────────
        pygame.draw.rect(self.ecran, GRIS_FONCE, (50, 380, 800, 220), border_radius=8)
        pygame.draw.rect(self.ecran, GRIS, (50, 380, 800, 220), width=1, border_radius=8)

        label_j = POLICE_PETITE.render("Journal de combat", True, GRIS)
        self.ecran.blit(label_j, (60, 385))

        for i, ligne in enumerate(journal[-7:]):
            surf = POLICE_PETITE.render(ligne, True, BLANC)
            self.ecran.blit(surf, (60, 405 + i * 26))

        # ── Boutons d'action (mode manuel) ────────────────────────────────────
        self._rect_retour_combat = None
        if mode == "manuel" and not fin:
            self._dessiner_boutons_action(combat)
        elif fin:
            vainqueur = combat.vainqueur
            if vainqueur:
                msg = POLICE_GRANDE.render(f"🏆 {vainqueur.nom} a gagné !", True, JAUNE)
            else:
                msg = POLICE_GRANDE.render("⏱️  Match nul !", True, ORANGE)
            self.ecran.blit(msg, (LARGEUR // 2 - msg.get_width() // 2, 615))
            sous = POLICE_PETITE.render("Clique n'importe où pour continuer", True, GRIS)
            self.ecran.blit(sous, (LARGEUR // 2 - sous.get_width() // 2, 658))

    def _dessiner_panneau_robot(self, robot, pv_aff, en_aff, x, y, est_actif):
        """Dessine le panneau d'un robot (nom, forme, barres, stats, buffs)."""
        LARGEUR_PANNEAU = 330
        couleur = COULEUR_TYPE.get(robot.type, BLANC)
        bordure = JAUNE if est_actif else GRIS_FONCE

        pygame.draw.rect(self.ecran, GRIS_FONCE, (x, y, LARGEUR_PANNEAU, 340), border_radius=10)
        pygame.draw.rect(self.ecran, bordure, (x, y, LARGEUR_PANNEAU, 340), width=2, border_radius=10)

        # Nom + type
        nom_surf  = POLICE_NORMALE.render(robot.nom, True, BLANC)
        type_surf = POLICE_PETITE.render(robot.type, True, couleur)
        self.ecran.blit(nom_surf,  (x + 10, y + 8))
        self.ecran.blit(type_surf, (x + 10, y + 34))

        # Indicateur tour actif
        if est_actif:
            ind = POLICE_PETITE.render("▶ Tour actif", True, JAUNE)
            self.ecran.blit(ind, (x + LARGEUR_PANNEAU - ind.get_width() - 8, y + 8))

        # Forme du robot ou image
        mort = not robot.est_vivant()
        img = IMAGES_ROBOT.get(robot.type)
        if img:
            img_rect = img.get_rect(center=(x + LARGEUR_PANNEAU // 2, y + 120))
            # Assombrir si mort
            if mort:
                img_grise = img.copy()
                img_grise.fill((80, 80, 80), special_flags=pygame.BLEND_MULT)
                self.ecran.blit(img_grise, img_rect)
            else:
                self.ecran.blit(img, img_rect)
        else:
            dessiner_robot(self.ecran, x + LARGEUR_PANNEAU // 2, y + 120, 44, robot.type, mort)

        # Barre de vie
        label_pv = POLICE_PETITE.render(f"PV : {robot.pv}/{robot.pv_max}", True, BLANC)
        self.ecran.blit(label_pv, (x + 10, y + 200))
        dessiner_barre(self.ecran, x + 10, y + 222, LARGEUR_PANNEAU - 20, 16,
                       pv_aff, robot.pv_max)

        # Barre d'énergie
        label_en = POLICE_PETITE.render(f"ÉNERGIE : {robot.energie}/100", True, CYAN)
        self.ecran.blit(label_en, (x + 10, y + 244))
        dessiner_barre(self.ecran, x + 10, y + 265, LARGEUR_PANNEAU - 20, 12,
                       en_aff, 100, couleur_pleine=CYAN)

        # Stats
        stats_str = f"ATT:{robot.attaque}  DEF:{robot.defense}  VIT:{robot.vitesse}"
        stats_surf = POLICE_PETITE.render(stats_str, True, GRIS)
        self.ecran.blit(stats_surf, (x + 10, y + 285))

        # Buffs actifs
        if robot.buffs_actifs:
            buffs_str = "Buffs: " + ", ".join(
                f"{k}({v})" for k, v in robot.buffs_actifs.items()
            )
            buff_surf = POLICE_PETITE.render(buffs_str, True, ORANGE)
            self.ecran.blit(buff_surf, (x + 10, y + 308))

    def _dessiner_boutons_action(self, combat):
        """Dessine les 4 boutons d'action en mode manuel."""
        attaquant = combat.attaquant_actuel
        caps = attaquant.capacites

        actions = [
            ("⚔️  Attaque",    None,  True),
            (f"⚡ {caps[0]['nom']} ({caps[0]['cout']}⚡)", 0,
             attaquant.energie >= caps[0]["cout"]),
            (f"⚡ {caps[1]['nom']} ({caps[1]['cout']}⚡)", 1,
             attaquant.energie >= caps[1]["cout"]),
            ("🛡️  Défense",    None,  True),
        ]

        self._rects_actions = []
        for i, (texte, idx, dispo) in enumerate(actions):
            couleur = GRIS_FONCE if not dispo else (20, 60, 20) if i == 0 else \
                      (60, 20, 80) if i in (1, 2) else (20, 20, 80)
            r = dessiner_bouton(self.ecran, texte,
                                50 + i * 205, 615, 195, 50,
                                couleur_fond=couleur)
            self._rects_actions.append((r, i, idx, dispo))

    def _detecter_action(self, pos, combat):
        """Retourne (action, index_capacite) selon le bouton cliqué."""
        if not hasattr(self, "_rects_actions"):
            return None
        for rect, i, idx_cap, dispo in self._rects_actions:
            if rect.collidepoint(pos) and dispo:
                if i == 0:
                    return ("attaque", None)
                elif i in (1, 2):
                    return ("capacite", idx_cap)
                elif i == 3:
                    return ("defense", None)
        return None

    @staticmethod
    def _afficher_message_erreur(ecran, message):
        pass

    def _afficher_message_erreur(self, message):
        """Affiche un message d'erreur simple et attend un clic."""
        horloge = pygame.time.Clock()
        while True:
            self.ecran.fill(NOIR)
            surf = POLICE_NORMALE.render(message, True, ROUGE)
            self.ecran.blit(surf, (LARGEUR // 2 - surf.get_width() // 2, HAUTEUR // 2))
            sous = POLICE_PETITE.render("Clique pour revenir au menu", True, GRIS)
            self.ecran.blit(sous, (LARGEUR // 2 - sous.get_width() // 2, HAUTEUR // 2 + 50))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type in (pygame.QUIT, pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                    return
            horloge.tick(60)
