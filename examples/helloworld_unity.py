import simenv as sm


scene = sm.Scene(engine='Unity')

sphere = sm.Sphere('sphere')
light = sm.DirectionalLight('light')
camera = sm.Camera('cam')

scene += sphere
scene += light
scene += camera

scene.render()

scene.engine.close()  # TODO have this in the delete of the Scene class instead of manually
