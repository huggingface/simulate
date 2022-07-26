import numpy as np

import simenv as sm
import simenv.assets.utils as utils


scene = sm.Scene(engine="Unity")

# Create mesh

x = np.arange(-5, 5, 0.25)
z = np.arange(-5, 5, 0.25)
x, z = np.meshgrid(x, z)
r = np.sqrt(x**2 + z**2)
y = np.sin(r)

scene += sm.StructuredGrid(x, y, z)
scene += sm.LightSun()
scene += sm.Camera(position=[0, 5, -15], rotation=[0, 1, 0, 0])
scene.show()

scene.close()
