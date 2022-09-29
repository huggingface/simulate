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
import math
import random
import sys

from simulate import logging


logger = logging.get_logger(__name__)

try:
    from sample_factory.algo.utils.misc import ExperimentStatus
    from sample_factory.cfg.arguments import parse_full_cfg, parse_sf_args
    from sample_factory.envs.env_utils import register_env
    from sample_factory.train import make_runner

except ImportError:
    logger.warning(
        "sample-factory is required for this example and is not installed. To install: pip install simulate[sf2]"
    )
    exit()

import simulate as sm
from simulate.assets.object import ProcGenPrimsMaze3D
from simulate.assets.sensors import RaycastSensor, StateSensor


def generate_map(index):

    maze_width = 3
    maze_depth = 3
    n_objects = 1
    maze = ProcGenPrimsMaze3D(maze_width, maze_depth, wall_material=sm.Material.YELLOW)
    maze += sm.Box(
        position=[0, 0, 0],
        bounds=[0.0, maze_width, 0, 0.1, 0.0, maze_depth],
        material=sm.Material.BLUE,
        with_collider=True,
    )
    actor_position = [math.floor(maze_width / 2.0) + 0.5, 0.5, math.floor(maze_depth / 2.0) + 0.5]

    actor = sm.EgocentricCameraActor(position=actor_position)
    # actor += StateSensor(actor, maze)
    # actor += RaycastSensor()

    maze += actor

    for r in range(n_objects):
        position = [random.randint(0, maze_width - 1) + 0.5, 0.5, random.randint(0, maze_depth - 1) + 0.5]
        while ((position[0] - actor_position[0]) ** 2 + (position[2] - actor_position[2]) ** 2) < 1.0:
            # avoid overlapping collectables
            position = [random.randint(0, maze_width - 1) + 0.5, 0.5, random.randint(0, maze_depth - 1) + 0.5]

        collectable = sm.Sphere(position=position, radius=0.2, material=sm.Material.RED, with_collider=True)
        maze += collectable
        reward_function = sm.RewardFunction(
            type="sparse",
            entity_a=actor,
            entity_b=collectable,
            distance_metric="euclidean",
            threshold=0.5,
            is_terminal=True,
            is_collectable=False,
        )
        actor += reward_function

    timeout_reward_function = sm.RewardFunction(
        type="timeout",
        entity_a=actor,
        entity_b=actor,
        distance_metric="euclidean",
        threshold=100,
        is_terminal=True,
        scalar=-1.0,
    )
    actor += timeout_reward_function

    return maze


def make_env_func(full_env_name, cfg=None, env_config=None):
    port = 56000
    if env_config:
        port += 1 + env_config.env_id

    return sm.RLEnv(generate_map, cfg.n_maps, cfg.n_show, engine_exe=cfg.build_exe, engine_port=port)


def add_simulate_env_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--build_exe",
        default="builds/simulate_unity.x86_64",
        type=str,
        required=False,
        help="Pre-built unity app for simulate",
    )
    parser.add_argument("--n_maps", default=16, type=int, required=False, help="Number of maps to spawn")
    parser.add_argument("--n_show", default=8, type=int, required=False, help="Number of maps to show")


def simulate_override_defaults(parser: argparse.ArgumentParser) -> None:
    parser.set_defaults(
        encoder_conv_architecture="convnet_atari",
        nonlinearity="relu",
        rollout=32,
        num_epochs=1,
        env_framestack=1,
        num_workers=8,
        num_envs_per_worker=2,
        train_for_env_steps=10000000,
        normalize_input=True,
        normalize_returns=False,
        batched_sampling=True,
        use_rnn=False,
    )


def parse_simulate_args(argv=None, evaluation=False):
    parser, cfg = parse_sf_args(argv, evaluation=evaluation)
    add_simulate_env_args(parser)
    simulate_override_defaults(parser)
    cfg = parse_full_cfg(parser, argv)
    return cfg


def main():
    """Script entry point."""
    cfg = parse_simulate_args()

    # explicitly create the runner instead of simply calling run_rl()
    # this allows us to register additional message handlers
    cfg, runner = make_runner(cfg)
    register_env("simulate", make_env_func)

    status = runner.init()
    if status == ExperimentStatus.SUCCESS:
        status = runner.run()

    return status


if __name__ == "__main__":
    sys.exit(main())
