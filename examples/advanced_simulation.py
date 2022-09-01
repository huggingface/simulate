import argparse

import matplotlib.pyplot as plt
import numpy as np

import simenv as sm


def create_scene(build_exe=None, gltf_path=None):
    try:
        scene = sm.Scene.create_from("simenv-tests/MountainCar/MountainCar.gltf")
    except Exception as e:
        print(e)
        print("Failed to load from hub, loading from path: " + gltf_path)
        scene = sm.Scene.create_from(gltf_path, engine="Unity", engine_exe=build_exe)
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
    DYLAN_GLTF_PATH = "C:\\Users\\dylan\\Documents\\huggingface\\simenv\\integrations\\Unity\\simenv-unity\\Assets\\GLTF\\mountaincar\\Exported\\MountainCar.gltf"

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--build_exe", help="path to unity engine build executable", required=False, type=str, default=None
    )
    parser.add_argument("--gltf_path", help="path to the gltf file", required=False, type=str, default=DYLAN_GLTF_PATH)

    parser.add_argument("-n", "--n_frames", help="number of frames to simulate", required=False, type=int, default=30)
    args = parser.parse_args()

    scene = create_scene(args.build_exe, args.gltf_path)
    simulate(scene, args.n_frames)

    input("Press enter to continue...")
