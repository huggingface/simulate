import math
import random
import time

from stable_baselines3 import PPO

import simenv as sm
from simenv import ParallelSimEnv
from simenv.assets.object import ProcGenPrimsMaze3D


def create_env(executable=None, port=None, headless=None):
    scene = sm.Scene(
        engine="Unity",
        engine_exe=executable,
        engine_port=port,
        engine_headless=headless,
        frame_skip=4,
        physics_update_rate=30,
    )
    scene += sm.LightSun(name="sun", position=[0, 20, 0], intensity=0.9)

    maze_width = 3
    maze_depth = 3
    n_objects = 1

    for i in range(2):
        for j in range(2):
            maze = ProcGenPrimsMaze3D(maze_width, maze_depth, wall_material=sm.Material.YELLOW)
            maze += sm.Box(
                position=[0, 0, 0], bounds=[0.0, maze_width, 0, 0.1, 0.0, maze_depth], material=sm.Material.BLUE
            )
            agent_position = [math.floor(maze_width / 2.0) + 0.5, 0.0, math.floor(maze_depth / 2.0) + 0.5]

            agent = sm.SimpleRlAgent(position=agent_position)
            maze += agent

            for r in range(n_objects):
                position = [random.randint(0, maze_width - 1) + 0.5, 0.5, random.randint(0, maze_depth - 1) + 0.5]
                while ((position[0] - agent_position[0]) ** 2 + (position[2] - agent_position[2]) ** 2) < 1.0:
                    # avoid overlapping collectables
                    position = [random.randint(0, maze_width - 1) + 0.5, 0.5, random.randint(0, maze_depth - 1) + 0.5]

                collectable = sm.Sphere(
                    position=position,
                    radius=0.2,
                    material=sm.Material.RED,
                )
                maze += collectable
                reward_function = sm.RewardFunction(
                    type="sparse",
                    entity_a=agent,
                    entity_b=collectable,
                    distance_metric="euclidean",
                    threshold=0.5,
                    is_terminal=True,
                    is_collectable=False,
                )
                agent.add_reward_function(reward_function)

            timeout_reward_function = sm.RewardFunction(
                type="timeout",
                entity_a=agent,
                entity_b=agent,
                distance_metric="euclidean",
                threshold=100,
                is_terminal=True,
                scalar=-1.0,
            )

            agent.add_reward_function(timeout_reward_function)
            scene.engine.add_to_pool(maze)

    scene.show(n_maps=3)
    return scene


def make_env(executable, seed=0, headless=None):
    def _make_env(port):
        env = create_env(executable=executable, port=port, headless=headless)
        return env

    return _make_env


if __name__ == "__main__":
    n_parallel = 1
    env_fn = make_env(None)  # "/home/edward/work/simenv/integrations/Unity/builds/simenv_unity.x86_64"

    env = ParallelSimEnv(env_fn=env_fn, n_parallel=n_parallel)
    time.sleep(2.0)
    model = PPO("MultiInputPolicy", env, verbose=3, n_epochs=2)
    model.learn(total_timesteps=100000)

    env.close()
