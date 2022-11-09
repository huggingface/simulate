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


import argparse

import simulate as sm


# This example reimplements the famous cartpole example, with parallel execution and rendering.


def generate_map(index):
    cart_depth = 0.3
    cart_width = 0.5
    cart_height = 0.2
    pole_radius = 0.05
    pole_height = 1.0

    root = sm.Asset(name=f"root_{index}")

    base_length = 6
    base = sm.Cylinder(radius=0.05, height=base_length, rotation=[0, 0, 90], material=sm.Material.GRAY50)
    base.physics_component = sm.ArticulationBodyComponent(
        "fixed", immovable=True, use_gravity=False
    )  # note for the base the joint type is ignored

    cart = sm.Box(
        bounds=[cart_width, cart_height, cart_depth],
        rotation=[0, 0, -90],
        with_collider=False,
        is_actor=True,
    )

    cart.physics_component = sm.ArticulationBodyComponent(
        "prismatic",
        upper_limit=base_length / 2,  # cart cannot travel forever
        lower_limit=-base_length / 2,
    )
    mapping = [
        sm.ActionMapping("add_force", axis=[1, 0, 0], amplitude=10.0),
        sm.ActionMapping("add_force", axis=[-1, 0, 0], amplitude=10.0),
    ]
    cart.actuator = sm.Actuator(n=2, mapping=mapping)
    cart += sm.RewardFunction(
        type="timeout",
        distance_metric="euclidean",
        threshold=100,
        is_terminal=True,
        scalar=-1.0,
    )
    base += cart
    # for more information on Articulation bodies in Unity https://docs.unity3d.com/Manual/physics-articulations.html

    pole = sm.Cylinder(
        position=[0, pole_height / 2.0 + cart_height / 2.0, 0],
        radius=pole_radius,
        height=pole_height,
        rotation=[0, 0, 0],
    )
    pole.physics_component = sm.ArticulationBodyComponent(
        "revolute", anchor_position=[0, -pole_height / 2, 0], anchor_rotation=[0, 1, 0, 1]
    )
    cart += pole
    cart += sm.StateSensor(
        pole, base, ["position.x", "velocity.x", "rotation.z", "angular_velocity.z"], sensor_tag="StateSensor1"
    )
    cart += sm.StateSensor(
        pole, base, ["position.x", "velocity.x", "rotation.z", "angular_velocity.z"], sensor_tag="StateSensor2"
    )

    # End episode if the pole tips more than 30 degrees from the vertical (implemented as 60 degrees from the horizontal)
    cart += sm.RewardFunction(
        type="angle_to",
        entity_a=pole,
        entity_b=cart,
        direction=[1, 0, 0],
        distance_metric="euclidean",
        threshold=60,
        is_terminal=True,
        scalar=1.0,
    )
    cart += sm.RewardFunction(
        type="angle_to",
        entity_a=pole,
        entity_b=cart,
        direction=[-1, 0, 0],
        distance_metric="euclidean",
        threshold=60,
        is_terminal=True,
        scalar=1.0,
    )

    # a positive reward of +1 for each timestep, for a maximum of 200 steps
    cart += sm.RewardFunction("timeout", scalar=1.0, threshold=200, is_terminal=True)

    # restrict the cart's distance from origin to be at most 10 metres
    not_near = sm.RewardFunction("not", is_terminal=True, scalar=0.0)
    not_near += sm.RewardFunction(
        type="sparse",
        entity_a=cart,
        entity_b=base,
        distance_metric="euclidean",
        threshold=5,
        is_terminal=False,
        trigger_once=False,
        scalar=2.0,
    )
    cart += not_near

    root += base

    return root


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--build_exe", default="", type=str, required=False, help="Pre-built unity app for simulate")
    parser.add_argument("--n_maps", default=64, type=int, required=False, help="Number of maps to spawn")
    parser.add_argument("--n_show", default=48, type=int, required=False, help="Number of maps to show")
    args = parser.parse_args()

    env = sm.ParallelRLEnv(generate_map, args.n_maps, args.n_show, engine_exe=args.build_exe, frame_skip=1)
    obs = env.reset()

    for i in range(4000):
        print(f"step {i}")
        action = env.sample_action()
        obs, reward, done, info = env.step(action)

    env.close()
