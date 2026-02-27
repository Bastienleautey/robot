# =============================================================================
# interface/creation.py — Écran de création d'un robot
# =============================================================================

import pygame
from interface.constantes import (
    LARGEUR, HAUTEUR, NOIR, BLANC, GRIS, ROUGE, VERT, JAUNE, ORANGE,
    GRIS_FONCE, BLEU, COULEUR_TYPE,
    POLICE_GRANDE, POLICE_NORMALE, POLICE_PETITE,
    dessiner_bouton, dessiner_robot, charger_image
)
from robot import Robot, creer_robot_manuel, creer_robot_aleatoire, valider_stats
from exceptions import StatsInvalidesException


TYPES = ["Assaut", "Défenseur", "Agile", "Équilibré"]

# Stats min/max par attribut
LIMITES = {
    "pv":      (50, 150),
    "attaque": (10, 50),
    "defense": (5,  40),
    "vitesse": (5,  40),
}

# Descriptions des capacités par type
CAPACITES_TEXTE = {
    "Assaut":    ["Tir de barrage (30⚡) : 1.5× dégâts", "Rage de combat (40⚡) : +20 ATT 2 tours"],
    "Défenseur": ["Bouclier renforcé (35⚡) : +15 DEF 3 tours", "Régénération (50⚡) : +30 PV"],
    "Agile":     ["Attaque rapide (25⚡) : 2 frappes", "Esquive (30⚡) : évite 1 attaque"],
    "Équilibré": ["Frappe puissante (35⚡) : 1.3× dégâts", "Recharge rapide (20⚡) : +40 énergie"],
}


