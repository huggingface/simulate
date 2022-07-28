import simenv as sm


scene = sm.Scene(engine="blender")
scene.load("simenv-tests/Chair/glTF-Binary/SheenChair.glb")
scene += sm.Light(name="sun", position=[0, 20, 0], intensity=0.9)
scene += sm.Camera(name="cam1", position=[2, 3, 2], rotation=[-45, 45, 0], width=1024, height=1024)
scene.show()
# scene.render(path="") # <-- uncomment to render the scene to an image in the desired folder
scene.close()
