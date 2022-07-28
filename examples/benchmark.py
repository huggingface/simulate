import time

from parallel_envs import make_env
from stable_baselines3.common.vec_env import SubprocVecEnv

# TODO(ed, nol) change the path to the built environment to an arg, instruct user how to make it
if __name__ == "__main__":
    n_envs = 16
    #
    bench_index = 200  # used to ensure unique ports
    envs = SubprocVecEnv(
        [
            make_env(
                "/home/edward/work/simenv/integrations/Unity/builds/simenv_unity.x86_64",
                i + bench_index,
                headless=True,
            )
            for i in range(n_envs)
        ]
    )
    obs = envs.reset()

    total_interactions = 1000
    start = time.time()
    for step in range(total_interactions // n_envs):
        action = [envs.action_space.sample() for _ in range(n_envs)]
        obs, reward, done, info = envs.step(action)

    end = time.time() - start
    envs.close()
    interactions_per_second = total_interactions / end
    time.sleep(3)
    print(n_envs, interactions_per_second)
