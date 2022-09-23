import os

import pytest

import simulate as sm


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


def test_add_force_is_impulse(build_exe, port_number):
    scene = sm.Scene(engine="unity", engine_exe=build_exe, engine_port=port_number) + sm.LightSun(
        name="sun", position=[0, 20, 0], intensity=0.9
    )

    # Add two 1 kg cubes as actor
    actor = sm.Box(name="actor", is_actor=True, position=[0.0, 0.5, 0.0])
    actor2 = sm.Box(name="actor2", is_actor=True, position=[0.0, 0.5, 5.0])
    # Which can only move along the x axis
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
    actor2.physics_component = sm.RigidBodyComponent(
        mass=1,
        constraints=[
            "freeze_rotation_x",
            "freeze_rotation_z",
            "freeze_rotation_y",
            "freeze_position_y",
            "freeze_position_z",
        ],
    )

    # The first one has an action which apply a force of 10 N along the x axis during one frame (without impulse mode)
    actor.actuator = sm.Actuator(
        n=1, mapping=sm.ActionMapping("add_force", axis=[1, 0, 0], amplitude=10, is_impulse=False)
    )
    # The first one has an action which apply a force of 10 N second along the x axis during one frame (with impulse mode)
    actor2.actuator = sm.Actuator(
        n=1, mapping=sm.ActionMapping("add_force", axis=[1, 0, 0], amplitude=10, is_impulse=True)
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
    velocity_1 = event["nodes"]["actor"]["velocity"]
    position_2 = event["nodes"]["actor2"]["position"]
    velocity_2 = event["nodes"]["actor2"]["velocity"]

    # Actor1: We have applied a force of 10 N to an object of 1 kg along the x axis during 0.2 second
    # Our new velocity should be V = F/m*t = 10/1*0.2 = 2 m/s
    # Our new position should be P = P0 + 0.5*F/m*t^2 = 0.0 + 0.5*10/1*0.2*0.2 = 0.2 m
    # Or in discretized version: P = P0 + sum(Vi*dt) = 0.0 + sum(0.02*i*0.2 for i in range(11)) = 0.22 m
    assert velocity_1[0] == pytest.approx(2, abs=1e-3)
    assert position_1[0] == pytest.approx(0.22, abs=1e-3)

    # Actor2: We have applied a force F*t of 10 N second to an object of 1 kg along the x axis for 10 times
    # Our new velocity should be V = sum(F*t/m, steps) = 10* 10 = 100 m/s
    # Our new position should be in discretized version: P = P0 + sum(Vi*dt) = 0.0 + sum(10*i*0.02 for i in range(11)) = 11 m
    assert velocity_2[0] == pytest.approx(100, abs=1e-3)
    assert position_2[0] == pytest.approx(11, abs=1e-3)

    scene.close()


def test_add_force_local_coordinates(build_exe, port_number):
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

    # The first one has an action which apply a force of 10 N along the x axis in world coordinates
    actor.actuator = sm.Actuator(
        n=1, mapping=sm.ActionMapping("add_force", axis=[1, 0, 0], amplitude=10, use_local_coordinates=False)
    )
    # The first one has an action which apply a force of 10 N along the x axis in local coordinates
    actor2.actuator = sm.Actuator(
        n=1, mapping=sm.ActionMapping("add_force", axis=[1, 0, 0], amplitude=10, use_local_coordinates=True)
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
    velocity_1 = event["nodes"]["actor"]["velocity"]
    position_2 = event["nodes"]["actor2"]["position"]
    velocity_2 = event["nodes"]["actor2"]["velocity"]

    # Actor1: We have applied a force of 10 N to an object of 1 kg along the x axis during 0.2 second
    # Our new velocity should be V = F/m*t = 10/1*0.2 = 2 m/s
    # Our new position should be P = P0 + 0.5*F/m*t^2 = 0.0 + 0.5*10/1*0.2*0.2 = 0.2 m
    # Or in discretized version: P = P0 + sum(Vi*dt) = 0.0 + sum(0.02*i*0.2 for i in range(11)) = 0.22 m
    assert velocity_1[0] == pytest.approx(2, abs=1e-3)
    assert position_1[0] == pytest.approx(0.22, abs=1e-3)

    # Actor2: We have applied a force of 10 N to an object of 1 kg along the rotated x axis so the z axis during 0.2 second
    # Our new velocity should be V = F/m*t = 10/1*0.2 = 2 m/s
    # Our new position should be P = P0 + 0.5*F/m*t^2 = 0.0 + 0.5*10/1*0.2*0.2 = 0.2 m
    # Or in discretized version: P = P0 + sum(Vi*dt) = 0.0 + sum(0.02*i*0.2 for i in range(11)) = 5 (original location along z) + 0.22 m = 5.22
    assert velocity_2[2] == pytest.approx(2, abs=1e-3)
    assert position_2[2] == pytest.approx(5.22, abs=1e-3)

    scene.close()


def test_add_force_amplitude(build_exe, port_number):
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

    # The first one has an action which apply a force of 10 N along the x axis
    actor.actuator = sm.Actuator(n=1, mapping=sm.ActionMapping("add_force", axis=[1, 0, 0], amplitude=10))
    # The first one has an action which apply a force of 5 N along the x axis
    actor2.actuator = sm.Actuator(n=1, mapping=sm.ActionMapping("add_force", axis=[1, 0, 0], amplitude=5))
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
    velocity_1 = event["nodes"]["actor"]["velocity"]
    position_2 = event["nodes"]["actor2"]["position"]
    velocity_2 = event["nodes"]["actor2"]["velocity"]

    # Actor1: We have applied a force of 10 N to an object of 1 kg along the x axis during 0.2 second
    # Our new velocity should be V = F/m*t = 10/1*0.2 = 2 m/s
    # Our new position should be P = P0 + 0.5*F/m*t^2 = 0.0 + 0.5*10/1*0.2*0.2 = 0.2 m
    # Or in discretized version: P = P0 + sum(Vi*dt) = 0.0 + sum(0.02*i*0.2 for i in range(11)) = 0.22 m
    assert velocity_1[0] == pytest.approx(2, abs=1e-3)
    assert position_1[0] == pytest.approx(0.22, abs=1e-3)

    # Actor2: We have applied a force of 5 N to an object of 1 kg along the x axis during 0.2 second
    # Our new velocity should be V = F/m*t = 5/1*0.2 = 1 m/s
    # Our new position should be P = P0 + 0.5*F/m*t^2 = 0.0 + 0.5*5/1*0.2*0.2 = 0.2 m
    # Or in discretized version: P = P0 + sum(Vi*dt) = 0.0 + sum(0.02*i*0.1 for i in range(11)) = 0.11 m
    assert velocity_2[0] == pytest.approx(1, abs=1e-3)
    assert position_2[0] == pytest.approx(0.11, abs=1e-3)

    scene.close()


def test_add_force_offset(build_exe, port_number):
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

    # The first one has an action which apply a force of 10 N along the x axis
    actor.actuator = sm.Actuator(n=1, mapping=sm.ActionMapping("add_force", axis=[1, 0, 0], amplitude=10, offset=0.0))
    # The first one has an action which apply a force of 5 N along the x axis
    actor2.actuator = sm.Actuator(n=1, mapping=sm.ActionMapping("add_force", axis=[1, 0, 0], amplitude=10, offset=2.0))
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
    velocity_1 = event["nodes"]["actor"]["velocity"]
    position_2 = event["nodes"]["actor2"]["position"]
    velocity_2 = event["nodes"]["actor2"]["velocity"]

    # Actor1: We have applied a force of 10 N to an object of 1 kg along the x axis during 0.2 second
    # Our new velocity should be V = F/m*t = 10/1*0.2 = 2 m/s
    # Our new position should be P = P0 + 0.5*F/m*t^2 = 0.0 + 0.5*10/1*0.2*0.2 = 0.2 m
    # Or in discretized version: P = P0 + sum(Vi*dt) = 0.0 + sum(0.02*i*0.2 for i in range(11)) = 0.22 m
    assert velocity_1[0] == pytest.approx(2, abs=1e-3)
    assert position_1[0] == pytest.approx(0.22, abs=1e-3)

    # Actor2: We have applied a force of -10 N to an object of 1 kg along the x axis during 0.2 second
    # Our new velocity should be V = F/m*t = -5/1*0.2 = -2 m/s
    # Our new position should be P = P0 - 0.5*F/m*t^2 = 0.0 - 0.5*5/1*0.2*0.2 = 0.2 m
    # Or in discretized version: P = P0 + sum(Vi*dt) = 0.0 - sum(0.02*i*0.1 for i in range(11)) = -0.22 m
    assert velocity_2[0] == pytest.approx(-2, abs=1e-3)
    assert position_2[0] == pytest.approx(-0.22, abs=1e-3)

    scene.close()


def test_add_force_max_velocity(build_exe, port_number):
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

    # The first one has an action which apply a force of 10 N along the x axis
    actor.actuator = sm.Actuator(
        n=1, mapping=sm.ActionMapping("add_force", axis=[1, 0, 0], amplitude=10, max_velocity_threshold=None)
    )
    # The first one has an action which apply a force of 10 N along the x axis with max velocity of 1.
    actor2.actuator = sm.Actuator(
        n=1, mapping=sm.ActionMapping("add_force", axis=[1, 0, 0], amplitude=10, max_velocity_threshold=1.0)
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
    velocity_1 = event["nodes"]["actor"]["velocity"]
    position_2 = event["nodes"]["actor2"]["position"]
    velocity_2 = event["nodes"]["actor2"]["velocity"]

    # Actor1: We have applied a force of 10 N to an object of 1 kg along the x axis during 0.2 second
    # Our new velocity should be V = F/m*t = 10/1*0.2 = 2 m/s
    # Our new position should be P = P0 + 0.5*F/m*t^2 = 0.0 + 0.5*10/1*0.2*0.2 = 0.2 m
    # Or in discretized version: P = P0 + sum(Vi*dt) = 0.0 + sum(0.02*i*0.2 for i in range(11)) = 0.22 m
    assert velocity_1[0] == pytest.approx(2, abs=1e-3)
    assert position_1[0] == pytest.approx(0.22, abs=1e-3)

    # Actor2: We have applied a force of -10 N to an object of 1 kg along the x axis during 0.2 second
    # The action is only applied if the veolcity is under the maxVelocityThreshold
    assert velocity_2[0] == pytest.approx(1.2, abs=1e-3)
    assert position_2[0] == pytest.approx(0.18, abs=1e-3)

    scene.close()


if __name__ == "__main__":
    build_exe = os.environ.get("BUILD_EXE")
    if not build_exe:
        build_exe = None
    test_add_force_amplitude(build_exe, port_number=None)
