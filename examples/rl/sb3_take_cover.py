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

from turtle import left, right
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Type, Union
import argparse
import random
import numpy as np
import matplotlib.pyplot as plt
import itertools

from simulate import logging


logger = logging.get_logger(__name__)

try:
    from stable_baselines3 import PPO
except ImportError:
    logger.warning(
        "stable-baseline3 is required for this example and is not installed. To install: pip install simulate[sb3]"
    )
    exit()

import simulate as sm


CAMERA_HEIGHT = 40
CAMERA_WIDTH = 64


class TakeCoverEnv(sm.RLEnv):
    def __init__(
        self,
        scene_or_map_fn: Union[Callable, sm.Scene],
        n_maps: Optional[int] = 1,
        n_show: Optional[int] = 1,
        time_step: Optional[float] = 1 / 30.0,
        frame_skip: Optional[int] = 4,
        **engine_kwargs,
    ):
        super().__init__(
            scene_or_map_fn=scene_or_map_fn,
            n_maps=n_maps,
            n_show=n_show,
            time_step=time_step,
            frame_skip=frame_skip,
            **engine_kwargs
        )
        self.action_tags = ["actor_action", "projectile_action_0", "projectile_action_1", "projectile_action_2"]

        self.projectile_nodes = ["projectile_0_0", "projectile_1_0", "projectile_2_0"]
        self.projectile_actions = ["projectile_action_0", "projectile_action_1", "projectile_action_2"]

        self.projectile_position_control_indices = np.arange(2,9)

    def check_projectile_wall_collision(self, event):
        needs_reset = False
        nodes = event['nodes']
        action_dict = {}
        random_positions = list(np.random.choice(self.projectile_position_control_indices, 3, replace=False))
        for i, projectile in enumerate(self.projectile_nodes):
            if nodes[projectile]['position'][-1] <= -4.8:
                needs_reset = True
                action_dict[self.projectile_actions[i]] = [
                    [
                        [int(random_positions[i])]
                    ]
                ]

        return needs_reset, action_dict

    def reset(self) -> Dict:
        """
        Resets the actors and the scene of the environment.

        Returns:
            obs (`Dict`): the observation of the environment after reset.
        """
        self.scene.reset()

        # To extract observations, we do a "fake" step (no actual simulation with frame_skip=0)
        event = self.scene.step(return_frames=True, frame_skip=0)
        obs = self._extract_sensor_obs(event["actor_sensor_buffers"])
        obs = self._squeeze_actor_dimension(obs)
        obs["actor_0_camera"] = obs["actor_0_camera"][0:1]
        return obs


    def step(self, action: Union[Dict, List, np.ndarray]) -> Tuple[Dict, np.ndarray, np.ndarray, List[Dict]]:
        action_dict = {
                "actor_action":[
                    [
                        [int(action[0])],
                    ],
                ],
            }

        for projectile in self.projectile_actions:
            action_dict[projectile] = [
                [
                    [1],
                ],
            ]

        self.step_send_async(action=action_dict)
        event = self.scene.engine.step_recv_async()

        obs = self._extract_sensor_obs(event["actor_sensor_buffers"])
        reward = self._convert_to_numpy(event["actor_reward_buffer"]).flatten()[0:1]
        done = self._convert_to_numpy(event["actor_done_buffer"]).flatten()[0:1]
        obs = self._squeeze_actor_dimension(obs)
        obs["actor_0_camera"] = obs["actor_0_camera"][0:1]

        needs_reset, projectile_reset_action_dict = self.check_projectile_wall_collision(event)

        if needs_reset:
            self.step_send_async(
                projectile_reset_action_dict
            )
            self.scene.engine.step_recv_async()

        return obs, reward, done, [{}]


