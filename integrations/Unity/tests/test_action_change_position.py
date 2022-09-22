import pytest

import simulate as sm


def test_change_position(build_exe, port_number):
    scene = sm.Scene(engine="unity", engine_exe=build_exe, engine_port=port_number) + sm.LightSun(
        name="sun", position=[0, 20, 0], intensity=0.9
    )

    # Add a 1 kg cube as actor
    actor = sm.Box(name="actor", is_actor=True, position=[0.0, 0.5, 0.0])
    # Can only move along the x axis
    actor.physics_component = sm.RigidBodyComponent(
        mass=1,
        constraints=[
            "freeze_rotation_x",
            "freeze_rotation_z",
            "freeze_rotation_y",
            "freeze_position_y",
            "freeze_position_z",
        ],
    )

    # One action to change (teleport) position along the x axis
    actor.actuator = sm.Actuator(n=1, mapping=sm.ActionMapping("change_position", axis=[1, 0, 0], amplitude=1))
    scene += actor

    # Create the scene with 1 observation step per simulation step with 50 physics steps per second (0.02 second per step)
    scene.config.time_step = 0.02
    scene.config.frame_skip = 1
    scene.show()
    event = scene.step()
    original_position = event["nodes"]["actor"]["position"]
    original_rotation = event["nodes"]["actor"]["rotation"]
    original_velocity = event["nodes"]["actor"]["velocity"]
    original_angular_velocity = event["nodes"]["actor"]["angular_velocity"]

    assert original_position == [0.0, 0.5, 0.0]
    assert original_rotation == [0.0, 0.0, 0.0, 1.0]
    assert original_velocity == [0.0, 0.0, 0.0]
    assert original_angular_velocity == [0.0, 0.0, 0.0]

    # Apply one time a force of 10 N to an object of 1 kg along the x axis during 0.02 second
    event = scene.step(action={"actuator": [[[0]]]})
    new_position = event["nodes"]["actor"]["position"]
    new_rotation = event["nodes"]["actor"]["rotation"]
    new_velocity = event["nodes"]["actor"]["velocity"]
    new_angular_velocity = event["nodes"]["actor"]["angular_velocity"]

    assert new_rotation == [0.0, 0.0, 0.0, 1.0]
    assert new_angular_velocity == [0.0, 0.0, 0.0]

    # We are teleporting the object by 1 m along the x axis
    assert new_velocity == [0.0, 0.0, 0.0]
    assert new_position == [1.0, 0.5, 0.0]

    # Apply 9 more time the teleporting
    for i in range(8):
        scene.step(action={"actuator": [[[0]]]})
    event = scene.step(action={"actuator": [[[0]]]})
    new_position = event["nodes"]["actor"]["position"]
    new_rotation = event["nodes"]["actor"]["rotation"]
    new_velocity = event["nodes"]["actor"]["velocity"]
    new_angular_velocity = event["nodes"]["actor"]["angular_velocity"]

    assert new_rotation == [0.0, 0.0, 0.0, 1.0]
    assert new_angular_velocity == [0.0, 0.0, 0.0]

    # We are teleporting the object 10 times by 1 m along the x axis
    assert new_velocity == [0.0, 0.0, 0.0]
    assert new_position == [10.0, 0.5, 0.0]

    scene.close()


def test_change_position_local_coordinates(build_exe, port_number):
    scene = sm.Scene(engine="unity", engine_exe=build_exe, engine_port=port_number) + sm.LightSun(
        name="sun", position=[0, 20, 0], intensity=0.9
    )

    # Add two 1 kg cubes as actor
    actor = sm.Box(name="actor", is_actor=True, position=[0.0, 0.5, 0.0])
    actor2 = sm.Box(name="actor2", is_actor=True, position=[0.0, 0.5, 5.0])
    # Which can only move along the x and z axis
    actor.physics_component = sm.RigidBodyComponent(
        mass=1, constraints=["freeze_rotation_x", "freeze_rotation_z", "freeze_rotation_y", "freeze_position_y"]
    )
    actor2.physics_component = sm.RigidBodyComponent(
        mass=1, constraints=["freeze_rotation_x", "freeze_rotation_z", "freeze_rotation_y", "freeze_position_y"]
    )

    # One action to change (teleport) position along the x axis in world coordinates
    actor.actuator = sm.Actuator(
        n=1, mapping=sm.ActionMapping("change_position", axis=[1, 0, 0], amplitude=1, use_local_coordinates=False)
    )
    # One action to change (teleport) position along the x axis in local coordinates
    actor2.actuator = sm.Actuator(
        n=1, mapping=sm.ActionMapping("change_position", axis=[1, 0, 0], amplitude=1, use_local_coordinates=True)
    )
    scene += [actor, actor2]

    # Let's rotate both objects to have local coordinates different than world coordinates
    scene.actor.rotate_y(90)
    scene.actor2.rotate_y(90)

    # Create the scene with 1 observation step per simulation step with 50 physics steps per second (0.02 second per step)
    scene.config.time_step = 0.02
    scene.config.frame_skip = 1
    scene.show()
    # Apply 10 times the actions
    for i in range(9):
        scene.step(action={"actuator": [[[0]]]})
    event = scene.step(action={"actuator": [[[0]]]})

    position_1 = event["nodes"]["actor"]["position"]
    position_2 = event["nodes"]["actor2"]["position"]
    velocity_1 = event["nodes"]["actor"]["velocity"]
    velocity_2 = event["nodes"]["actor2"]["velocity"]

    # We have teleported the object 10 times by 1 m along the x axis in local and global coordinates
    assert velocity_1 == [0.0, 0.0, 0.0]
    assert velocity_2 == [0.0, 0.0, 0.0]
    assert position_1 == pytest.approx([10.0, 0.5, 0.0], abs=1e-3)
    assert position_2 == pytest.approx([0.0, 0.5, 15.0], abs=1e-3)

    scene.close()


