import simenv as sm

if __name__ == "__main__":
    # creates a basic scene and saves as gltf
    scene = sm.Scene() + [sm.Sphere(position=[1, 0, 0]), sm.Box(name="target", position=[1, 0, 0])]
    target = scene.target
    scene += sm.SimpleRlAgent(reward_target=target)
    scene.save("output/test.gltf")

    scene.close()
