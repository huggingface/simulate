from operator import is_
import unittest
import os
import random

import simenv as sm


def make_scene(build_exe, camera_width, camera_height):
    scene += sm.Box(
        position=[-10, 0, 0],
        bounds=[0, 0.1, 0, 1, -10, 10],
        material=sm.Material.RED,
    )
    scene += sm.Box(position=[10, 0, 0], bounds=[0, 0.1, 0, 1, -10, 10], material=sm.Material.RED
    )
    scene += sm.Box(position=[0, 0, 10], bounds=[-10, 10, 0, 1, 0, 0.1], material=sm.Material.RED
    )
    scene += sm.Box(position=[0, 0, -10],
        bounds=[-10, 10, 0, 1, 0, 0.1],
        material=sm.Material.RED,
    )

    target = sm.Box(
        name="target",
        position=[-4, 0.5, 4],
        material=sm.Material.GREEN,
    )
    scene += target

    # Lets add an actor in the scene, a box mesh with associated actions and a camera as observation device
    actor = sm.EgocentricCameraActor(name="actor", position=[0.0, 0.5, 0.0])
    # Specify the action to control the actor: 3 discrete action to rotate and move forward
    actor.controller = sm.Controller(
        n=7,
        mapping=[
            sm.ActionMapping("add_force", axis=[1, 0, 0], amplitude=10, is_impulse=True),
            sm.ActionMapping("add_torque", axis=[1, 0, 0], amplitude=10, is_impulse=True),
            sm.ActionMapping("add_force_at_position", axis=[1, 0, 0], position=[0, 0, 0], amplitude=10, is_impulse=True),
            sm.ActionMapping("change_position", axis=[2, 0, 0], amplitude=1),
            sm.ActionMapping("change_rotation", axis=[2, 0, 0], amplitude=-90),
            sm.ActionMapping("set_position", position=[1, 0, 1], use_local_coordinates=False),
            sm.ActionMapping("set_rotation", axis=[1, 0, 0], use_local_coordinates=False),
        ],
    )
    scene += actor

    # Add a camera located on the actor
    actor += sm.StateSensor(target_entity=target, reference_entity=actor, properties="position")
    actor += sm.RaycastSensor(n_horizontal_rays=12, n_vertical_rays=4, horizontal_fov=120, vertical_fov=45)
    
    reward = sm.RewardFunction(type="not")  # By default a dense reward equal to the distance between 2 entities
    reward += sm.RewardFunction(entity_a=target, entity_b=actor)
    actor += reward
    return scene

# sm.ActionMapping("add_force", axis=[1, 0, 0], amplitude=10, is_impulse=True),
# sm.ActionMapping("add_torque", axis=[1, 0, 0], amplitude=10, is_impulse=True),
# sm.ActionMapping("add_force_at_position", axis=[1, 0, 0], position=[0, 0, 0], amplitude=10, is_impulse=True),
# sm.ActionMapping("change_position", axis=[2, 0, 0], amplitude=1),
# sm.ActionMapping("change_rotation", axis=[2, 0, 0], amplitude=-90),
# sm.ActionMapping("set_position", position=[1, 0, 1], use_local_coordinates=False),
# sm.ActionMapping("set_rotation", axis=[1, 0, 0], use_local_coordinates=False),

def test_add_force(build_exe):
    camera_width = 40
    camera_height = 40

    scene = sm.Scene(engine="unity", engine_exe=build_exe) + sm.LightSun(name="sun", position=[0, 20, 0], intensity=0.9)

    actor = sm.Box(name="actor", position=[0.0, 0.5, 0.0])
    # Specify the action to control the actor: 3 discrete action to rotate and move forward
    actor.controller = sm.Controller(n=1,
        mapping=sm.ActionMapping("add_force", axis=[1, 0, 0], amplitude=10),
    )
    scene += actor

    event = scene.step()

    for i in range(scene.actor.controller.n):
        event = scene.step(action={"0": 0})
        print(event["nodes"]["actor"]["position"])

    scene.close()


if __name__ == "__main__":
    build_exe = os.environ.get("BUILD_EXE")
    if not build_exe:
        build_exe = None
    test_playground(build_exe)