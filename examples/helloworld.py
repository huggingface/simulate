import simenv as sm


scene = sm.Scene() + [sm.Sphere(position=[1, 0, 0]), sm.Box(name="target", position=[1, 0, 0])]
target = scene.target
scene += sm.SimpleRlAgent(reward_target=target)
scene.save("test.gltf")

scene.close()
