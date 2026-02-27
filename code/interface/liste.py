# =============================================================================
# interface/liste.py — Écran d'affichage de la liste des robots
# =============================================================================

import pygame
from interface.constantes import (
    LARGEUR, HAUTEUR, NOIR, BLANC, GRIS, ROUGE, JAUNE, GRIS_FONCE, BLEU,
    COULEUR_TYPE, POLICE_GRANDE, POLICE_NORMALE, POLICE_PETITE,
    dessiner_bouton, dessiner_robot, charger_image
)

# Images robots chargées une fois
_IMAGES_ROBOT_LISTE = {}


class EcranListeRobots:
    """
    Affiche la liste des robots sous forme de cartes.
    Permet de supprimer un robot (avec confirmation).
    """

    def __init__(self, ecran, robots):
        self.ecran = ecran
        self.robots = robots          # référence à la liste partagée
        self.confirmer_suppression = None  # index du robot à supprimer
        self.fond = charger_image("mes_robtos.JPG", (LARGEUR, HAUTEUR))

        global _IMAGES_ROBOT_LISTE
        if not _IMAGES_ROBOT_LISTE:
            _IMAGES_ROBOT_LISTE = {
                "Assaut":    charger_image("robot1.JPG", (60, 60)),
                "Défenseur": charger_image("robot2.JPG", (60, 60)),
                "Agile":     charger_image("robot3.JPG", (60, 60)),
                "Équilibré": charger_image("robot4.JPG", (60, 60)),
            }

    def afficher(self):
        """
        Affiche la liste et retourne la liste modifiée quand l'utilisateur part.
        """
        horloge = pygame.time.Clock()

        while True:
            if self.fond:
                self.ecran.blit(self.fond, (0, 0))
            else:
                self.ecran.fill(NOIR)
            self._dessiner_ui()
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return self.robots
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    result = self._gerer_clic(event.pos)
                    if result == "retour":
                        return self.robots

            horloge.tick(60)

    def _dessiner_ui(self):
        # Titre
        titre = POLICE_GRANDE.render("🤖  Mes Robots", True, JAUNE)
        self.ecran.blit(titre, (LARGEUR // 2 - titre.get_width() // 2, 20))

        self._rects_supprimer = {}

        if not self.robots:
            msg = POLICE_NORMALE.render("Aucun robot disponible. Créez-en un d'abord !", True, GRIS)
            self.ecran.blit(msg, (LARGEUR // 2 - msg.get_width() // 2, HAUTEUR // 2))
        else:
            # Grille de cartes : 2 colonnes
            for i, robot in enumerate(self.robots):
                col = i % 2
                ligne = i // 2
                x = 50 + col * 420
                y = 80 + ligne * 180

                self._dessiner_carte(robot, i, x, y)

        # Bouton retour
        self._rect_retour = dessiner_bouton(self.ecran, "↩ Retour au Menu",
                                           LARGEUR // 2 - 110, HAUTEUR - 70, 220, 50)

        # Fenêtre de confirmation de suppression
        if self.confirmer_suppression is not None:
            self._dessiner_confirmation()

    def _dessiner_carte(self, robot, index, x, y):
        """Dessine la carte d'un robot."""
        LARGEUR_CARTE = 380
        HAUTEUR_CARTE = 155

        couleur_type = COULEUR_TYPE.get(robot.type, BLANC)

        # Fond de la carte
        rect_carte = pygame.Rect(x, y, LARGEUR_CARTE, HAUTEUR_CARTE)
        pygame.draw.rect(self.ecran, GRIS_FONCE, rect_carte, border_radius=10)
        pygame.draw.rect(self.ecran, couleur_type, rect_carte, width=2, border_radius=10)

        # Image ou forme du robot
        img = _IMAGES_ROBOT_LISTE.get(robot.type)
        if img:
            self.ecran.blit(img, (x + 5, y + (HAUTEUR_CARTE - 60) // 2))
        else:
            dessiner_robot(self.ecran, x + 35, y + 55, 26, robot.type)

        # Nom et type
        nom_surf = POLICE_NORMALE.render(robot.nom, True, BLANC)
        self.ecran.blit(nom_surf, (x + 70, y + 12))
        type_surf = POLICE_PETITE.render(robot.type, True, couleur_type)
        self.ecran.blit(type_surf, (x + 70, y + 40))

        # Stats
        stats_texte = [
            f"PV : {robot.pv_max}",
            f"ATT : {robot.attaque}",
            f"DEF : {robot.defense}",
            f"VIT : {robot.vitesse}",
        ]
        for j, stat in enumerate(stats_texte):
            surf = POLICE_PETITE.render(stat, True, GRIS)
            col_offset = (j % 2) * 120
            row_offset = (j // 2) * 22
            self.ecran.blit(surf, (x + 70 + col_offset, y + 65 + row_offset))

        # Bouton Supprimer
        rect_sup = dessiner_bouton(self.ecran, "🗑 Supprimer",
                                   x + 220, y + HAUTEUR_CARTE - 45, 148, 36,
                                   couleur_fond=(80, 20, 20))
        self._rects_supprimer[index] = rect_sup

    def _dessiner_confirmation(self):
        """Fenêtre modale de confirmation de suppression."""
        overlay = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.ecran.blit(overlay, (0, 0))

        fenetre = pygame.Rect(LARGEUR // 2 - 220, HAUTEUR // 2 - 90, 440, 180)
        pygame.draw.rect(self.ecran, GRIS_FONCE, fenetre, border_radius=12)
        pygame.draw.rect(self.ecran, ROUGE, fenetre, width=2, border_radius=12)

        robot = self.robots[self.confirmer_suppression]
        msg1 = POLICE_NORMALE.render(f"Supprimer « {robot.nom} » ?", True, BLANC)
        msg2 = POLICE_PETITE.render("Cette action est irréversible.", True, GRIS)
        self.ecran.blit(msg1, (LARGEUR // 2 - msg1.get_width() // 2, HAUTEUR // 2 - 65))
        self.ecran.blit(msg2, (LARGEUR // 2 - msg2.get_width() // 2, HAUTEUR // 2 - 30))

        self._rect_confirmer = dessiner_bouton(self.ecran, "✅ Oui, supprimer",
                                               LARGEUR // 2 - 220, HAUTEUR // 2 + 20, 200, 46,
                                               couleur_fond=(100, 20, 20))
        self._rect_annuler   = dessiner_bouton(self.ecran, "❌ Annuler",
                                               LARGEUR // 2 + 20, HAUTEUR // 2 + 20, 200, 46)

    def _gerer_clic(self, pos):
        """Gère les clics souris. Retourne 'retour' ou None."""
        # Si la fenêtre de confirmation est ouverte
        if self.confirmer_suppression is not None:
            if self._rect_confirmer.collidepoint(pos):
                del self.robots[self.confirmer_suppression]
                self.confirmer_suppression = None
            elif self._rect_annuler.collidepoint(pos):
                self.confirmer_suppression = None
            return None

        # Bouton retour
        if self._rect_retour.collidepoint(pos):
            return "retour"

        # Boutons supprimer
        for index, rect in self._rects_supprimer.items():
            if rect.collidepoint(pos):
                self.confirmer_suppression = index
                return None

        return None
