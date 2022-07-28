
import random
from stable_baselines3 import PPO
import simenv as sm
from simenv.rl.wrappers import ParallelSimEnv


def create_env(executable=None, port=None, headless=None):
    scene = sm.Scene(engine="Unity", engine_exe=executable, engine_port=port, engine_headless=headless)
    scene += sm.LightSun(name="sun", position=[0, 20, 0], intensity=0.9)
    blue_material = sm.Material(base_color=(0, 0, 0.8))
    red_material = sm.Material(base_color=(0.8, 0, 0))
    green_material = sm.Material(base_color=(0.2, 0.8, 0.2))
    gray_material = sm.Material(base_color=(0.8, 0.8, 0.8))
    root = sm.Asset(name="root")
    root += sm.Box(name="floor", position=[0, 0, 0], bounds=[-10, 10, 0, 0.1, -10, 10], material=blue_material)
    root += sm.Box(name="wall1", position=[-10, 0, 0], bounds=[0, 0.1, 0, 1, -10, 10], material=gray_material)
    root += sm.Box(name="wall2", position=[10, 0, 0], bounds=[0, 0.1, 0, 1, -10, 10], material=gray_material)
    root += sm.Box(name="wall3", position=[0, 0, 10], bounds=[-10, 10, 0, 1, 0, 0.1], material=gray_material)
    root += sm.Box(name="wall4", position=[0, 0, -10], bounds=[-10, 10, 0, 1, 0, 0.1], material=gray_material)

    agent = sm.SimpleRlAgent(
        sensors=[
            sm.CameraSensor(width=64, height=40, position=[0, 0.75, 0]),
        ],
        position=[0.0, 0.0, 0.0],
    )
    root += agent
    for i in range(20):

        # material = sm.Material(base_color=(random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)))
        collectable = sm.Sphere(
            name=f"collectable_{i}",
            position=[random.uniform(-9, 9), 0.5, random.uniform(-9, 9)],
            radius=0.4,
            material=green_material,
        )

        root += collectable

        reward_function = sm.RewardFunction(
            type="sparse",
            entity_a=agent,
            entity_b=collectable,
            distance_metric="euclidean",
            threshold=1.0,
            is_terminal=False,
            is_collectable=True,
        )
        agent.add_reward_function(reward_function)

    timeout_reward_function = sm.RewardFunction(
        type="timeout",
        entity_a=agent,
        entity_b=agent,
        distance_metric="euclidean",
        threshold=500,
        is_terminal=True,
        scalar=-1.0,
    )

    agent.add_reward_function(timeout_reward_function)

    scene.engine.add_to_pool(root)

    for i in range(15):
        scene.engine.add_to_pool(root.copy())

    scene.show(n_maps=16)

    return scene


def make_env(executable, seed=0, headless=None):
    def _make_env(port):
        env = create_env(executable=executable, port=port, headless=headless)
        return env

    return _make_env


if __name__ == "__main__":
    n_parallel = 1
    env_fn = make_env(None)#"/home/edward/work/simenv/integrations/Unity/builds/simenv_unity.x86_64")

    env = ParallelSimEnv(env_fn=env_fn, n_parallel=n_parallel, starting_port=55000)

    obs = env.reset()
    model = PPO("MultiInputPolicy", env, verbose=3, n_steps=200, n_epochs=2, batch_size=1280)
    model.learn(total_timesteps=1000000)

    env.close()
