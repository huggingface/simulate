import simenv as sm

scene = sm.Scene()

sphere = sm.Sphere('sphere')
light = sm.DirectionalLight('light')
agent = sm.Agent('agent')
camera = sm.Camera('cam')

scene += sphere
scene += light
scene += agent
scene += camera

scene.initialize_unity_backend()
