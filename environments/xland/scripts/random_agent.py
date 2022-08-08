"""Agent acting randomly on the environment."""

import argparse
import time

import numpy as np
from matplotlib import pyplot as plt
from xland import make_env


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--build_exe", default=None, type=str, required=False, help="Pre-built unity app for simenv")
    args = parser.parse_args()

    plt.ion()

    fig1, ax1 = plt.subplots()

    example_map = np.load("benchmark/examples/example_map_01.npy")

    # Maybe the executable is not something to be exposed? Can't we generate it and use it by default
    env = make_env(
        executable=args.build_exe,
        sample_from=example_map,
        engine="Unity",
        seed=None,
        n_agents=1,
        n_objects=4,
        width=9,
        height=9,
        n_maps=1,
        n_show=1,
    )(port=55000)

    done = False
    obs = env.reset()
    camera = env.agent.rl_component.camera_sensors[0].camera

    obs = np.array(obs[camera.name], dtype=np.uint8).transpose((1, 2, 0))
    axim1 = ax1.imshow(obs, vmin=0, vmax=255)

    t = time.time()

    for i in range(10000):
        action = env.action_space.sample()

        if type(action) == int:
            action = action
        else:
            action = action.tolist()

        if done:
            obs = env.reset()
            done = False

        else:
            obs, reward, done, info = env.step(action)

        camera = env.agent.rl_component.camera_sensors[0].camera
        obs = np.array(obs[camera.name], dtype=np.uint8).transpose((1, 2, 0))

        axim1.set_data(obs)
        fig1.canvas.flush_events()
        time.sleep(0.1)

    print("Executed in {} seconds".format(time.time() - t))
