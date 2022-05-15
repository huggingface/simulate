import simenv as sm


scene = sm.Scene(engine='Unity')

sphere = sm.Sphere('sphere')
light = sm.DirectionalLight('light')
<<<<<<< HEAD
agent = sm.RL_Agent('agent')
=======
>>>>>>> 0ae54ab (adding modding)
camera = sm.Camera('cam')

scene += sphere
scene += light
scene += camera

scene.build()

scene.close()  # TODO have this in the delete of the Scene class instead of manually
