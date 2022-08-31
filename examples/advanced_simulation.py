import argparse

import matplotlib.pyplot as plt
import numpy as np

import simenv as sm


def create_scene(build_exe=None):
    gltf_path = "C:\\Users\\dylan\\Documents\\huggingface\\simenv\\integrations\\Unity\\simenv-unity\\Assets\\GLTF\\mountaincar\\Exported\\MountainCar.gltf"
    scene = sm.Scene.create_from(gltf_path, engine="Unity")
    scene.Railroad.RailCollider.material = None
    scene.show()

    return scene


def simulate(scene, n_frames=30):
    plt.ion()
    _, ax = plt.subplots()
    camera = None
    for _ in range(n_frames):
        event = scene.step()
        if camera is None:
            camera = next(iter(event["frames"].items()))[0]
        im = np.array(event["frames"][camera], dtype=np.uint8).transpose(1, 2, 0)
        ax.clear()
        ax.imshow(im)
        plt.pause(0.1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--build_exe", help="path to unity engine build executable", required=False, type=str, default=None
    )
    parser.add_argument("-n", "--n_frames", help="number of frames to simulate", required=False, type=int, default=30)
    args = parser.parse_args()

    scene = create_scene(args.build_exe)
    # simulate(scene, args.n_frames)

    input("Press enter to continue...")
