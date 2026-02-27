# =============================================================================
# interface/menu.py — Menu principal du jeu
# =============================================================================

import pygame
from interface.constantes import (
    LARGEUR, HAUTEUR, NOIR, BLANC, GRIS, BLEU_FONCE, JAUNE,
    POLICE_TITRE, POLICE_NORMALE, dessiner_bouton, charger_image
)


class MenuPrincipal:
    """Écran du menu principal avec 4 boutons de navigation."""

    def __init__(self, ecran):
        self.ecran = ecran
        self.fond = charger_image("menue.png", (LARGEUR, HAUTEUR))
        self.boutons = [
            {"texte": "⚙️  Créer un Robot",  "action": "creation"},
            {"texte": "🤖  Mes Robots",       "action": "liste"},
            {"texte": "⚔️  Combat",            "action": "combat"},
            {"texte": "❌  Quitter",           "action": "quitter"},
        ]

    def afficher(self):
        """
        Affiche le menu principal et retourne l'action choisie.
        Retourne : "creation" | "liste" | "combat" | "quitter"
        """
        horloge = pygame.time.Clock()

        while True:
            # Fond
            if self.fond:
                self.ecran.blit(self.fond, (0, 0))
            else:
                self.ecran.fill(NOIR)

            # ── Titre ──────────────────────────────────────────────────────────
            titre = POLICE_TITRE.render("iRon Legions", True, JAUNE)
            rect_titre = titre.get_rect(center=(LARGEUR // 2, 120))
            self.ecran.blit(titre, rect_titre)

            sous_titre = POLICE_NORMALE.render("Que le meilleur robot l'emporte !", True, BLANC)
            rect_sous = sous_titre.get_rect(center=(LARGEUR // 2, 180))
            self.ecran.blit(sous_titre, rect_sous)

            # ── Boutons ────────────────────────────────────────────────────────
            rects_boutons = []
            for i, bouton in enumerate(self.boutons):
                y = 260 + i * 90
                rect = dessiner_bouton(
                    self.ecran, bouton["texte"],
                    LARGEUR // 2 - 160, y, 320, 60
                )
                rects_boutons.append((rect, bouton["action"]))

            pygame.display.flip()

            # ── Événements ────────────────────────────────────────────────────
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quitter"
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for rect, action in rects_boutons:
                        if rect.collidepoint(event.pos):
                            return action

            horloge.tick(60)
