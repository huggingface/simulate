import argparse
import random

import matplotlib.pyplot as plt
import numpy as np

import simenv as sm


def make_scene(build_exe, camera_width, camera_height):
    scene = sm.Scene(engine="unity", engine_exe=build_exe)
    scene += sm.LightSun(name="sun", position=[0, 20, 0], intensity=0.9)

    scene += sm.Box(
        name="floor",
        position=[0, 0, 0],
        bounds=[-50, 50, 0, 0.1, -50, 50],
        material=sm.Material.BLUE,
        with_collider=True,
    )
    scene += sm.Box(
        name="wall1",
        position=[-10, 0, 0],
        bounds=[0, 0.1, 0, 1, -10, 10],
        material=sm.Material.RED,
        with_collider=True,
    )
    scene += sm.Box(
        name="wall2", position=[10, 0, 0], bounds=[0, 0.1, 0, 1, -10, 10], material=sm.Material.RED, with_collider=True
    )
    scene += sm.Box(
        name="wall3", position=[0, 0, 10], bounds=[-10, 10, 0, 1, 0, 0.1], material=sm.Material.RED, with_collider=True
    )
    scene += sm.Box(
        name="wall4",
        position=[0, 0, -10],
        bounds=[-10, 10, 0, 1, 0, 0.1],
        material=sm.Material.RED,
        with_collider=True,
    )

    material = sm.Material(base_color=[random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)])
    for i in range(1):
        scene += sm.Box(
            name=f"cube{i}",
            position=[random.uniform(-9, 9), 0.5, random.uniform(-9, 9)],
            material=material,
            with_collider=True,
        )

    # Lets add an actor in the scene, a capsule mesh with associated actions and a camera as observation device
    actor = sm.EgocentricCameraActor(name="actor", position=[0.0, 0.5, 0.0])  # Has a collider
    # Specify the action to control the actor: 3 discrete action to rotate and move forward
    actor.controller = sm.Controller(
        n=3,
        mapping=[
            sm.ActionMapping("change_relative_rotation", axis=[0, 1, 0], amplitude=-90),
            sm.ActionMapping("change_relative_rotation", axis=[0, 1, 0], amplitude=90),
            sm.ActionMapping("change_relative_position", axis=[1, 0, 0], amplitude=2.0),
        ],
    )
    scene += actor

    # Add a camera located on the actor
    actor_camera = sm.Camera(name="camera", width=camera_width, height=camera_height, position=[0, 0.75, 0])
    actor += actor_camera
    actor += sm.StateSensor(target_entity=actor, reference_entity=actor_camera, properties="position")
    actor += sm.RaycastSensor(n_horizontal_rays=12, n_vertical_rays=4, horizontal_fov=120, vertical_fov=45)
    # # Let's add a target and a reward function
    material = sm.Material(base_color=[random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)])
    target = sm.Box(
        name="cube",
        position=[random.uniform(-9, 9), 0.5, random.uniform(-9, 9)],
        material=material,
        with_collider=True,
    )
    scene += target

    reward = sm.RewardFunction(type="not")  # By default a dense reward equal to the distance between 2 entities
    reward += sm.RewardFunction(entity_a=target, entity_b=actor)
    actor += reward
    return scene


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--build_exe", default=None, type=str, required=False, help="Pre-built unity app for simenv")
    args = parser.parse_args()

    camera_width = 40
    camera_height = 40
    scene = make_scene(args.build_exe, camera_width, camera_height)
    print(scene)
    scene.save("test.gltf")

    env = sm.RLEnv(scene)

    plt.ion()
    fig1, ax1 = plt.subplots()
    dummy_obs = np.zeros(shape=(camera_height, camera_width, 3), dtype=np.uint8)
    axim1 = ax1.imshow(dummy_obs, vmin=0, vmax=255)

    for i in range(100):
        obs, reward, done, info = env.step()
        obs = obs["CameraSensor"].transpose(1, 2, 0)
        axim1.set_data(obs)
        fig1.canvas.flush_events()

        plt.pause(0.1)

    scene.close()
