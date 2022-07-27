import simenv as sm


scene = sm.Scene(engine="Unity")
scene += sm.Sphere()
scene += sm.Light()
scene += sm.SimpleRlAgent(camera_width=36, camera_height=36, position=[2, 2, 2])
scene += sm.Camera()
scene.show()

scene.close()  # TODO have this in the delete of the Scene class instead of manually
