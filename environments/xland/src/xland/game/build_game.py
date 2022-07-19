"""
Predicate selection for the game.
"""

from .predicates import away, collect, near


def generate_game():
    """
    Generate the game.
    """

    predicates = [near, away, collect]

    print("No game generation implemented yet. Skipping...")
