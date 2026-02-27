# =============================================================================
# interface/constantes.py — Couleurs, polices et utilitaires graphiques pygame
# =============================================================================

import os
import pygame

# ── Répertoire des images
IMAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "interfaces_graphiques")


def charger_image(nom, taille=None):
    """
    Charge une image depuis le dossier interfaces_graphiques/.
    Retourne la surface pygame, ou None si le fichier est introuvable.
    """
    chemin = os.path.join(IMAGE_DIR, nom)
    try:
        img = pygame.image.load(chemin)
        if taille:
            img = pygame.transform.scale(img, taille)
        return img
    except Exception as e:
        print(f"⚠️  Image non chargée : {nom} ({e})")
        return None


# ── Dimensions de la fenêtre ──────────────────────────────────────────────────
LARGEUR = 900
HAUTEUR = 700

# ── Palette de couleurs ───────────────────────────────────────────────────────
NOIR        = (10,  10,  20)
BLANC       = (255, 255, 255)
GRIS        = (160, 160, 160)
GRIS_FONCE  = (60,  60,  70)
ROUGE       = (220, 50,  50)
ROUGE_VIVE  = (255, 30,  30)
VERT        = (50,  200, 80)
VERT_FONCE  = (20,  120, 40)
ORANGE      = (255, 160, 30)
BLEU        = (60,  120, 220)
BLEU_FONCE  = (20,  40,  100)
JAUNE       = (255, 220, 0)
VIOLET      = (160, 60,  200)
CYAN        = (30,  200, 220)

# Couleurs par type de robot
COULEUR_TYPE = {
    "Assaut":    ROUGE,
    "Défenseur": BLEU,
    "Agile":     VERT,
    "Équilibré": JAUNE,
}

# ── Polices (initialisées au démarrage pygame) ────────────────────────────────
pygame.font.init()
POLICE_TITRE   = pygame.font.SysFont("Arial", 42, bold=True)
POLICE_GRANDE  = pygame.font.SysFont("Arial", 30, bold=True)
POLICE_NORMALE = pygame.font.SysFont("Arial", 22)
POLICE_PETITE  = pygame.font.SysFont("Arial", 16)


# ── Utilitaires graphiques ────────────────────────────────────────────────────

def dessiner_bouton(surface, texte, x, y, largeur, hauteur,
                    couleur_fond=BLEU_FONCE, couleur_texte=BLANC,
                    couleur_survol=BLEU, rayon=8):
    """
    Dessine un bouton arrondi avec effet de survol.
    Retourne le pygame.Rect du bouton pour la détection de clic.
    """
    rect = pygame.Rect(x, y, largeur, hauteur)
    souris = pygame.mouse.get_pos()
    survol = rect.collidepoint(souris)

    couleur = couleur_survol if survol else couleur_fond
    pygame.draw.rect(surface, couleur, rect, border_radius=rayon)
    pygame.draw.rect(surface, BLANC, rect, width=1, border_radius=rayon)

    label = POLICE_NORMALE.render(texte, True, couleur_texte)
    label_rect = label.get_rect(center=rect.center)
    surface.blit(label, label_rect)

    return rect


def dessiner_barre(surface, x, y, largeur, hauteur, valeur, valeur_max,
                   couleur_fond=GRIS_FONCE, couleur_pleine=VERT):
    """
    Dessine une barre de progression (vie ou énergie) avec fond.
    """
    # Fond
    pygame.draw.rect(surface, couleur_fond, (x, y, largeur, hauteur), border_radius=4)

    # Barre remplie
    if valeur_max > 0:
        ratio = max(0, min(1, valeur / valeur_max))
        largeur_remplie = int(largeur * ratio)
        if largeur_remplie > 0:
            # Couleur dynamique selon le pourcentage
            if ratio > 0.5:
                couleur = couleur_pleine
            elif ratio > 0.25:
                couleur = ORANGE
            else:
                couleur = ROUGE_VIVE
            pygame.draw.rect(surface, couleur,
                             (x, y, largeur_remplie, hauteur), border_radius=4)

    # Bordure
    pygame.draw.rect(surface, BLANC, (x, y, largeur, hauteur), width=1, border_radius=4)


def dessiner_robot(surface, x, y, taille, type_robot, mort=False):
    """
    Dessine la forme géométrique représentant un type de robot.
    Assaut=triangle, Défenseur=carré, Agile=losange, Équilibré=cercle.
    """
    couleur = GRIS if mort else COULEUR_TYPE.get(type_robot, BLANC)

    if type_robot == "Assaut":
        # Triangle pointant vers le haut
        points = [
            (x, y - taille),
            (x - taille, y + taille // 2),
            (x + taille, y + taille // 2),
        ]
        pygame.draw.polygon(surface, couleur, points)
        pygame.draw.polygon(surface, BLANC, points, 2)

    elif type_robot == "Défenseur":
        # Carré centré
        rect = pygame.Rect(x - taille, y - taille, taille * 2, taille * 2)
        pygame.draw.rect(surface, couleur, rect, border_radius=6)
        pygame.draw.rect(surface, BLANC, rect, width=2, border_radius=6)

    elif type_robot == "Agile":
        # Losange
        points = [
            (x, y - taille),
            (x + taille, y),
            (x, y + taille),
            (x - taille, y),
        ]
        pygame.draw.polygon(surface, couleur, points)
        pygame.draw.polygon(surface, BLANC, points, 2)

    else:  # Équilibré
        # Cercle
        pygame.draw.circle(surface, couleur, (x, y), taille)
        pygame.draw.circle(surface, BLANC, (x, y), taille, 2)
