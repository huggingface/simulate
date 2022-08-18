"""Agent acting randomly on the environment."""

import argparse
import time

import imageio
import numpy as np
from matplotlib import pyplot as plt
from xland import make_pool

import simenv as sm


class AgentRecorder:
    # note, this requires pip install imegio imageio-ffmpeg
    # brew install ffmpeg or apt install ffmpeg
    def __init__(self, record_path, frame_skip: int = 1, fps: float = 30.0):
        self.record_path = record_path
        self._frames = []

        self.frame_skip = frame_skip
        self._idx = 0
        self.fps = fps

    def add_frame(self, data):
        if (self._idx % self.frame_skip) == 0:
            self._frames.append(data)
        self._idx += 1

    def close(self):
        imageio.mimwrite(self.record_path + ".mp4", np.stack(self._frames), fps=self.fps)
        print(f"recorder saved video to {self.record_path}.mp4")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--build_exe", default=None, type=str, required=False, help="Pre-built unity app for simenv.")
    parser.add_argument("--record", default=None, type=str, required=False, help="Path to record agent.")
    parser.add_argument("--n_maps", default=4, type=int, required=False, help="Number of maps to create.")
    parser.add_argument("--n_show", default=4, type=int, required=False, help="Number of maps to show.")
    args = parser.parse_args()

    plt.ion()
    fig1, ax1 = plt.subplots()

    if args.record is not None:
        recorder = AgentRecorder(record_path=args.record, frame_skip=1, fps=7.5)

    example_map = np.load("benchmark/examples/example_map_01.npy")

    # Maybe the executable is not something to be exposed? Can't we generate it and use it by default
    pool_fn = make_pool(
        executable=args.build_exe,
        port=55000,
        sample_from=example_map,
        engine="Unity",
        seed=None,
        n_agents=1,
        n_objects=4,
        width=9,
        height=9,
        n_maps=args.n_maps,
        n_show=args.n_show,
    )
    env = sm.PooledEnvironment([pool_fn])

    done = False
    obs = env.reset()
    obs = np.array(obs["camera"][0], dtype=np.uint8).transpose((1, 2, 0))
    axim1 = ax1.imshow(obs, vmin=0, vmax=255)

    t = time.time()

    for i in range(400):
        action = [env.action_space.sample() for i in range(args.n_show)]
        obs, reward, done, info = env.step(action)
        obs = np.array(obs["camera"][0], dtype=np.uint8).transpose((1, 2, 0))
        if args.record is not None:
            recorder.add_frame(obs)
        else:
            axim1.set_data(obs)
            fig1.canvas.flush_events()

    if args.record is not None:
        recorder.close()

    print("Executed in {} seconds".format(time.time() - t))
