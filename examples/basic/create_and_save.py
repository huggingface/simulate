import simulate as sm


if __name__ == "__main__":
    # creates a basic scene and saves as gltf
    scene = sm.Scene(engine="Unity")

    # add objects to scene
    scene += [sm.Sphere(position=[1, 0, 0], with_collider=True), sm.Box(name="target", position=[0, 2.5, 0])]

    # create an actor with reward function
    target = scene.target
    actor = sm.EgocentricCameraActor(position=[0, 0, 3])
    scene += [actor, sm.RewardFunction(entity_a=actor, entity_b=target)]

    print(scene)

    # save the scene
    scene.save("output/test.gltf")

    scene.show()

    input("Press enter to end this example.")
    scene.close()
