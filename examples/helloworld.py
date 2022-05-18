import simenv as sm
import simenv.assets.utils as utils
import os

scene = sm.Scene()
view = sm.Unity(scene)

camera = sm.Camera('cam1')
light = sm.Light('sun', rotation=utils.quat_from_degrees(60, -30, 0))
floor = sm.Plane('ground')
obj1 = sm.Sphere('obj1', position=[0, 5, 0])
obj2 = sm.Cube('obj2', position=[2, 5, 0], scaling=[2, 2, 2])

scene += camera
scene += light
scene += floor
scene += obj1
scene += obj2

view.run()

render_dir = os.getcwd() + '/output/helloworld/'
if not os.path.exists(render_dir):
    os.makedirs(render_dir)
view.render(render_dir)

view.close()