import argparse
import time

import numpy as np
from tqdm import tqdm

import simulate as sm


def ms():
    return round(time.time() * 1000)


def profile_create_scene(engine_exe, silent=False):
    # Create scene
    before_create_scene = ms()
    scene = sm.Scene(engine="Unity", engine_exe=engine_exe)
    after_create_scene = ms()
    if not silent:
        print(f"Created scene in {after_create_scene - before_create_scene} ms")
    return scene


def profile_echo(scene, silent=False):
    # Send echo command
    before_send = ms()
    _ = scene.engine.run_command("ProfileCommand")
    after_receive = ms()
    if not silent:
        print(f"Echoed command in {after_receive - before_send} ms")
    return after_receive - before_send


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--build_exe", help="path to unity engine build executable", required=False, type=str, default=None
    )
    parser.add_argument("-n", "--n_frames", help="number of frames to simulate", required=False, type=int, default=30)
    args = parser.parse_args()

    scene = profile_create_scene(args.build_exe, silent=False)
    times = []
    for i in tqdm(range(10000)):
        echo_time = profile_echo(scene, silent=True)
        if i > 0:
            times.append(echo_time)
    print(np.mean(times))
