import simulate as sm


def create_scene():
    scene = sm.Scene(engine="blender")
    scene += sm.Asset.create_from("simulate-tests/Chair/glTF-Binary/SheenChair.glb", name="chair")
    scene += sm.Light(name="sun", position=[0, 20, 0], intensity=0.9)
    scene += sm.Camera(name="cam1", position=[2, 3, 2], rotation=[-45, 45, 0], width=1024, height=1024)
    scene.show()
    # scene.render(path="") # <-- uncomment to render the scene to an image in the desired folder
    scene.close()


if __name__ == "__main__":
    create_scene()
