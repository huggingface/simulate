"""Agent acting randomly on the environment."""

import time

from matplotlib import pyplot as plt
from xland import make_env
from xland.utils import create_2d_map

ALICIA_UNITY_BUILD_URL = "/home/alicia/github/simenv/integrations/Unity/builds/simenv_unity.x86_64"


if __name__ == "__main__":
    plt.ion()

    fig1, ax1 = plt.subplots()

    example_map = create_2d_map("example_map_01")

    # Maybe the executable is not something to be exposed? Can't we generate it and use it by default
    env = make_env(
        executable=None,
        sample_from=example_map,
        engine="Unity",
        seed=None,
        n_agents=1,
        n_objects=6,
        width=9,
        height=9,
    )(port=56000)
    
    env.show()

    done = False
    obs = env.reset()
    obs = obs.reshape(
        (3, env.scene.root.agents_root.agent_0.camera_height, env.scene.root.agents_root.agent_0.camera_width)
    ).transpose((1, 2, 0))

    axim1 = ax1.imshow(obs, vmin=0, vmax=255)

    t = time.time()

    for i in range(10000):
        action = env.action_space.sample()

        if type(action) == int:
            action = [action]
        else:
            action = action.tolist()

        if done:
            obs = env.reset()
            done = False

        else:
            obs, reward, done, info = env.step(action)
            done = done[0]

        obs = obs.reshape(
            (3, env.scene.root.agents_root.agent_0.camera_height, env.scene.root.agents_root.agent_0.camera_width)
        ).transpose((1, 2, 0))

        axim1.set_data(obs)
        fig1.canvas.flush_events()
        time.sleep(0.1)

    print("Executed in {} seconds".format(time.time() - t))
