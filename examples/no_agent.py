import time

import matplotlib.pyplot as plt
import numpy as np

import simenv as sm
import simenv.assets.utils as utils

scene = sm.Scene(engine="Unity")

scene += sm.LightSun(name="sun", position=[0, 20, 0], intensity=0.9)
scene += sm.Box(name="floor", position=[0, -0.05, 0], scaling=[100, 0.1, 100])
scene += sm.Box(name="wall1", position=[-1, 0.5, 0], scaling=[0.1, 1, 5.1])
scene += sm.Box(name="wall2", position=[1, 0.5, 0], scaling=[0.1, 1, 5.1])
scene += sm.Box(name="wall3", position=[0, 0.5, 4.5], scaling=[5.9, 1, 0.1])
scene += sm.Box(name="wall4", position=[-2, 0.5, 2.5], scaling=[1.9, 1, 0.1])
scene += sm.Box(name="wall5", position=[2, 0.5, 2.5], scaling=[1.9, 1, 0.1])
scene += sm.Box(name="wall6", position=[-3, 0.5, 3.5], scaling=[0.1, 1, 2.1])
scene += sm.Box(name="wall7", position=[3, 0.5, 3.5], scaling=[0.1, 1, 2.1])
scene += sm.Box(name="wall8", position=[0, 0.5, -2.5], scaling=[1.9, 1, 0.1])

scene.show()

input("Press Enter to continue")

scene.close()
