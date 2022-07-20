import simenv as sm


class Goal:
    def __init__(self):
        pass


class Floor:
    def __init__(self):
        pass


class Lava:
    def __init__(self):
        pass


class Wall:
    def __init__(self):
        pass


class Door:
    def __init__(self):
        pass


class Key:
    def __init__(self):
        pass


class Box:
    def __init__(self):
        pass


class MiniGridEnv:

    def __init__(self, scene: sm.Scene, width, height):
        self.scene = scene
        self.width = width
        self.height = height
        self.tile_size = 32

        scene += sm.Camera(camera_type="orthographic", width=800, height=800)
        scene += sm.Light()

        for i in range(width):
            for k in range(height):
                self.scene += sm.Box(name=f"floor{i * height + k}", position=[i, k, 0], material=sm.Material.BLACK)

