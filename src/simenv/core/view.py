import abc


class View(abc.ABC):
    def __init__(self, scene):
        self.nodes = []
        self.scene = scene
        self.scene.link_view(self)

    def add(self, node):
        self.nodes.append(node)

    def remove(self, node):
        self.nodes.remove(node)

    def close(self):
        return
