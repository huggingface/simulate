import simenv as sm


scene = sm.Scene()

scene += sm.Sphere()
scene += sm.Light()
scene += sm.RL_Agent()
scene += sm.Camera()
scene.show()

scene.close()
