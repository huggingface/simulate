import simenv as sm


scene = sm.Scene()

scene += sm.Sphere()
scene += sm.Light()
scene += sm.RlAgent()
scene += sm.Camera()
scene.show()

scene.close()
