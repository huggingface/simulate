import itertools

from .asset import Asset


class Agent(Asset):
    dimensionality = 3
    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(self, name, translation=[0, 0, 0], rotation=[0, 0, 0, 1], scale=[1, 1, 1]):
        super().__init__(name, translation, rotation, scale)
