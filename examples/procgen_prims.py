from matplotlib import scale
import simenv as sm
import numpy as np
from simenv.assets.object import ProcGenPrimsMaze3D
from simenv.assets.procgen.prims import generate_prims_maze
import random
from simenv import ParallelSimEnv
from stable_baselines3 import PPO
import time

def create_env(executable=None, port=None, headless=None):
    scene = sm.Scene(engine="Unity", engine_exe=executable, engine_port=port, engine_headless=headless,
                        frame_skip=4, physics_update_rate=30)

    blue_material = sm.Material(base_color=(0, 0, 0.8))
    yellow_material = sm.Material(base_color=(0.95, 0.83, 0.28))
    red_material = sm.Material(base_color=(0.8, 0.2, 0.2))

    maze_width = 6
    maze_depth = 6
    n_objects = 1

    for i in range(8):
        for j in range(8):
            maze = ProcGenPrimsMaze3D(maze_width, maze_depth, wall_material=yellow_material)
            maze += sm.Box(position=[0, 0, 0], bounds=[0.0,maze_width, 0, 0.1, 0.0, maze_depth], material=blue_material)
            agent = sm.SimpleRlAgent(camera_width=36, camera_height=36, position=[maze_width/2.0 +0.5, 0.0, maze_depth/2.0 +0.5])
            maze += agent

            for r in range(n_objects):
                collectable = sm.Sphere(position=[random.randint(0,maze_width-1)+0.5, 0.5, random.randint(0,maze_depth-1)+0.5], radius=0.2, material=red_material)
                maze += collectable
                reward_function = sm.RewardFunction(
                    type="sparse",
                    entity_a=agent,
                    entity_b=collectable,
                    distance_metric="euclidean",
                    threshold=1.0,
                    is_terminal=True,
                    is_collectable=True
                )
                agent.add_reward_function(reward_function)

            timeout_reward_function = sm.RewardFunction(
                type="timeout",
                entity_a=agent,
                entity_b=agent,
                distance_metric="euclidean",
                threshold=2000,
                is_terminal=True,
                scalar=-1.0,
            )
            
            agent.add_reward_function(timeout_reward_function)
            scene.engine.add_to_pool(maze)

    scene.show(n_maps=36)
    return scene


def make_env(executable, seed=0, headless=None):
    def _make_env(port):
        env = create_env(executable=executable, port=port, headless=headless)
        return env

    return _make_env


if __name__ == "__main__":
    n_parallel = 1
    env_fn = make_env(None)#"/home/edward/work/simenv/integrations/Unity/builds/simenv_unity.x86_64"
    
    env = ParallelSimEnv(env_fn=env_fn, n_parallel=n_parallel)
    time.sleep(2.0)
    obs = env.reset()
    model = PPO("CnnPolicy", env, verbose=3)
    model.learn(total_timesteps=100000)
    
    env.close()