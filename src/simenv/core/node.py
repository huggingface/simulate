import uuid

class Node():
    def __init__(self, name, translation = [0, 0, 0], rotation = [0, 0, 0, 1], scale = [1, 1, 1]):
        self.name = name
        self.uid = uuid.uuid4()
        self.translation = translation
        self.rotation = rotation
        self.scale = scale

    def __str__(self):
        return 'name: {0}, translation: {1}, rotation: {2}, scale: {3}'.format(self.name, self.translation, self.rotation, self.scale)
