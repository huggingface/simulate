from matplotlib import scale
import simenv as sm
import numpy as np
from simenv.assets.object import ProcGenPrimsMaze3D
from simenv.assets.procgen.prims import generate_prims_maze

scene = sm.Scene(engine="Unity")
scene += sm.Light(name="sun", position=[0, 20, 0], intensity=0.9)

blue_material = sm.Material(base_color=(0, 0, 0.8))
scene += sm.Box(name="floor", position=[0, 0, 0], bounds=[-50, 50, 0, 0.1, -50, 50], material=blue_material)
scene += ProcGenPrimsMaze3D(10, 16)

scene.show()

input("Press enter to continue")