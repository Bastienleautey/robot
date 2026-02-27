# =============================================================================
# combat.py — Moteur de combat, IA, gestion des tours et des buffs
# =============================================================================

import random
from exceptions import CombatImpossibleException, EnergieInsuffisanteException
from robot import Robot


# ─────────────────────────────────────────────────────────────────────────────
# Fonctions utilitaires
# ─────────────────────────────────────────────────────────────────────────────

def determiner_premier_attaquant(robot1, robot2):
    """
    Retourne le robot qui attaque en premier (le plus rapide).
    En cas d'égalité, choix aléatoire.
    """
    if robot1.vitesse > robot2.vitesse:
        return robot1
    elif robot2.vitesse > robot1.vitesse:
        return robot2
    else:
        return random.choice([robot1, robot2])


def calculer_degats(attaquant, defenseur, multiplicateur=1.0):
    """
    Calcule les dégâts infligés par l'attaquant au défenseur.

    Formule :
      degats_base = max(5, attaque - defense)
      variation   = ±10%
      critique    = 10% de chance × 1.5
    """
    # Attaque réelle (avec buffs actifs)
    attaque_reelle = attaquant.attaque + attaquant.buffs_actifs.get("buff_attaque", 0)
    defense_reelle = defenseur.defense + defenseur.buffs_actifs.get("buff_defense", 0)

    degats_base = max(5, attaque_reelle - defense_reelle)

    # Variation aléatoire ±10%
    degats = degats_base * random.uniform(0.9, 1.1)

    # Multiplicateur de capacité (Tir de barrage, Frappe puissante…)
    degats *= multiplicateur

    # Coup critique (10% de chance)
    critique = False
    if random.random() < 0.10:
        degats *= 1.5
        critique = True

    return round(degats), critique


# ─────────────────────────────────────────────────────────────────────────────
# Gestion des buffs
# ─────────────────────────────────────────────────────────────────────────────

def appliquer_buffs(robot):
    """
    Décrémente les buffs actifs à la fin du tour.
    Supprime les buffs expirés (durée = 0).
    """
    for buff in list(robot.buffs_actifs.keys()):
        if buff in ("buff_attaque", "buff_defense", "esquive", "defense_active"):
            robot.buffs_actifs[buff] -= 1
            if robot.buffs_actifs[buff] <= 0:
                del robot.buffs_actifs[buff]


# ─────────────────────────────────────────────────────────────────────────────
# Intelligence artificielle
# ─────────────────────────────────────────────────────────────────────────────

def decider_action_ia(robot, adversaire):
    """
    Algorithme de décision de l'IA.
    Retourne un tuple : ("action", index_capacite_ou_None)

    Règles de priorité :
      1. Énergie < 30          → défense
      2. PV faible + régén dispo → capacité de soin (index 1 pour Défenseur)
      3. Énergie >= 60          → capacité aléatoire
      4. Sinon                  → attaque normale
    """
    # Règle 1 : énergie critique → se défendre
    if robot.energie < 30:
        return ("defense", None)

    # Règle 2 : PV critiques + soin disponible (Défenseur, capacité 1 = Régénération)
    pv_critique = robot.pv < robot.pv_max * 0.30
    if pv_critique and robot.type == "Défenseur" and robot.energie >= robot.capacites[1]["cout"]:
        return ("capacite", 1)

    # Règle 3 : assez d'énergie → capacité aléatoire disponible
    if robot.energie >= 60:
        capacites_dispo = [
            i for i, c in enumerate(robot.capacites)
            if robot.energie >= c["cout"]
        ]
        if capacites_dispo:
            return ("capacite", random.choice(capacites_dispo))

    # Règle 4 : attaque normale
    return ("attaque", None)


# ─────────────────────────────────────────────────────────────────────────────
# Classe Combat
# ─────────────────────────────────────────────────────────────────────────────

