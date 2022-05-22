"""
Python file to call map, game and agents generation.
"""

from world import generate_map
from game import generate_game


def generate_env(seed):
    """
    Generate the environment.
    """

    # TODO: choose width and height randomly from a set of predefined values
    width = 9
    height = 9

    # Generate the map
    generate_map(seed=seed, width=width, height=height)

    # Generate the game
    generate_game()

    # TODO: generation of agents


if __name__ == '__main__':
    generate_env(seed=0)