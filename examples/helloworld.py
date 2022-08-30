import simenv as sm


if __name__ == "__main__":
    # creates a basic scene and saves as gltf
    scene = sm.Scene() + [sm.Sphere(position=[1, 0, 0]), sm.Box(name="target", position=[1, 0, 0])]
    target = scene.target
    actor = sm.SimpleActor()
    scene += [actor, sm.RewardFunction(entity_a=actor, entity_b=target)]
    scene.save("output/test.gltf")

    scene.close()
