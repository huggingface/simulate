import os

import pytest

import simulate as sm


# sm.ActionMapping("add_force_at_position", axis=[1, 0, 0], position=[0, 0, 0], amplitude=10, is_impulse=True),
# sm.ActionMapping("change_rotation", axis=[2, 0, 0], amplitude=-90),
# sm.ActionMapping("set_position", position=[1, 0, 1], use_local_coordinates=False),
# sm.ActionMapping("set_rotation", axis=[1, 0, 0], use_local_coordinates=False),


def test_no_action(build_exe, port_number):
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
    # One action to apply force along  the x axis
    actor.actuator = sm.Actuator(
        n=1, mapping=sm.ActionMapping("add_force", axis=[1, 0, 0], amplitude=10, is_impulse=True)
    )
    scene += actor

    # Create the scene
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

    # 10 steps with no action
    for i in range(9):
        scene.step()
    event = scene.step()
    new_position = event["nodes"]["actor"]["position"]
    new_rotation = event["nodes"]["actor"]["rotation"]
    new_velocity = event["nodes"]["actor"]["velocity"]
    new_angular_velocity = event["nodes"]["actor"]["angular_velocity"]

    # We should still be at the same place
    assert new_position == original_position
    assert new_rotation == original_rotation
    assert new_velocity == original_velocity
    assert new_angular_velocity == original_angular_velocity

    scene.close()


def test_add_force(build_exe, port_number):
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

    # One action to apply force along  the x axis without impulse
    actor.actuator = sm.Actuator(
        n=1,
        # Apply a force of 10 N along the x axis during one frame
        mapping=sm.ActionMapping("add_force", axis=[1, 0, 0], amplitude=10, is_impulse=False),
    )
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

    # We are applying a force of 10 N to an object of 1 kg along the x axis during 0.02 second
    # Our new velocity should be V = F/m*t = 10/1*0.02 = 0.2 m/s
    # Our new position should be P = P0 + V*t = 0.0 + 0.2*0.02 = 0.004 m
    assert new_velocity[0] == pytest.approx(0.2, abs=1e-3)
    assert new_position[0] == pytest.approx(original_position[0] + 0.2 * 0.02, abs=1e-3)

    # Apply 9 more time the force of 10 N to an object of 1 kg along the x axis during 0.02 second
    for i in range(8):
        scene.step(action={"actuator": [[[0]]]})
    event = scene.step(action={"actuator": [[[0]]]})
    new_position = event["nodes"]["actor"]["position"]
    new_rotation = event["nodes"]["actor"]["rotation"]
    new_velocity = event["nodes"]["actor"]["velocity"]
    new_angular_velocity = event["nodes"]["actor"]["angular_velocity"]

    assert new_rotation == [0.0, 0.0, 0.0, 1.0]
    assert new_angular_velocity == [0.0, 0.0, 0.0]

    # We have applied a force of 10 N to an object of 1 kg along the x axis during 0.2 second
    # Our new velocity should be V = F/m*t = 10/1*0.2 = 2 m/s
    # Our new position should be P = P0 + 0.5*F/m*t^2 = 0.0 + 0.5*10/1*0.2*0.2 = 0.2 m
    # Or in discretized version: P = P0 + sum(Vi*dt) = 0.0 + sum(0.02*i*0.2 for i in range(11)) = 0.22 m
    assert new_velocity[0] == pytest.approx(2, abs=1e-3)
    assert new_position[0] == pytest.approx(original_position[0] + sum(0.02 * i * 0.2 for i in range(11)), abs=1e-3)

    scene.close()


def test_add_force_time_step(build_exe, port_number):
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

    # One action to apply force along  the x axis without impulse
    actor.actuator = sm.Actuator(
        n=1,
        # Apply a force of 10 N along the x axis during one frame
        mapping=sm.ActionMapping("add_force", axis=[1, 0, 0], amplitude=10, is_impulse=False),
    )
    scene += actor

    # Create the scene with 1 observation step per simulation step with 100 physics steps per second (0.01 second per step)
    scene.config.time_step = 0.01
    scene.config.frame_skip = 1
    scene.show()
    # Apply 20 times a force of 10 N to an object of 1 kg along the x axis during 0.01 second
    for i in range(19):
        scene.step(action={"actuator": [[[0]]]})
    event = scene.step(action={"actuator": [[[0]]]})
    position_1 = event["nodes"]["actor"]["position"]
    velocity_1 = event["nodes"]["actor"]["velocity"]

    # We have applied a force of 10 N to an object of 1 kg along the x axis during 0.2 second
    # Our new velocity should be V = F/m*t = 10/1*0.2 = 2 m/s
    # Our new position should be P = P0 + 0.5*F/m*t^2 = 0.0 + 0.5*10/1*0.2*0.2 = 0.2 m
    # Or in discretized version: P = P0 + sum(Vi*dt) = 0.0 + sum(0.01*i*0.1 for i in range(21)) = 0.21 m
    assert velocity_1[0] == pytest.approx(2, abs=1e-3)
    assert position_1[0] == pytest.approx(0.21, abs=1e-3)

    scene.close()


def test_add_force_frame_skip(build_exe, port_number):
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

    # One action to apply force along  the x axis without impulse
    actor.actuator = sm.Actuator(
        n=1,
        # Apply a force of 10 N along the x axis during one frame
        mapping=sm.ActionMapping("add_force", axis=[1, 0, 0], amplitude=10, is_impulse=False),
    )
    scene += actor

    # Create the scene with 1 observation step per simulation step with 100 physics steps per second (0.01 second per step)
    scene.config.time_step = 0.01
    scene.config.frame_skip = 5
    scene.show()
    # Apply 4 times a force of 10 N to an object of 1 kg along the x axis during 0.01 * 5 second
    for i in range(3):
        scene.step(action={"actuator": [[[0]]]})
    event = scene.step(action={"actuator": [[[0]]]})
    position_1 = event["nodes"]["actor"]["position"]
    velocity_1 = event["nodes"]["actor"]["velocity"]

    # We have applied a force of 10 N to an object of 1 kg along the x axis during 0.2 second
    # Our new velocity should be V = F/m*t = 10/1*0.2 = 2 m/s
    # Our new position should be P = P0 + 0.5*F/m*t^2 = 0.0 + 0.5*10/1*0.2*0.2 = 0.2 m
    # Or in discretized version: P = P0 + sum(Vi*dt) = 0.0 + sum(0.01*i*0.1 for i in range(21)) = 0.21 m
    assert velocity_1[0] == pytest.approx(2, abs=1e-3)
    assert position_1[0] == pytest.approx(0.21, abs=1e-3)

    scene.close()


if __name__ == "__main__":
    build_exe = os.environ.get("BUILD_EXE")
    if not build_exe:
        build_exe = None
    test_add_force_frame_skip(build_exe, port_number=55001)