def test_change_position_amplitude(build_exe, port_number):
    scene = sm.Scene(engine="unity", engine_exe=build_exe, engine_port=port_number) + sm.LightSun(
        name="sun", position=[0, 20, 0], intensity=0.9
    )

    # Add two 1 kg cubes as actor
    actor = sm.Box(name="actor", is_actor=True, position=[0.0, 0.5, 0.0])
    actor2 = sm.Box(name="actor2", is_actor=True, position=[0.0, 0.5, 5.0])
    # Which can only move along the x and z axis
    actor.physics_component = sm.RigidBodyComponent(
        mass=1, constraints=["freeze_rotation_x", "freeze_rotation_z", "freeze_rotation_y", "freeze_position_y"]
    )
    actor2.physics_component = sm.RigidBodyComponent(
        mass=1, constraints=["freeze_rotation_x", "freeze_rotation_z", "freeze_rotation_y", "freeze_position_y"]
    )

    # One action to change (teleport) position along the x axis of 10
    actor.actuator = sm.Actuator(n=1, mapping=sm.ActionMapping("change_position", axis=[1, 0, 0], amplitude=10))
    # One action to change (teleport) position along the x axis of 5
    actor2.actuator = sm.Actuator(n=1, mapping=sm.ActionMapping("change_position", axis=[1, 0, 0], amplitude=5))
    scene += [actor, actor2]

    # Create the scene with 1 observation step per simulation step with 50 physics steps per second (0.02 second per step)
    scene.config.time_step = 0.02
    scene.config.frame_skip = 1
    scene.show()
    # Apply 10 times the actions
    for i in range(9):
        scene.step(action={"actuator": [[[0]]]})
    event = scene.step(action={"actuator": [[[0]]]})

    position_1 = event["nodes"]["actor"]["position"]
    position_2 = event["nodes"]["actor2"]["position"]

    # We have teleported the object 10 times by 10 or 5 m along the x axis in local and global coordinates
    assert position_1 == pytest.approx([100.0, 0.5, 0.0], abs=1e-3)
    assert position_2 == pytest.approx([50.0, 0.5, 5.0], abs=1e-3)

    scene.close()


def test_change_position_offset(build_exe, port_number):
    scene = sm.Scene(engine="unity", engine_exe=build_exe, engine_port=port_number) + sm.LightSun(
        name="sun", position=[0, 20, 0], intensity=0.9
    )

    # Add two 1 kg cubes as actor
    actor = sm.Box(name="actor", is_actor=True, position=[0.0, 0.5, 0.0])
    actor2 = sm.Box(name="actor2", is_actor=True, position=[0.0, 0.5, 5.0])
    # Which can only move along the x and z axis
    actor.physics_component = sm.RigidBodyComponent(
        mass=1, constraints=["freeze_rotation_x", "freeze_rotation_z", "freeze_rotation_y", "freeze_position_y"]
    )
    actor2.physics_component = sm.RigidBodyComponent(
        mass=1, constraints=["freeze_rotation_x", "freeze_rotation_z", "freeze_rotation_y", "freeze_position_y"]
    )

    # One action to change (teleport) position along the x axis of 10
    actor.actuator = sm.Actuator(
        n=1, mapping=sm.ActionMapping("change_position", axis=[1, 0, 0], amplitude=10, offset=0.0)
    )
    # One action to change (teleport) position along the x axis of -10
    actor2.actuator = sm.Actuator(
        n=1, mapping=sm.ActionMapping("change_position", axis=[1, 0, 0], amplitude=10, offset=2.0)
    )
    scene += [actor, actor2]

    # Create the scene with 1 observation step per simulation step with 50 physics steps per second (0.02 second per step)
    scene.config.time_step = 0.02
    scene.config.frame_skip = 1
    scene.show()
    # Apply 10 times the actions
    for i in range(9):
        scene.step(action={"actuator": [[[0]]]})
    event = scene.step(action={"actuator": [[[0]]]})

    position_1 = event["nodes"]["actor"]["position"]
    position_2 = event["nodes"]["actor2"]["position"]

    # We have teleported the object 10 times by 10 or 5 m along the x axis in local and global coordinates
    assert position_1 == pytest.approx([100.0, 0.5, 0.0], abs=1e-3)
    assert position_2 == pytest.approx([-100.0, 0.5, 5.0], abs=1e-3)

    scene.close()


if __name__ == "__main__":
    build_exe = None  # os.environ.get("BUILD_EXE")
    if not build_exe:
        build_exe = None
    test_change_position_offset(build_exe)
