import simenv as sm
scene = sm.Scene() # engine='Unity')

scene += sm.Sphere()
scene += sm.Light()
scene += sm.RL_Agent()
scene += sm.Camera()
scene.show()

scene.close()  # TODO have this in the delete of the Scene class instead of manually