class EcranCreation:
    """Écran de création d'un robot avec boutons +/- pour les stats."""

    def __init__(self, ecran, robots_existants):
        self.ecran = ecran
        self.robots_existants = robots_existants

        self.fond = charger_image("creer_robots.JPG", (LARGEUR, HAUTEUR))
        self._images_robot = {
            "Assaut":    charger_image("robot1.JPG", (80, 80)),
            "Défenseur": charger_image("robot2.JPG", (80, 80)),
            "Agile":     charger_image("robot3.JPG", (80, 80)),
            "Équilibré": charger_image("robot4.JPG", (80, 80)),
        }

        # État du formulaire
        self.nom = ""
        self.type_index = 0
        self.stats = {"pv": 52, "attaque": 16, "defense": 16, "vitesse": 16}
        self.erreur = ""
        self.saisie_active = True   # le champ texte est actif

    @property
    def type_selectionne(self):
        return TYPES[self.type_index]

    @property
    def total(self):
        return sum(self.stats.values())

    def afficher(self):
        """
        Affiche l'écran de création et retourne :
        - Le robot créé si validation réussie
        - None si l'utilisateur revient au menu
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
                    return None

                result = self._gerer_evenement(event)
                if result == "retour":
                    return None
                if result is not None and isinstance(result, Robot):
                    return result

            horloge.tick(60)

    def _dessiner_ui(self):
        """Dessine tous les éléments de l'interface de création."""
        # Titre
        titre = POLICE_GRANDE.render("⚙️  Créer un Robot", True, JAUNE)
        self.ecran.blit(titre, (LARGEUR // 2 - titre.get_width() // 2, 20))

        # ── Nom ──────────────────────────────────────────────────────────────
        label_nom = POLICE_NORMALE.render("Nom du robot :", True, BLANC)
        self.ecran.blit(label_nom, (60, 80))

        rect_nom = pygame.Rect(60, 110, 300, 40)
        couleur_bord = JAUNE if self.saisie_active else GRIS
        pygame.draw.rect(self.ecran, GRIS_FONCE, rect_nom, border_radius=6)
        pygame.draw.rect(self.ecran, couleur_bord, rect_nom, width=2, border_radius=6)
        texte_nom = POLICE_NORMALE.render(self.nom + ("|" if self.saisie_active else ""), True, BLANC)
        self.ecran.blit(texte_nom, (rect_nom.x + 8, rect_nom.y + 8))

        # ── Type de robot ─────────────────────────────────────────────────────
        label_type = POLICE_NORMALE.render("Type :", True, BLANC)
        self.ecran.blit(label_type, (60, 170))

        dessiner_bouton(self.ecran, "◀", 60, 200, 40, 36)
        couleur_type = COULEUR_TYPE.get(self.type_selectionne, BLANC)
        type_surf = POLICE_NORMALE.render(self.type_selectionne, True, couleur_type)
        self.ecran.blit(type_surf, (115, 207))
        dessiner_bouton(self.ecran, "▶", 250, 200, 40, 36)

        # Image ou forme du robot selon type sélectionné
        img = self._images_robot.get(self.type_selectionne)
        if img:
            self.ecran.blit(img, (310, 195))
        else:
            dessiner_robot(self.ecran, 350, 215, 22, self.type_selectionne)

        # Capacités du type sélectionné
        caps = CAPACITES_TEXTE[self.type_selectionne]
        label_caps = POLICE_PETITE.render("Capacités :", True, GRIS)
        self.ecran.blit(label_caps, (400, 175))
        for i, cap in enumerate(caps):
            surf = POLICE_PETITE.render(f"  • {cap}", True, couleur_type)
            self.ecran.blit(surf, (400, 195 + i * 22))

        # ── Stats avec boutons +/- ────────────────────────────────────────────
        ordre = [("pv", "PV"), ("attaque", "Attaque"), ("defense", "Défense"), ("vitesse", "Vitesse")]
        self._rects_plus  = {}
        self._rects_moins = {}

        for i, (cle, label) in enumerate(ordre):
            y = 260 + i * 60
            min_val, max_val = LIMITES[cle]

            label_surf = POLICE_NORMALE.render(f"{label} ({min_val}-{max_val}) :", True, BLANC)
            self.ecran.blit(label_surf, (60, y))

            # Bouton -
            r_moins = dessiner_bouton(self.ecran, "−", 260, y - 2, 36, 36)
            self._rects_moins[cle] = r_moins

            # Valeur
            val_surf = POLICE_GRANDE.render(str(self.stats[cle]), True, BLANC)
            self.ecran.blit(val_surf, (308, y - 2))

            # Bouton +
            r_plus = dessiner_bouton(self.ecran, "+", 360, y - 2, 36, 36)
            self._rects_plus[cle] = r_plus

        # ── Total ─────────────────────────────────────────────────────────────
        couleur_total = VERT if self.total == 100 else ROUGE
        total_surf = POLICE_GRANDE.render(f"Total : {self.total} / 100", True, couleur_total)
        self.ecran.blit(total_surf, (60, 510))

        indicateur = "✅ Valide" if self.total == 100 else "❌ Doit être exactement 100"
        ind_surf = POLICE_PETITE.render(indicateur, True, couleur_total)
        self.ecran.blit(ind_surf, (60, 545))

        # ── Message d'erreur ──────────────────────────────────────────────────
        if self.erreur:
            err_surf = POLICE_PETITE.render(self.erreur, True, ROUGE)
            self.ecran.blit(err_surf, (60, 570))

        # ── Boutons d'action ──────────────────────────────────────────────────
        self._rect_aleatoire = dessiner_bouton(self.ecran, "🎲 Créer Aléatoire", 60, 615, 200, 50)
        self._rect_creer     = dessiner_bouton(
            self.ecran, "✅ Créer Robot", 280, 615, 200, 50,
            couleur_fond=(20, 80, 20) if self.total == 100 else GRIS_FONCE
        )
        self._rect_retour    = dessiner_bouton(self.ecran, "↩ Retour", 500, 615, 140, 50)

    def _gerer_evenement(self, event):
        """Gère un événement pygame. Retourne l'action ou None."""
        if event.type == pygame.KEYDOWN and self.saisie_active:
            if event.key == pygame.K_BACKSPACE:
                self.nom = self.nom[:-1]
            elif event.key == pygame.K_RETURN:
                self.saisie_active = False
            elif len(self.nom) < 20 and event.unicode.isprintable():
                self.nom += event.unicode
            self.erreur = ""

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            # Clic sur champ nom
            rect_nom = pygame.Rect(60, 110, 300, 40)
            self.saisie_active = rect_nom.collidepoint(pos)

            # Navigation type
            if pygame.Rect(60, 200, 40, 36).collidepoint(pos):
                self.type_index = (self.type_index - 1) % len(TYPES)
            if pygame.Rect(250, 200, 40, 36).collidepoint(pos):
                self.type_index = (self.type_index + 1) % len(TYPES)

            # Boutons +/-
            for cle, rect in self._rects_moins.items():
                if rect.collidepoint(pos):
                    min_val, _ = LIMITES[cle]
                    self.stats[cle] = max(min_val, self.stats[cle] - 1)
            for cle, rect in self._rects_plus.items():
                if rect.collidepoint(pos):
                    _, max_val = LIMITES[cle]
                    self.stats[cle] = min(max_val, self.stats[cle] + 1)

            # Bouton Aléatoire
            if self._rect_aleatoire.collidepoint(pos):
                return self._creer_aleatoire()

            # Bouton Créer
            if self._rect_creer.collidepoint(pos) and self.total == 100:
                return self._valider_et_creer()

            # Bouton Retour
            if self._rect_retour.collidepoint(pos):
                return "retour"

        return None

    def _valider_et_creer(self):
        """Valide le formulaire et crée le robot."""
        nom = self.nom.strip()
        if len(nom) < 3:
            self.erreur = "❌ Le nom doit contenir au moins 3 caractères."
            return None

        noms_existants = [r.nom.lower() for r in self.robots_existants]
        if nom.lower() in noms_existants:
            self.erreur = f"❌ Un robot nommé '{nom}' existe déjà."
            return None

        try:
            robot = creer_robot_manuel(
                nom, self.type_selectionne,
                self.stats["pv"], self.stats["attaque"],
                self.stats["defense"], self.stats["vitesse"]
            )
            return robot
        except (StatsInvalidesException, ValueError) as e:
            self.erreur = str(e)
            return None

    def _creer_aleatoire(self):
        """Génère un robot aléatoire basé sur le type sélectionné."""
        nom = self.nom.strip() or f"Robot-{self.type_selectionne[:3]}"
        noms_existants = [r.nom.lower() for r in self.robots_existants]
        if nom.lower() in noms_existants:
            nom = nom + str(len(self.robots_existants) + 1)

        if len(nom) < 3:
            nom = "Bot"

        try:
            robot = creer_robot_aleatoire(nom, self.type_selectionne)
            # Mettre à jour l'affichage des stats
            self.stats["pv"]      = robot.pv
            self.stats["attaque"] = robot.attaque
            self.stats["defense"] = robot.defense
            self.stats["vitesse"] = robot.vitesse
            self.nom = robot.nom
            return robot
        except ValueError as e:
            self.erreur = str(e)
            return None
