import pytest

import simulate as sm


def test_add_torque(build_exe, port_number):
    scene = sm.Scene(engine="unity", engine_exe=build_exe, engine_port=port_number) + sm.LightSun(
        name="sun", position=[0, 20, 0], intensity=0.9
    )

    # Add a 1 kg sphere as actor
    actor = sm.Cylinder(
        name="actor", is_actor=True, position=[0.0, 0.5, 0.0]
    )  # Using a cylinder to compute more easily our equations
    # Can only rotate along the y axis
    actor.physics_component = sm.RigidBodyComponent(
        mass=1,
        constraints=[
            "freeze_rotation_x",
            "freeze_rotation_z",
            "freeze_position_x",
            "freeze_position_y",
            "freeze_position_z",
        ],
    )

    # One action to apply torque along the y axis without impulse
    actor.actuator = sm.Actuator(
        n=1,
        # Apply a torque of 1 N.m along the y axis during one frame
        mapping=sm.ActionMapping("add_torque", axis=[0, 1, 0], amplitude=1, is_impulse=False),
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

    # Apply one time a torque of 1 N.m to an object of 1 kg along the y axis during 0.02 second
    event = scene.step(action={"actuator": [[[0]]]})
    new_position = event["nodes"]["actor"]["position"]
    new_rotation = event["nodes"]["actor"]["rotation"]
    new_velocity = event["nodes"]["actor"]["velocity"]
    new_angular_velocity = event["nodes"]["actor"]["angular_velocity"]

    assert new_velocity == [0.0, 0.0, 0.0]
    assert new_position == [0.0, 0.5, 0.0]

    # We are applying a torque of 1 N.m to an object of 1 kg along the y axis during 0.02 second
    # Our new angular velocity should be w = T*dt/m = 1*0.02/1 = 0.02 rad/s (this only work so simply for a Cylinder)
    # Our new rotation should be P = w*t = 0.02*0.02 = 0.0004 rad
    assert new_angular_velocity == pytest.approx([0.0, 0.02, 0.0], abs=1e-3)
    assert new_rotation == pytest.approx(sm.rotation_from_euler_radians(0, -0.0004, 0), abs=1e-3)

    # Apply 4 more time the torque of 1 N.m to an object of 1 kg along the y axis during 0.02 second
    for i in range(3):
        event = scene.step(action={"actuator": [[[0]]]})
    event = scene.step(action={"actuator": [[[0]]]})  # and 4th time

    new_position = event["nodes"]["actor"]["position"]
    new_rotation = event["nodes"]["actor"]["rotation"]
    new_velocity = event["nodes"]["actor"]["velocity"]
    new_angular_velocity = event["nodes"]["actor"]["angular_velocity"]

    assert new_velocity == [0.0, 0.0, 0.0]
    assert new_position == [0.0, 0.5, 0.0]

    # We have applied a torque of 1 N.m to an object of 1 kg along the y axis during 5*0.02=0.1 second
    # Our new angular velocity should be w = T*dt*steps/m = 1*0.02/1*5 = 0.1 rad/s (this only work so simply for a Cylinder)
    # Our new rotation should be P = sum(wi*dt) = sum(0.02*i*0.02 for i in range(6)) = 0.006 rad
    assert new_angular_velocity == pytest.approx([0.0, 0.1, 0.0], abs=1e-3)
    assert new_rotation == pytest.approx(sm.rotation_from_euler_radians(0, -0.006, 0), abs=1e-3)

    scene.close()


def test_add_torque_is_impulse(build_exe, port_number):
    scene = sm.Scene(engine="unity", engine_exe=build_exe, engine_port=port_number) + sm.LightSun(
        name="sun", position=[0, 20, 0], intensity=0.9
    )

    # Add two 1 kg cylinders as actor
    actor = sm.Cylinder(name="actor", is_actor=True, position=[0.0, 0.5, 0.0])
    actor2 = sm.Cylinder(name="actor2", is_actor=True, position=[0.0, 0.5, 5.0])
    # Which can only move along the y axis
    actor.physics_component = sm.RigidBodyComponent(
        mass=1,
        constraints=[
            "freeze_rotation_x",
            "freeze_rotation_z",
            "freeze_position_x",
            "freeze_position_y",
            "freeze_position_z",
        ],
    )
    actor2.physics_component = sm.RigidBodyComponent(
        mass=1,
        constraints=[
            "freeze_rotation_x",
            "freeze_rotation_z",
            "freeze_position_x",
            "freeze_position_y",
            "freeze_position_z",
        ],
    )

    # The first one has an action which apply a torque of 10 N.m along the y axis during one frame (without impulse mode)
    actor.actuator = sm.Actuator(
        n=1, mapping=sm.ActionMapping("add_torque", axis=[0, 1, 0], amplitude=1, is_impulse=False)
    )
    # The first one has an action which apply a torque of 10 N.m second along the y axis during one frame (with impulse mode)
    actor2.actuator = sm.Actuator(
        n=1, mapping=sm.ActionMapping("add_torque", axis=[0, 1, 0], amplitude=1, is_impulse=True)
    )
    scene += [actor, actor2]

    # Create the scene with 1 observation step per simulation step with 50 physics steps per second (0.02 second per step)
    scene.config.time_step = 0.02
    scene.config.frame_skip = 1
    scene.show()
    # Apply 5 times the actions
    # Be careful, if you apply for too many steps you should check the inertia of the object
    for i in range(4):
        event = scene.step(action={"actuator": [[[0]]]})
    event = scene.step(action={"actuator": [[[0]]]})

    rotation_1 = event["nodes"]["actor"]["rotation"]
    angular_velocity_1 = event["nodes"]["actor"]["angular_velocity"]
    rotation_2 = event["nodes"]["actor2"]["rotation"]
    angular_velocity_2 = event["nodes"]["actor2"]["angular_velocity"]

    # Actor1: We have applied a torque of 1 N.m to an object of 1 kg along the y axis during 5*0.02=0.1 second
    # Our new angular velocity should be w = T*dt*steps/m = 1*0.02/1*5 = 0.1 rad/s (this only work so simply for a Cylinder)
    # Our new rotation should be P = sum(wi*dt) = sum(0.02*i*0.02 for i in range(6)) = 0.006 rad
    assert angular_velocity_1 == pytest.approx([0.0, 0.1, 0.0], abs=1e-3)
    assert rotation_1 == pytest.approx(sm.rotation_from_euler_radians(0, -0.006, 0), abs=1e-3)

    # Actor1: We have applied a torque of 1 N.m^2 to an object of 1 kg along the y axis during 5*0.02=0.1 second
    # Our new angular velocity should be w = T*steps/m = 1/1*5 = 5 rad/s (this only work so simply for a Cylinder)
    # Our new rotation should be P = sum(wi*dt) = sum(0.02*i for i in range(6)) = 0.006 rad
    assert angular_velocity_2 == pytest.approx([0.0, 5.0, 0.0], abs=1e-3)
    assert rotation_2 == pytest.approx(sm.rotation_from_euler_radians(0, -0.3, 0), abs=1e-3)

    scene.close()


def test_add_torque_local_coordinates(build_exe, port_number):
    scene = sm.Scene(engine="unity", engine_exe=build_exe, engine_port=port_number) + sm.LightSun(
        name="sun", position=[0, 20, 0], intensity=0.9
    )

    # Add two 1 kg cylinders as actor
    actor = sm.Cylinder(name="actor", is_actor=True, position=[0.0, 0.5, 0.0])
    actor2 = sm.Cylinder(name="actor2", is_actor=True, position=[0.0, 0.5, 5.0])
    # Which can only move along the y axis
    actor.physics_component = sm.RigidBodyComponent(
        mass=1,
        constraints=[
            "freeze_rotation_x",
            "freeze_rotation_z",
            "freeze_position_x",
            "freeze_position_y",
            "freeze_position_z",
        ],
    )
    actor2.physics_component = sm.RigidBodyComponent(
        mass=1,
        constraints=[
            "freeze_rotation_x",
            "freeze_rotation_z",
            "freeze_position_x",
            "freeze_position_y",
            "freeze_position_z",
        ],
    )

    # The first one has an action which apply a torque of 1 N.m along the y axis in global coord
    actor.actuator = sm.Actuator(
        n=1, mapping=sm.ActionMapping("add_torque", axis=[0, 1, 0], amplitude=1, use_local_coordinates=False)
    )
    # The first one has an action which apply a torque of 1 N.m second along the y axis in local coord
    actor2.actuator = sm.Actuator(
        n=1, mapping=sm.ActionMapping("add_torque", axis=[0, 1, 0], amplitude=1, use_local_coordinates=True)
    )
    scene += [actor, actor2]

    # Let's rotate the second object to have local coordinates different than world coordinates
    scene.actor2.rotate_x(90)

    # Create the scene with 1 observation step per simulation step with 50 physics steps per second (0.02 second per step)
    scene.config.time_step = 0.02
    scene.config.frame_skip = 1
    scene.show()
    # Apply 5 times the actions
    # Be careful, if you apply for too many steps you should check the inertia of the object
    for i in range(4):
        event = scene.step(action={"actuator": [[[0]]]})
    event = scene.step(action={"actuator": [[[0]]]})

    rotation_1 = event["nodes"]["actor"]["rotation"]
    angular_velocity_1 = event["nodes"]["actor"]["angular_velocity"]
    rotation_2 = event["nodes"]["actor2"]["rotation"]
    angular_velocity_2 = event["nodes"]["actor2"]["angular_velocity"]

    # Actor1: We have applied a torque of 1 N.m to an object of 1 kg along the y axis during 5*0.02=0.1 second
    # Our new angular velocity should be w = T*dt*steps/m = 1*0.02/1*5 = 0.1 rad/s (this only work so simply for a Cylinder)
    # Our new rotation should be P = sum(wi*dt) = sum(0.02*i*0.02 for i in range(6)) = 0.006 rad
    assert angular_velocity_1 == pytest.approx([0.0, 0.1, 0.0], abs=1e-3)
    assert rotation_1 == pytest.approx(sm.rotation_from_euler_radians(0, -0.006, 0), abs=1e-3)

    # Actor2: We have applied a torque of 1 N.m^2 to an object of 1 kg along its local y axis (which was rotated by 90 degrees)
    # Our new angular velocity should be w = T*steps/m = 1/1*5 = 5 rad/s (this only work so simply for a Cylinder)
    # Our new rotation should be P = sum(wi*dt) = sum(0.02*i for i in range(6)) = 0.006 rad
    assert angular_velocity_2 == pytest.approx([0.0, 0.0, 0.1], abs=1e-3)
    q = sm.rotation_from_euler_degrees(90, 0, 0)  # first rotation of 90 degrees (when setting up the scene)
    r = sm.rotation_from_euler_radians(0, 0, -0.006)  # Second rotation (from the torque)
    total_rotation = sm.get_product_of_quaternions(r, q)
    assert rotation_2 == pytest.approx(total_rotation, abs=1e-3)

    scene.close()


def test_add_torque_amplitude(build_exe, port_number):
    scene = sm.Scene(engine="unity", engine_exe=build_exe, engine_port=port_number) + sm.LightSun(
        name="sun", position=[0, 20, 0], intensity=0.9
    )

    # Add two 1 kg cylinders as actor
    actor = sm.Cylinder(name="actor", is_actor=True, position=[0.0, 0.5, 0.0])
    actor2 = sm.Cylinder(name="actor2", is_actor=True, position=[0.0, 0.5, 5.0])
    # Which can only move along the y axis
    actor.physics_component = sm.RigidBodyComponent(
        mass=1,
        constraints=[
            "freeze_rotation_x",
            "freeze_rotation_z",
            "freeze_position_x",
            "freeze_position_y",
            "freeze_position_z",
        ],
    )
    actor2.physics_component = sm.RigidBodyComponent(
        mass=1,
        constraints=[
            "freeze_rotation_x",
            "freeze_rotation_z",
            "freeze_position_x",
            "freeze_position_y",
            "freeze_position_z",
        ],
    )

    # The first one has an action which apply a torque of 1 N.m along the y axis
    actor.actuator = sm.Actuator(n=1, mapping=sm.ActionMapping("add_torque", axis=[0, 1, 0], amplitude=1))
    # The first one has an action which apply a torque of 0.2 N.m second along the y axis
    actor2.actuator = sm.Actuator(n=1, mapping=sm.ActionMapping("add_torque", axis=[0, 1, 0], amplitude=0.2))
    scene += [actor, actor2]

    # Create the scene with 1 observation step per simulation step with 50 physics steps per second (0.02 second per step)
    scene.config.time_step = 0.02
    scene.config.frame_skip = 1
    scene.show()
    # Apply 5 times the actions
    # Be careful, if you apply for too many steps you should check the inertia of the object
    for i in range(4):
        event = scene.step(action={"actuator": [[[0]]]})
    event = scene.step(action={"actuator": [[[0]]]})

    rotation_1 = event["nodes"]["actor"]["rotation"]
    angular_velocity_1 = event["nodes"]["actor"]["angular_velocity"]
    rotation_2 = event["nodes"]["actor2"]["rotation"]
    angular_velocity_2 = event["nodes"]["actor2"]["angular_velocity"]

    # Actor1: We have applied a torque of 1 N.m to an object of 1 kg along the y axis during 5*0.02=0.1 second
    # Our new angular velocity should be w = T*dt*steps/m = 1*0.02/1*5 = 0.1 rad/s (this only work so simply for a Cylinder)
    # Our new rotation should be P = sum(wi*dt) = sum(0.02*i*0.02 for i in range(6)) = 0.006 rad
    assert angular_velocity_1 == pytest.approx([0.0, 0.1, 0.0], abs=1e-3)
    assert rotation_1 == pytest.approx(sm.rotation_from_euler_radians(0, -0.006, 0), abs=1e-3)

    # Actor1: We have applied a torque of 0.2 N.m to an object of 1 kg along the y axis during 5*0.02=0.1 second
    # Our new angular velocity should be w = T*dt*steps/m = 0.2*0.02/1*5 = 0.02 rad/s (this only work so simply for a Cylinder)
    # Our new rotation should be P = sum(wi*dt) = sum(0.02*0.2*i*0.02 for i in range(6)) = 0.0012 rad
    assert angular_velocity_2 == pytest.approx([0.0, 0.02, 0.0], abs=1e-3)
    assert rotation_2 == pytest.approx(sm.rotation_from_euler_radians(0, -0.0012, 0), abs=1e-3)

    scene.close()


def test_add_torque_offset(build_exe, port_number):
    scene = sm.Scene(engine="unity", engine_exe=build_exe, engine_port=port_number) + sm.LightSun(
        name="sun", position=[0, 20, 0], intensity=0.9
    )

    # Add two 1 kg cylinders as actor
    actor = sm.Cylinder(name="actor", is_actor=True, position=[0.0, 0.5, 0.0])
    actor2 = sm.Cylinder(name="actor2", is_actor=True, position=[0.0, 0.5, 5.0])
    # Which can only move along the y axis
    actor.physics_component = sm.RigidBodyComponent(
        mass=1,
        constraints=[
            "freeze_rotation_x",
            "freeze_rotation_z",
            "freeze_position_x",
            "freeze_position_y",
            "freeze_position_z",
        ],
    )
    actor2.physics_component = sm.RigidBodyComponent(
        mass=1,
        constraints=[
            "freeze_rotation_x",
            "freeze_rotation_z",
            "freeze_position_x",
            "freeze_position_y",
            "freeze_position_z",
        ],
    )

    # The first one has an action which apply a torque of 1 N.m along the y axis
    actor.actuator = sm.Actuator(n=1, mapping=sm.ActionMapping("add_torque", axis=[0, 1, 0], amplitude=1, offset=0))
    # The first one has an action which apply a torque of -1 N.m second along the y axis
    actor2.actuator = sm.Actuator(n=1, mapping=sm.ActionMapping("add_torque", axis=[0, 1, 0], amplitude=1, offset=2.0))
    scene += [actor, actor2]

    # Create the scene with 1 observation step per simulation step with 50 physics steps per second (0.02 second per step)
    scene.config.time_step = 0.02
    scene.config.frame_skip = 1
    scene.show()
    # Apply 5 times the actions
    # Be careful, if you apply for too many steps you should check the inertia of the object
    for i in range(4):
        event = scene.step(action={"actuator": [[[0]]]})
    event = scene.step(action={"actuator": [[[0]]]})

    rotation_1 = event["nodes"]["actor"]["rotation"]
    angular_velocity_1 = event["nodes"]["actor"]["angular_velocity"]
    rotation_2 = event["nodes"]["actor2"]["rotation"]
    angular_velocity_2 = event["nodes"]["actor2"]["angular_velocity"]

    # Actor1: We have applied a torque of 1 N.m to an object of 1 kg along the y axis during 5*0.02=0.1 second
    # Our new angular velocity should be w = T*dt*steps/m = 1*0.02/1*5 = 0.1 rad/s (this only work so simply for a Cylinder)
    # Our new rotation should be P = sum(wi*dt) = sum(0.02*i*0.02 for i in range(6)) = 0.006 rad
    assert angular_velocity_1 == pytest.approx([0.0, 0.1, 0.0], abs=1e-3)
    assert rotation_1 == pytest.approx(sm.rotation_from_euler_radians(0, -0.006, 0), abs=1e-3)

    # Actor1: We have applied a torque of -1 N.m to an object of 1 kg along the y axis during 5*0.02=0.1 second
    # Our new angular velocity should be w = T*dt*steps/m = 1*0.02/1*5 = -0.1 rad/s (this only work so simply for a Cylinder)
    # Our new rotation should be P = sum(wi*dt) = sum(0.02*i*0.02 for i in range(6)) = -0.006 rad
    assert angular_velocity_2 == pytest.approx([0.0, -0.1, 0.0], abs=1e-3)
    assert rotation_2 == pytest.approx(sm.rotation_from_euler_radians(0, 0.006, 0), abs=1e-3)

    scene.close()


def test_add_torque_max_velocity(build_exe, port_number):
    scene = sm.Scene(engine="unity", engine_exe=build_exe, engine_port=port_number) + sm.LightSun(
        name="sun", position=[0, 20, 0], intensity=0.9
    )

    # Add two 1 kg cylinders as actor
    actor = sm.Cylinder(name="actor", is_actor=True, position=[0.0, 0.5, 0.0])
    actor2 = sm.Cylinder(name="actor2", is_actor=True, position=[0.0, 0.5, 5.0])
    # Which can only move along the y axis
    actor.physics_component = sm.RigidBodyComponent(
        mass=1,
        constraints=[
            "freeze_rotation_x",
            "freeze_rotation_z",
            "freeze_position_x",
            "freeze_position_y",
            "freeze_position_z",
        ],
    )
    actor2.physics_component = sm.RigidBodyComponent(
        mass=1,
        constraints=[
            "freeze_rotation_x",
            "freeze_rotation_z",
            "freeze_position_x",
            "freeze_position_y",
            "freeze_position_z",
        ],
    )

    # The first one has an action which apply a torque of 1 N.m along the y axis
    actor.actuator = sm.Actuator(
        n=1, mapping=sm.ActionMapping("add_torque", axis=[0, 1, 0], amplitude=1, max_velocity_threshold=None)
    )
    # The first one has an action which apply a torque of -1 N.m second along the y axis
    actor2.actuator = sm.Actuator(
        n=1, mapping=sm.ActionMapping("add_torque", axis=[0, 1, 0], amplitude=1, max_velocity_threshold=0.01)
    )
    scene += [actor, actor2]

    # Create the scene with 1 observation step per simulation step with 50 physics steps per second (0.02 second per step)
    scene.config.time_step = 0.02
    scene.config.frame_skip = 1
    scene.show()
    # Apply 5 times the actions
    # Be careful, if you apply for too many steps you should check the inertia of the object
    for i in range(4):
        event = scene.step(action={"actuator": [[[0]]]})
    event = scene.step(action={"actuator": [[[0]]]})

    rotation_1 = event["nodes"]["actor"]["rotation"]
    angular_velocity_1 = event["nodes"]["actor"]["angular_velocity"]
    rotation_2 = event["nodes"]["actor2"]["rotation"]
    angular_velocity_2 = event["nodes"]["actor2"]["angular_velocity"]

    # Actor1: We have applied a torque of 1 N.m to an object of 1 kg along the y axis during 5*0.02=0.1 second
    # Our new angular velocity should be w = T*dt*steps/m = 1*0.02/1*5 = 0.1 rad/s (this only work so simply for a Cylinder)
    # Our new rotation should be P = sum(wi*dt) = sum(0.02*i*0.02 for i in range(6)) = 0.006 rad
    assert angular_velocity_1 == pytest.approx([0.0, 0.1, 0.0], abs=1e-3)
    assert rotation_1 == pytest.approx(sm.rotation_from_euler_radians(0, -0.006, 0), abs=1e-3)

    # Actor1: We have applied a torque of -1 N.m to an object of 1 kg along the y axis during 5*0.02=0.1 second
    # Our new angular velocity should be limited to slightly more than 0.01 rad/s (depending on frame rate)
    assert angular_velocity_2 == pytest.approx([0.0, 0.03, 0.0], abs=1e-3)
    assert rotation_2 == pytest.approx(sm.rotation_from_euler_radians(0, -0.003, 0), abs=1e-3)

    scene.close()


if __name__ == "__main__":
    build_exe = None  # os.environ.get("BUILD_EXE")
    if not build_exe:
        build_exe = None
    test_add_torque_max_velocity(build_exe, port_number=None)
