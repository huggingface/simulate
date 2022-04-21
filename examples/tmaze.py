import simenv as sm
import simenv.utils.rotation as rotation
import os

scene = sm.Scene(start_frame=0, end_frame=300, frame_rate=60)
view = sm.Unity(scene)

camera = sm.Camera('cam1', translation=[5, 6.5, -3.75], rotation=rotation.quat_from_degrees(45, -45, 0), width=1024, height=1024)
light = sm.DirectionalLight('sun', rotation=rotation.quat_from_degrees(60, -30, 0), intensity=3.5)
agent = sm.Agent('agent', translation=[0, 0, -1.5])
floor = sm.Plane('floor', dynamic=False, scale=[3, 3, 3])
wall1 = sm.Cube('wall1', dynamic=False, translation=[-1, .5, 0], scale=[.1, 1, 5.1])
wall2 = sm.Cube('wall2', dynamic=False, translation=[1, .5, 0], scale=[.1, 1, 5.1])
wall3 = sm.Cube('wall3', dynamic=False, translation=[0, .5, 4.5], scale=[5.9, 1, .1])
wall4 = sm.Cube('wall4', dynamic=False, translation=[-2, .5, 2.5], scale=[1.9, 1, .1])
wall5 = sm.Cube('wall5', dynamic=False, translation=[2, .5, 2.5], scale=[1.9, 1, .1])
wall6 = sm.Cube('wall6', dynamic=False, translation=[-3, .5, 3.5], scale=[.1, 1, 2.1])
wall7 = sm.Cube('wall7', dynamic=False, translation=[3, .5, 3.5], scale=[.1, 1, 2.1])
wall8 = sm.Cube('wall8', dynamic=False, translation=[0, .5, -2.5], scale=[1.9, 1, .1])

scene += camera
scene += light
scene += agent
scene += floor
scene += wall1
scene += wall2
scene += wall3
scene += wall4
scene += wall5
scene += wall6
scene += wall7
scene += wall8

view.run()

render_dir = os.getcwd() + '/output/tmaze/'
if not os.path.exists(render_dir):
    os.makedirs(render_dir)
view.render(render_dir)

view.close()