class Combat:
    """
    Gère un combat complet entre deux robots.
    Modes : 'manuel', 'auto', 'rapide'
    """

    TOUR_MAX = 50

    def __init__(self, robot1, robot2, mode="manuel"):
        # Validation
        if not isinstance(robot1, Robot) or not isinstance(robot2, Robot):
            raise CombatImpossibleException("Les deux combattants doivent être des objets Robot.")
        if robot1 is robot2 or robot1.nom == robot2.nom:
            raise CombatImpossibleException("Les deux robots doivent être différents.")
        if mode not in ("manuel", "auto", "rapide"):
            raise CombatImpossibleException(f"Mode invalide : '{mode}'")

        self.robot1 = robot1
        self.robot2 = robot2
        self.tour = 0
        self.journal = []          # historique textuel des actions
        self.mode = mode
        self.vainqueur = None

        # Déterminer l'ordre d'attaque
        self.attaquant_actuel = determiner_premier_attaquant(robot1, robot2)
        self.defenseur_actuel = robot2 if self.attaquant_actuel is robot1 else robot1

        self._log(f"⚡ {self.attaquant_actuel.nom} attaque en premier !")

    # ── Journalisation ────────────────────────────────────────────────────────

    def _log(self, message):
        """Ajoute un message au journal du combat."""
        self.journal.append(message)

    # ── Tour de combat ────────────────────────────────────────────────────────

    def jouer_tour(self, action, index_capacite=None):
        """
        Exécute un tour de combat complet.

        action : "attaque" | "capacite" | "defense"
        index_capacite : 0 ou 1 (uniquement si action == "capacite")

        Retourne un dict résumant ce qui s'est passé.
        """
        if self.vainqueur is not None:
            return {"fin": True, "vainqueur": self.vainqueur}

        self.tour += 1
        attaquant = self.attaquant_actuel
        defenseur = self.defenseur_actuel
        resultat = {
            "tour": self.tour,
            "attaquant": attaquant.nom,
            "defenseur": defenseur.nom,
            "degats": 0,
            "critique": False,
            "action": action,
            "message": "",
            "fin": False,
            "vainqueur": None,
        }

        # ── Régénération d'énergie ────────────────────────────────────────────
        attaquant.regenerer_energie()

        # ── Résolution de l'action ────────────────────────────────────────────
        try:
            if action == "attaque":
                degats, crit = calculer_degats(attaquant, defenseur)
                # L'esquive annule l'attaque
                if "esquive" in defenseur.buffs_actifs:
                    msg = f"💨 {defenseur.nom} esquive l'attaque de {attaquant.nom} !"
                    del defenseur.buffs_actifs["esquive"]
                else:
                    # Demi-dégâts si défense active
                    if "defense_active" in defenseur.buffs_actifs:
                        degats = max(1, degats // 2)
                    defenseur.recevoir_degats(degats)
                    critique_txt = " 💥 CRITIQUE !" if crit else ""
                    msg = f"⚔️  {attaquant.nom} attaque {defenseur.nom} pour {degats} dégâts.{critique_txt}"
                resultat["degats"] = degats
                resultat["critique"] = crit

            elif action == "capacite":
                capacite = attaquant.utiliser_capacite(index_capacite)
                effet = capacite["effet"]

                if effet == "multiplicateur":
                    degats, crit = calculer_degats(attaquant, defenseur, capacite["valeur"])
                    if "esquive" in defenseur.buffs_actifs:
                        msg = f"💨 {defenseur.nom} esquive {capacite['nom']} !"
                        del defenseur.buffs_actifs["esquive"]
                    else:
                        defenseur.recevoir_degats(degats)
                        msg = f"🔥 {attaquant.nom} utilise {capacite['nom']} → {degats} dégâts !"
                    resultat["degats"] = degats

                elif effet == "buff_attaque":
                    attaquant.buffs_actifs["buff_attaque"] = capacite["duree"]
                    msg = f"💪 {attaquant.nom} active {capacite['nom']} (+{capacite['valeur']} ATT pendant {capacite['duree']} tours)"

                elif effet == "buff_defense":
                    attaquant.buffs_actifs["buff_defense"] = capacite["duree"]
                    msg = f"🛡️  {attaquant.nom} active {capacite['nom']} (+{capacite['valeur']} DEF pendant {capacite['duree']} tours)"

                elif effet == "soin":
                    soin = min(capacite["valeur"], attaquant.pv_max - attaquant.pv)
                    attaquant.pv += soin
                    msg = f"💚 {attaquant.nom} utilise {capacite['nom']} et récupère {soin} PV !"

                elif effet == "double_attaque":
                    d1, c1 = calculer_degats(attaquant, defenseur)
                    d2, c2 = calculer_degats(attaquant, defenseur)
                    total = d1 + d2
                    defenseur.recevoir_degats(total)
                    msg = f"⚡ {attaquant.nom} frappe deux fois : {d1} + {d2} = {total} dégâts !"
                    resultat["degats"] = total

                elif effet == "esquive":
                    attaquant.buffs_actifs["esquive"] = 1
                    msg = f"💨 {attaquant.nom} se prépare à esquiver la prochaine attaque !"

                elif effet == "recharge_energie":
                    gain = min(capacite["valeur"], 100 - attaquant.energie)
                    attaquant.energie += gain
                    msg = f"⚡ {attaquant.nom} recharge son énergie (+{gain} → {attaquant.energie}/100)"

                else:
                    msg = f"❓ {attaquant.nom} utilise {capacite['nom']} (effet inconnu)"

            elif action == "defense":
                attaquant.buffs_actifs["defense_active"] = 1
                msg = f"🛡️  {attaquant.nom} se met en position défensive (dégâts réduits de 50% ce tour)"

            else:
                msg = f"❓ Action inconnue : {action}"

        except EnergieInsuffisanteException as e:
            msg = f"⚠️  {str(e)} — attaque normale à la place"
            degats, crit = calculer_degats(attaquant, defenseur)
            defenseur.recevoir_degats(degats)
            resultat["degats"] = degats

        # ── Décrémenter les buffs ─────────────────────────────────────────────
        appliquer_buffs(attaquant)

        self._log(msg)
        resultat["message"] = msg

        # ── Vérifier fin de combat ────────────────────────────────────────────
        fin = self.verifier_fin_combat()
        if fin:
            resultat["fin"] = True
            resultat["vainqueur"] = self.vainqueur
        else:
            # Inverser les rôles pour le prochain tour
            self.attaquant_actuel, self.defenseur_actuel = (
                self.defenseur_actuel, self.attaquant_actuel
            )

        return resultat

    # ── Vérification de fin ───────────────────────────────────────────────────

    def verifier_fin_combat(self):
        """
        Vérifie si le combat est terminé.
        Retourne True si un vainqueur est déterminé ou si le tour max est atteint.
        """
        if not self.robot1.est_vivant():
            self.vainqueur = self.robot2
            self._log(f"🏆 {self.robot2.nom} remporte le combat !")
            return True
        if not self.robot2.est_vivant():
            self.vainqueur = self.robot1
            self._log(f"🏆 {self.robot1.nom} remporte le combat !")
            return True
        if self.tour >= self.TOUR_MAX:
            self._log("⏱️  Match nul ! Limite de tours atteinte.")
            return True
        return False
