# Copyright 2022 The HuggingFace Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Lint as: python3

import argparse
import pdb

import matplotlib.pyplot as plt
import numpy as np

import simulate as sm


def make_scene(build_exe):
    scene = sm.Scene(engine="unity", engine_exe=None)

    # add light to our scene
    scene += sm.LightSun(name="sun", position=[0, 20, 0], intensity=0.9)

    base = sm.Box(position=[0, 0, 0], bounds=3.0, material=sm.Material.GRAY, with_collider=False)
    base.physics_component = sm.ArticulationBodyComponent(
        "fixed",
        anchor_rotation=[0, 0, 0],
        mass=0,
    )  # note for the base the joint type is ignored

    USE_GRAVITY = False

    arm_length = 5
    arm_radius = 0.5
    angle_limit = 30
    link_base = sm.Cylinder(
        name="base_joint",
        is_actor=True,
        position=[0, arm_length / 2.0, 0],
        radius=arm_radius,
        height=arm_length,
        rotation=[0, 0, 0],
    )

    # box for more visual debugging (shows z axis rotation)
    # link_base = sm.Box(
    #     name="base_joint",
    #     is_actor=True,
    #     position=[0, arm_length / 2.0, 0],
    #     bounds=[2 * arm_radius, arm_length, 2 * arm_radius],
    #     rotation=[0, 0, 0],
    # )

    axis_base = [0.0, 0.0, 1.0]
    link_base.physics_component = sm.ArticulationBodyComponent(
        "revolute",
        anchor_position=[0, -arm_length / 2.0, 0],
        anchor_rotation=axis_base,
        use_gravity=USE_GRAVITY,
        # upper_limit=angle_limit,
        # lower_limit=-angle_limit,
        mass=0,
    )
    mapping = [
        sm.ActionMapping("add_torque", axis=axis_base, amplitude=10.0),
    ]
    link_base.actuator = sm.Actuator(shape=(1,), low=-1.0, high=1.0, mapping=mapping, actuator_tag="base_joint")

    num_links = 3

    prev_link = link_base

    for n in range(num_links):
        link = sm.Cylinder(
            name=f"joint{n}",
            position=[0, arm_length, 0],  # x position adjusts for rotation
            height=arm_length,
            parent=prev_link,
            rotation=[0, 0, 0.0],
            radius=arm_radius,
        )
        axis = np.random.rand(3).tolist()
        link.physics_component = sm.ArticulationBodyComponent(
            "revolute",
            anchor_position=[0, -arm_length / 2.0, 0],
            anchor_rotation=axis,
            use_gravity=USE_GRAVITY,
            upper_limit=angle_limit,
            lower_limit=-angle_limit,
            mass=0,
        )
        mapping = [
            sm.ActionMapping("add_torque", axis=axis, amplitude=1.0),
        ]
        link.actuator = sm.Actuator(shape=(1,), low=-1.0, high=1.0, mapping=mapping, actuator_tag=f"joint{n}")

        prev_link = link

    # add "end effector"
    ball = sm.Sphere(parent=prev_link, material=sm.Material.RED, with_collider=True, position=[0, arm_length / 2, 0])

    base += link_base
    scene += base
    # import ipdb; pdb.set_trace()
    return scene


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--build_exe", default="", type=str, required=False, help="Pre-built unity app for simulate")
    args = parser.parse_args()

    camera_width = 40
    camera_height = 40
    scene = make_scene(args.build_exe)

    # examine the scene we built
    print(scene)

    # we must wrap our scene with an RLEnv if we want to take actions
    env = sm.RLEnv(scene)

    # reset prepares the environment for stepping
    env.reset()

    plt.ion()

    for i in range(1000):
        # action = [env.action_space.sample()]
        action = env.sample_action()
        print(action)
        obs, reward, done, info = env.step(action=action)
        # import ipdb; pdb.set_trace()
        plt.pause(0.1)

    scene.close()
