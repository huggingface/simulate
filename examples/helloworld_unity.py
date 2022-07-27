import numpy as np
import PIL
import pyvista as pv

import simenv as sm


scene = sm.Scene(engine="pyvista")
image = PIL.Image.open("elevation.png", mode="r")
scene += sm.Box(material=sm.Material(base_color_texture=image))
scene += sm.Light()
# scene += sm.SimpleRlAgent(camera_width=36, camera_height=36, position=[2,2,2])
# scene += sm.Camera()
scene.show()
input()

scene.close()  # TODO have this in the delete of the Scene class instead of manually
# create a surface to host this texture
# surf = pv.Cylinder()
# tex = pv.numpy_to_texture(np.asarray(image))
# surf.plot(texture=tex)
