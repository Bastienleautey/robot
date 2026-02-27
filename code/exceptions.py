# =============================================================================
# exceptions.py — Exceptions personnalisées du jeu Combat de Robots
# =============================================================================


class StatsInvalidesException(Exception):
    """Levée quand les statistiques d'un robot ne respectent pas les règles."""
    pass


class CombatImpossibleException(Exception):
    """Levée quand un combat ne peut pas être lancé (robots invalides, identiques...)."""
    pass


class EnergieInsuffisanteException(Exception):
    """Levée quand un robot n'a pas assez d'énergie pour utiliser une capacité."""
    pass