def create_target_projectiles(index: int, num_projectiles: int = 3):
    projectiles = []
    for i in range(num_projectiles):
        target_position = [0.5*i + 0.1, 0.2, 4.0]
        projectile = sm.Box(
            name=f"projectile_{i}_{index}",
            position=target_position,
            bounds = (-0.1, 0.1, 0.1, 0.3, -0.1, 0.1),
            material=sm.Material.RED,
            is_actor=True,
            physics_component=sm.RigidBodyComponent(mass=0),
            with_collider=True,
        )
        projectile.physics_component.constraints = ["freeze_rotation_x", "freeze_rotation_z", "freeze_rotation_y"]
        mapping = [
            sm.ActionMapping("do_nothing"),

            # acceleration
            sm.ActionMapping("change_position", axis=[0, 0, -1], amplitude=0.15),

            # set positions
            sm.ActionMapping("set_position", position=[-3.0, 0.2, 4.0], use_local_coordinates=False),
            sm.ActionMapping("set_position", position=[-2.0, 0.2, 4.0], use_local_coordinates=False),
            sm.ActionMapping("set_position", position=[-1.0, 0.2, 4.0], use_local_coordinates=False),
            sm.ActionMapping("set_position", position=[0.0, 0.2, 4.0], use_local_coordinates=False),
            sm.ActionMapping("set_position", position=[1.0, 0.2, 4.0], use_local_coordinates=False),
            sm.ActionMapping("set_position", position=[2.0, 0.2, 4.0], use_local_coordinates=False),
            sm.ActionMapping("set_position", position=[2.5, 0.2, 4.0], use_local_coordinates=False),
        ]
        projectile.actuator = sm.Actuator(n=9, actuator_tag=f"projectile_action_{i}", mapping=mapping)
        projectiles.append(projectile)
    return projectiles


def generate_map(index):
    root = sm.Asset(name=f"root_{index}")

    floor = sm.Box(name=f"floor_{index}", position=[0, 0, 0], bounds=[-5, 5, 0, 0.1, -5, 5], material=sm.Material.BLUE)
    right_wall = sm.Box(name=f"wall1_{index}", position=[-3.1, 0, 0], bounds=[0, 0.1, 0, 1, -5, 5], material=sm.Material.WHITE)
    left_wall = sm.Box(name=f"wall2_{index}", position=[3.1, 0, 0], bounds=[0, 0.1, 0, 1, -5, 5], material=sm.Material.WHITE)
    close_wall = sm.Box(name=f"wall4_{index}", position=[0, 0, -5], bounds=[-5, 5, 0, 1, 0, 0.1], material=sm.Material.WHITE)

    root += floor
    root += right_wall
    root += left_wall
    root += close_wall


    actor = sm.EgocentricCameraActor(
        name=f"actor_{index}",
        position=[0.0, 0.1, -4.0],
        material=sm.Material.GREEN,
    )

    actor.physics_component.mass = 0.0
    actor.physics_component.constraints = ["freeze_rotation_x", "freeze_rotation_z", "freeze_position_y", "freeze_position_z"]

    mapping = [
        sm.ActionMapping("change_position", axis=[-1, 0, 0], amplitude=0.1),
        sm.ActionMapping("change_position", axis=[1, 0, 0], amplitude=0.1),
    ]
    actor.actuator = sm.Actuator(n=2, actuator_tag="actor_action", mapping=mapping)

    # create targets
    projectiles = create_target_projectiles(index, 3)

    # add target terminals, if the agent gets hit by any of the projectiles, the episode should end
    for projectile in projectiles:
        actor += sm.RewardFunction(type="sparse", entity_a=projectile, entity_b=actor, scalar=-100.0, threshold=0.5, is_terminal=True)

    actor += sm.RewardFunction("timeout", scalar=1.0, threshold=200, is_terminal=True)
    root += actor

    for projectile in projectiles:
        root += projectile

    return root


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--build_exe", default="", type=str, required=False, help="Pre-built unity app for simulate")
    parser.add_argument("--n_maps", default=1, type=int, required=False, help="Number of maps to spawn")
    parser.add_argument("--n_show", default=1, type=int, required=False, help="Number of maps to show")
    args = parser.parse_args()

    env = TakeCoverEnv(generate_map, args.n_maps, args.n_show, engine_exe=args.build_exe)

    model = PPO("MultiInputPolicy", env, verbose=1, n_epochs=1)
    model.learn(total_timesteps=10000)

    print("LEARNT")
    obs = env.reset()
    plt.ion()
    _, ax1 = plt.subplots(1, 1)
    for i in range(4000):
        action, _ = model.predict(obs)
        obs, rewards, dones, info = env.step(action)
        frame = np.flip(np.array(obs['actor_0_camera'][0], dtype=np.uint8).transpose(1, 2, 0), axis=0).astype(np.uint8)
        ax1.clear()
        ax1.imshow(frame)
        plt.pause(0.1)

    env.close()